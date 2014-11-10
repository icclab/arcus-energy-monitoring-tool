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

from peewee import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/home/icclab/Ember-Django/Arcus/energy/arcus.conf')

database_user = config.get('mysql', 'mysql_user')

database = MySQLDatabase('arcus', **{'host': 'xxx.xx.x.x', 'user': database_user})


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = database


class MonthlyJoules(BaseModel):
    date = CharField(max_length=255, null=True)
    joules = IntegerField(null=True)
    resource = CharField(max_length=255, null=True)
    timestamp = DateTimeField(null=True)

    class Meta:
        db_table = 'monthly_joules'


class PowerSamplesAdm(BaseModel):
    date = CharField(max_length=255, null=True)
    resource = CharField(max_length=255, null=True)
    timestamp = DateTimeField(null=True)
    value = IntegerField(null=True)

    class Meta:
        db_table = 'power_samples_adm'


class VmPower(BaseModel):
    date = CharField(max_length=255, null=True)
    joulesall = IntegerField(db_column='joulesAll', null=True)
    joulesmean = IntegerField(db_column='joulesMean', null=True)
    name = CharField(max_length=255, null=True)
    project = CharField(max_length=255, null=True)
    timestamp = DateTimeField(null=True)
    wattsall = IntegerField(db_column='wattsAll', null=True)
    wattsmean = IntegerField(db_column='wattsMean', null=True)

    class Meta:
        db_table = 'vm_power'
