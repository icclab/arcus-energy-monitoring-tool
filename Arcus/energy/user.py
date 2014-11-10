"""
 Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
 All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
"""

__author__ = 'gaea'

from ceilometerclient import client as clients
from datetime import *
import time
from calendar import monthrange
import keystoneclient.v2_0.client as ksclient
import ConfigParser
from arcus_database import VmPower


class User:
    month_list = ['January', 'February', 'March', 'April',
                  'May', 'June', 'July', 'August', 'September',
                  'October', 'November', 'December']
    config = ConfigParser.RawConfigParser()
    config.read('/home/icclab/Ember-Django/Arcus/energy/arcus.conf')

    _user = config.get('keystone_credentials', 'user')
    _token = config.get('keystone_credentials', 'token')
    _passw = config.get('keystone_credentials', 'password')
    _auth_url = config.get('keystone_credentials', 'auth_url')
    _admin_url = config.get('keystone_credentials', 'admin_url')
    _tenant = config.get('keystone_credentials', 'tenant')
    _ceilometer_auth_url = config.get('ceilometer', 'auth_url')

    def __init__(self, token):
        self.client = self._credentials(token)
        self.admin_client = self._admin_credentials()

        date_now = datetime.now()
        self.year = date_now.year
        self.month = date_now.month
        self.month = date_now.month
        self.end_day = monthrange(self.year, self.month)[1]
        self.power_meters, self.projects, self.energy = list(), list(), list()

    def _credentials(self, token):
        """

        :rtype : ceilometer_client
        :type self: User
        """
        self.tenant_list = list()
        keystone = dict(token=token, auth_url=self._auth_url)
        kclient = ksclient.Client(**keystone)

        tenants = kclient.tenants.list()
        for tenant in tenants:
            self.tenant_list.append(tenant.id)

        return clients.Client(2, endpoint=self._ceilometer_auth_url, token=lambda: token)

    def _admin_credentials(self):
        """

        :rtype : ceilometer_client
        :type self: User
        """
        keystone = dict(os_username=self._user, os_password=self._passw, os_auth_url=self._auth_url,
                        os_tenant_name=self._tenant)
        return clients.get_client(2, **keystone)


