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
from calendar import monthrange
import time
import keystoneclient.v2_0.client as ksclient
from arcus_database import MonthlyJoules, PowerSamplesAdm, VmPower
import ConfigParser


class Admin:
    _config = ConfigParser.RawConfigParser()
    _config.read('/home/icclab/Ember-Django/Arcus/energy/arcus.conf')

    _token = _config.get('keystone_credentials', 'token')
    _admin_url = _config.get('keystone_credentials', 'admin_url')
    _ceilometer_url = _config.get('ceilometer', 'auth_url')

    month_list = ['January', 'February', 'March', 'April',
                  'May', 'June', 'July', 'August', 'September',
                  'October', 'November', 'December']

    def __init__(self, token):
        self.client = self._credentials(token)

        date_now = datetime.now()
        self.year = date_now.year
        self.month = date_now.month
        self.day = date_now.day
        self.end_day = monthrange(self.year, self.month)[1]
        self.power_meters, self.project_list, self.energy = list(), list(), list()

    def _credentials(self, token):
        """

        :rtype : ceilometer_client
        :type self: Admin
        """
        return clients.Client(2, endpoint=self._ceilometer_url, token=lambda: token)


class AdminManager(Admin):

    def tenants_name(self):
        """

        :rtype : list
        :type self: Admin
        """
        keystone = ksclient.Client(token=self._token,
                                   endpoint=self._admin_url)
        return keystone.tenants.list()

    def hosts(self):
        """

        :type self: Admin
        """
        resource_meter, self.power_meters = list(), list()
        meter_list = self.client.meters.list()
        for meter in meter_list:
            if meter.name == 'power':
                resource_meter.append(meter.resource_id)
        self.power_meters = resource_meter

    def projects(self):
        """

        :type self: Admin
        """
        project_list = list()
        meter_list = self.client.meters.list()
        for meter in meter_list:
            if meter.project_id not in project_list and meter.project_id is not None:
                project_list.append(meter.project_id)
        self.project_list = project_list

    def energy_samples(self):
        """

        :rtype : dict
        :type self: AdminManager
        """
        data_list = list()
        data = ''
        for meter in self.power_meters:
            date_query = '{0}-{1}'.format(str(self.year), str(self.month_list[self.month-1]))
            data = PowerSamplesAdm.select().where((PowerSamplesAdm.date == date_query) &
                                                  (PowerSamplesAdm.resource == meter))
            if data:
                data_list.append(map(lambda m: m.value, data))

        values = map(lambda m: sum(m), zip(*data_list))
        timestamp = (map(lambda m: m.timestamp, data))
        return dict(timestamp=timestamp, value=values)

    def total_energy(self):
        energy_list = list()
        energy_list_sup = list()
        date_query = '{0}-{1}'.format(str(self.month_list[self.month-1]), str(self.year))
        data = MonthlyJoules.select().where((MonthlyJoules.date == date_query))
        for energy in data:
            if energy.resource not in energy_list_sup:
                energy_list_sup.append(energy.resource)
                energy_list.append(dict(resource=energy.resource, value=energy.joules))
            else:
                for e in energy_list:
                    if energy.resource == e['resource']:
                        e['value'] += energy.joules
        self.energy = energy_list

    def overview(self):
        """

        :rtype : dict
        :type self: AdminManager
        """
        self.total_energy()
        self.hosts()
        data_chart = self.energy_samples()
        month_seconds = 60*60*24*self.day
        highest_server = 0
        total = sum(map(lambda m: m['value'], self.energy))/1000

        for data in self.energy:
            if data['value'] > highest_server:
                highest_server = data['value']
        highest_server /= 1000
        mean_rate_highest = (highest_server*1000)/month_seconds
        mean_rate = (total*1000)/month_seconds
        chart_data = overview_chart(data_chart)
        chart = dict(name='Server', data=chart_data)

        return dict(id=1, total=total, mean_rate=int(mean_rate), rate_energy=mean_rate_highest,
                    month=self.month_list[self.month-1], hosts=len(self.power_meters), chart=[chart])

    def consumption_hosts(self):
        """

        :rtype : dict
        :type self: AdminManager
        """
        self.total_energy()
        chart = []
        highest_server = 0
        for results in self.energy:
            chart.append({'name': results['resource'],
                          'data': [int(results['value'])/1000]})
            if results['value'] > highest_server:
                highest_server = results['value']
        highest_server /= 1000
        total = int(sum(map(lambda m: m['data'][0], chart)))
        month_seconds = 60*60*24*self.day
        mean_rate = (total*1000)/month_seconds
        mean_rate_highest = (highest_server*1000)/month_seconds
        return dict(id=1, total=total, mean_rate=mean_rate, host_rate=mean_rate_highest, number_hosts=len(chart),
                    month=self.month_list[self.month-1], chart=chart)

    def consumption_projects(self):
        self.total_energy()
        self.projects()
        total_energy = sum(map(lambda m: int(m['value']), self.energy))/1000
        energy_project = self.energy_project()
        high_energy_project, total = 0, 0
        data_chart = list()
        projects = self.tenants_name()
        vm_project, project_name, highest_project = '', '', ''
        for tenant in energy_project:
            total_project = 0
            for vms in tenant:
                total_project += vms.joulesmean
                vm_project = vms.project
                total += vms.joulesmean
            total_project /= 1000
            total /= 1000
            for p in projects:
                if p.id == vm_project:
                    project_name = p.name
            if total_project > high_energy_project:
                high_energy_project = total_project
                highest_project = project_name
            data_chart.append(dict(name=project_name, data=[total_project]))
        print len(energy_project)
        print energy_project
        mean_rate_project = total/len(energy_project)
        return dict(id=1, total=total_energy, mean_rate=int(mean_rate_project), number_proj=len(energy_project),
                    month=self.month_list[self.month-1], highest_prj=high_energy_project, highest_name=highest_project,
                    chart=data_chart)

    def variation(self, start):
        start = int(start)
        month_energy_list = self.energy_per_month(start)
        highest_consumption, total = 0, 0
        highest_month = ''
        for month in month_energy_list:
            total = total + month['data'][0]
            if month['data'][0] > highest_consumption:
                highest_consumption = month['data'][0]
                highest_month = month['name']
        return dict(id=1, total=total, highest_month=highest_month, highest_energy=highest_consumption,
                    month=self.month_list[self.month-1], chart=month_energy_list)

    def energy_per_month(self, start):
        month_energy_list = []
        for month in range(start, self.month+2):
            date_query = '{0}-{1}'.format(str(self.month_list[month-1]), str(self.year))
            data = MonthlyJoules.select().where((MonthlyJoules.date == date_query))
            energy = sum(map(lambda m: int(m.joules), data))/1000
            month_energy_list.append({'name': self.month_list[month-1],
                                      'data': [energy]})
        return month_energy_list

    def energy_project(self):
        energy_vm = list()
        for project in self.project_list:
            is_empty = True
            date_query = '{0}-{1}'.format(str(self.year), str(self.month_list[self.month-1]))
            data = VmPower.select().where((VmPower.project == project) & (VmPower.date == date_query))
            for d in data:
                if d.project:
                    is_empty = False
            if not is_empty:
                energy_vm.append(map(lambda m: m, data))
        return energy_vm


def overview_chart(data_chart):
    timestamps = data_chart['timestamp']
    value = data_chart['value']
    epoch = list()
    for timestamp in timestamps:
        if len(str(timestamp)) > 19:
            timestamp = str(timestamp)[:-7]
        pattern = '%Y-%m-%d %H:%M:%S'
        epoch.append(int(time.mktime(time.strptime(str(timestamp), pattern)))*1000)
    time_list = zip(epoch, value)
    return time_list
