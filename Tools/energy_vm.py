#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from ceilometerclient import client
from datetime import *
from arcus_database import VmPower
import ConfigParser


class VMPower:
    _config = ConfigParser.ConfigParser()
    _config.read('/etc/cron.hourly/arcus.conf')
    _user = _config.get('keystone_credentials', 'user')
    _passw = _config.get('keystone_credentials', 'password')
    _auth_url = _config.get('keystone_credentials', 'auth_url')
    _tenant = _config.get('keystone_credentials', 'tenant')
    month_list = ['January', 'February', 'March', 'April',
                  'May', 'June', 'July', 'August', 'September',
                  'October', 'November', 'December']

    def __init__(self):
        date1 = datetime.now()
        year = date1.year
        month = date1.month
        day = date1.day
        hour = date1.hour
        self.set_variables(year, month, hour, day)

    def get_client(self):
        keystone = dict(os_username=self._user, os_password=self._passw, os_auth_url=self._auth_url,
                        os_tenant_name=self._tenant)
        ceilometer = client.get_client(2, **keystone)
        return ceilometer

    def hosts(self):
        resource_meter = []
        ceilometer = self.get_client()
        meter_list = ceilometer.meters.list()
        for meter in meter_list:
            if meter.name == 'power':
                resource_meter.append(meter.resource_id)
        power_meters = resource_meter
        return power_meters

    @staticmethod
    def get_query(resource, y, m, h, d):
        if h < 10:
            hour_1 = '0{0}'.format(str(h-1))
            h = '0{0}'.format(str(h))
        elif h == 10:
            hour_1 = '0{0}'.format(str(h-1))
            h = str(h)
        else:
            hour_1 = str(h-1)
        return list((dict(field='timestamp', op='gt',
                          value='{2}-{0}-{3}T{1}:00:00'.format(str(m), str(hour_1), str(y), str(d))),
                     dict(field='timestamp', op='lt',
                          value='{3}-{0}-{1}T{2}:00:00'.format(str(m), str(d), str(h), str(y))),
                     dict(field='resource_id', op='eq', value=resource)))

    def get_energy_meters(self, query):
        ceilometer = self.get_client()
        samples = ceilometer.samples.list(meter_name='energy', q=query)
        return samples

    def set_instances(self):
        resource_meter = []
        ceilometer = self.get_client()
        meter_list = ceilometer.meters.list()
        for meter in meter_list:
            if meter.name == 'instance':
                resource_meter.append(meter.resource_id)
        instance_meters = resource_meter
        return instance_meters

    def get_instances(self, query, limit):
        query2 = query
        query2.append((dict(field='metadata.status', op='eq', value='active')))
        ceilometer = self.get_client()
        if limit:
            samples = ceilometer.samples.list(meter_name='instance', q=query2, limit=1)
        else:
            samples = ceilometer.samples.list(meter_name='instance', q=query2)
        return samples

    def get_energy_load(self, instances, y, m, h, d):
        utilisation = list()
        ceilometer = self.get_client()
        for instance in instances:
            query = self.get_query(instance.resource_id, y, m, h, d)
            samples = ceilometer.samples.list(meter_name='cpu_util', q=query)
            mean_value = sum(map(lambda x: float(x.counter_volume), samples))
            if mean_value == 0:
                mean_value = 1
            if len(samples) != 0:
                mean_value2 = (mean_value/len(samples))*int(instance.resource_metadata['vcpus'])
                utilisation.append({'instance': instance.resource_metadata['display_name'], 'cpu_util': mean_value2,
                                    'project': instance.project_id})
        return utilisation

    def set_variables(self, y, m, h, d):
        power_meters = self.hosts()
        total_energy, active_instances = 0, 0
        datew, timestamp = '', ''
        instances = list()
        for resources in power_meters:
            query = self.get_query(resources, y, m, h, d)
            energy_samples = self.get_energy_meters(query)
            energy_samples = list(reversed(energy_samples))
            initial_energy = energy_samples[0].counter_volume
            for samples in energy_samples:
                if samples.counter_volume > initial_energy:
                    total_energy += samples.counter_volume - initial_energy
                initial_energy = samples.counter_volume
            datew = str(y) + '-' + self.month_list[m-1]
            timestamp = datetime(y, m, d, h)
        total_energy *= 3600000
        instance_meters = self.set_instances()
        for instance in instance_meters:
            query = self.get_query(instance, y, m, h, d)
            instance_samples = self.get_instances(query, True)
            for sample in instance_samples:
                if sample:
                    active_instances += 1
                    instances.append(sample)
        if active_instances == 0:
            active_instances = 1
        instance_divided_all = int(total_energy)/active_instances
        instance_divided_load = self.get_energy_load(instances, y, m, h, d)
        total_utilisation = sum(map(lambda x: float(x['cpu_util']), instance_divided_load))

        for instance in instance_divided_load:
            energy_per_instance = (int(total_energy)*instance['cpu_util'])/total_utilisation
            joule = VmPower.create(joulesall=instance_divided_all,
                                   joulesmean=energy_per_instance,
                                   date=datew,
                                   timestamp=timestamp,
                                   name=instance['instance'],
                                   project=instance['project'],
                                   wattsall=instance_divided_all/3600,
                                   wattsmean=energy_per_instance/3600)
            joule.save()