class UserManager(User):

    @staticmethod
    def tenants_name():
        keystone = ksclient.Client(token=User._token,
                                   endpoint=User._admin_url)
        return keystone.tenants.list()

    @property
    def energy_vm(self):
        """

        :type self: User
        """
        energy_vm = list()
        for project in self.tenant_list:
            date_query = '{0}-{1}'.format(str(self.year), str(self.month_list[self.month-1]))
            data = VmPower.select().where((VmPower.project == project) & (VmPower.date == date_query))
            if data:
                energy_vm.append(map(lambda m: m, data))
        return energy_vm

    def overview(self):
        """

        :rtype : dictionary
        :type self: UserManager
        """
        energy_vm = self.energy_vm
        projects = self.tenants_name()

        instances_active, mean_rate_vm, mean_rate, sum_total = 0, 0, 0, 0
        #sum_total = sum(map(lambda m: int(sum(map(lambda y: y.joulesmean, m))), zip(*energy_vm)))/1000
        vm_name_list, vm_project, vm_project_support = list(), list(), list()
        for tenant in energy_vm:
            for vms in tenant:
                sum_total += vms.joulesmean
                if vms.name not in vm_name_list:
                    vm_name_list.append(vms.name)
                    instances_active += 1
                if vms.project not in vm_project_support:
                    vm_project_support.append(vms.project)
                    for p in projects:
                            if p.id == vms.project:
                                vm_project.append(p.name)

        datachart = data_chart(energy_vm)

        ch_list = overview_chart(datachart)

        for dchart in datachart:
            mean_rate_vm = (sum(map(lambda m: float(m), dchart['value']))/len(dchart['value']))/instances_active
            mean_rate = (sum(map(lambda m: float(m), dchart['value']))/len(dchart['value']))
        chart = list()
        x = 0
        print vm_project
        for t in ch_list:
            chart.append({'name': vm_project[x], 'data': t})
            x += 1
        sum_total /= 1000
        return dict(id=1, total=sum_total, mean_rate="%.2f" % mean_rate, month=self.month_list[self.month-1],
                    inst_active=instances_active, mean_vm="%.2f" % mean_rate_vm, chart=chart)

    def consumption_vm(self):
        """

        :rtype : dictionary
        :type self: UserManager
        """

        energy_vm = self.energy_vm
        instances_active, higher_vm, total = 0, 0, 0
        vm_name = ''
        instance_chart_list = list()

        vm_name_list = list()
        vm_list = list()
        for tenant in energy_vm:
            for vms in tenant:
                total += vms.joulesmean
                if vms.name not in vm_name_list:
                    vm_name_list.append(vms.name)
                    vm_list.append(vms)
                    instances_active += 1
                else:
                    for vm in vm_list:
                        if vm.name == vms.name:
                            vm.wattsmean += vms.wattsmean
                            vm.joulesmean += vms.joulesmean

        for vms in vm_list:
            instance_chart_list.append({'name': vms.name,
                                        'data': [vms.joulesmean/1000]})
            if higher_vm < vms.joulesmean/1000:
                higher_vm = vms.joulesmean/1000
                vm_name = vms.name
        total /= 1000
        return dict(id=1, total=total, inst_active=instances_active, vm_name=vm_name, vm_rate=higher_vm,
                    month=self.month_list[self.month-1], chart=instance_chart_list)

    def consumption_project(self):
        """

        :rtype : dictionary
        :type self: UserManager
        """
        energy_vm = self.energy_vm
        datachart = list()
        high_energy_project, total, highest_project = 0, 0, 0
        projects = self.tenants_name()
        vm_project = ''

        for tenant in energy_vm:
            total_project = 0
            for vms in tenant:
                total_project += vms.joulesmean
                vm_project = vms.project
                total += vms.joulesmean
            total_project /= 1000
            for p in projects:
                if p.id == vm_project:
                    project_name = p.name
            if total_project > high_energy_project:
                high_energy_project = total_project
                highest_project = project_name
            datachart.append(dict(name=project_name, data=[total_project]))

        total /= 1000
        return dict(id=1, total=total, projs_active=len(energy_vm), high_proj=high_energy_project,
                    month=self.month_list[self.month-1], name=highest_project, chart=datachart)

    def variation(self, start):
        """

        :rtype : dictionary
        :type self: UserManager
        """
        start = int(start)
        energy_list = list()
        for month in range(start, self.month+1):
            month_energy_list = self.energy_per_month(month)
            total = 0
            for tenant in month_energy_list:
                total_project = 0
                for vms in tenant:
                    total_project += vms.joulesmean
                    total += vms.joulesmean
            total /= 1000
            energy_list.append({'name': self.month_list[month-1],
                                'data': [total]})
        highest_consumption = 0
        highest_month = ''
        total2 = 0
        for month in energy_list:
            total2 += month['data'][0]
            if month['data'][0] > highest_consumption:
                highest_consumption = month['data'][0]
                highest_month = month['name']
        return dict(id=1, total=total2, highest_month=highest_month,
                    highest_energy=highest_consumption, month=self.month_list[self.month-1],
                    chart=energy_list)

    def energy_per_month(self, start):
        """

        :type self: User
        """
        energy_vm = list()
        for project in self.tenant_list:
            date_query = '{0}-{1}'.format(str(self.year), str(self.month_list[start-1]))
            data = VmPower.select().where((VmPower.project == project) & (VmPower.date == date_query))

            if data:
                energy_vm.append(map(lambda m: m, data))
        return energy_vm


def overview_chart(chart):
    time_list = list()
    for data in chart:
        timestamps = data['timestamp']
        value = data['value']
        epoch = list()
        for timestamp in timestamps:
            if len(str(timestamp)) > 19:
                timestamp = str(timestamp)[:-7]
            pattern = '%Y-%m-%d %H:%M:%S'
            epoch.append(int(time.mktime(time.strptime(str(timestamp), pattern)))*1000)
        time_list.append(zip(epoch, value))
    return time_list


def data_chart(energy_vm):
    last_timestamp = ''
    value = 0
    energy_list = list()
    for tenants in energy_vm:
        ene_list, time_list = list(), list()
        for vms in tenants:
            if last_timestamp == '':
                last_timestamp = vms.timestamp
                value += vms.wattsmean
            elif last_timestamp == vms.timestamp:
                value += vms.wattsmean
            else:
                ene_list.append(value)
                time_list.append(vms.timestamp)
                value = vms.wattsmean
                last_timestamp = vms.timestamp
        values = map(lambda m: m, ene_list)
        energy_list.append(dict(timestamp=time_list, value=values))
    return energy_list