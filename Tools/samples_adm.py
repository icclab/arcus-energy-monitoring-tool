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
from arcus_database import PowerSamplesAdm
import ConfigParser


class SamplesAdmin:

    _config_monthly = ConfigParser.ConfigParser()
    _config_monthly.read('/etc/cron.hourly/arcus.conf')
    _user = _config_monthly.get('keystone_credentials', 'user')
    _passw = _config_monthly.get('keystone_credentials', 'password')
    _auth_url = _config_monthly.get('keystone_credentials', 'auth_url')
    _tenant = _config_monthly.get('keystone_credentials', 'tenant')
    month_list = ['January', 'February', 'March', 'April',
                  'May', 'June', 'July', 'August', 'September',
                  'October', 'November', 'December']

    def __init__(self):
        date1 = datetime.now()
        year = date1.year
        month = date1.month
        day = date1.day
        hour = date1.hour
        self.variables(year, month, hour, day)

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
            hour_1 = '0' + str(h-1)
            h = '0' + str(h)
        elif h == 10:
            hour_1 = '0' + str(h-1)
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
        samples = ceilometer.samples.list(meter_name='power', q=query)
        return samples

    def variables(self, y, m, h, d):
        power_meters = self.hosts()
        energy_list = list()
        for resources in power_meters:
            query = self.get_query(resources, y, m, h, d)
            energy_samples = self.get_energy_meters(query)
            energy_samples = list(reversed(energy_samples))
            meter_list_len = len(energy_samples)
            div = meter_list_len/5
            if div == 0:
                div = 1
            start = 0
            end = div
            for num in range(0, (meter_list_len/div)):
                energy = sum(map(lambda p: float(p.counter_volume),
                                 energy_samples[start:end]))
                energy /= div
                timestamp = energy_samples[start].timestamp
                energy_list.append(dict(energy=energy, timestamp=timestamp, resource=resources))
                start += div
                end += div
        samples = sorted(energy_list, key=lambda engy: engy['timestamp'])
        for i in samples:
            datew = str(y) + '-' + self.month_list[m-1]
            timestamp = i['timestamp']
            total_energy = i['energy']
            resource1 = i['resource']
            joule = PowerSamplesAdm.create(value=total_energy, resource=resource1, date=datew, timestamp=timestamp)
            joule.save()

manager = SamplesAdmin()
