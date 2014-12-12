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
from datetime import *
import subprocess
from pymongo import *
import time
import sys

username = "ceilometer"
password = "password"
host_ip = "192.168.0.2"

#Example "/home/backup/tmp" - Make sure that the folder doesn't exist
path = "/path/to/tmp/"
zipath = "/path/to/zip/"


class Arcus():
    def __init__(self):
        self.client = MongoClient(host_ip)
        self.db = self.client.ceilometer

        now = datetime.now()
        self.year = now.year
        self.month = now.month

        try:
            print "Creating dirs..."
            execut = subprocess.Popen("mkdir {0}".format(path), shell=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = execut.communicate()
            if err:
                raise Exception("%s" % err)
            else:
                print ("Dir %s created" % path)
        except:
            e = sys.exc_info()[1]
            print "Error: %s" % e

        try:
            execut = subprocess.Popen("mkdir {0}".format(zipath), shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            out, err = execut.communicate()
            if err:
                raise Exception("%s" % err)
            else:
                print("Dir %s created" % zipath)
        except:
            e = sys.exc_info()[1]
            print "Error: %s" % e

    def dump_collections(self):
        collections = self.db.collection_names()
        start = datetime(self.year, self.month-1, 1, 0, 0, 0)
        start = int(time.mktime(start.timetuple())) * 1000
        end = datetime(self.year, self.month, 1, 0, 0, 0)
        end = int(time.mktime(end.timetuple())) * 1000

        for item in collections:
            if item == 'meter':
                command = "mongodump --host {0} -u {1} -p{2} --db ceilometer --collection {3} ".format(host_ip,
                                                                                                       username,
                                                                                                       password,
                                                                                                       item) + \
                          "--query '{timestamp: {$gt: " + "Date({0}), $lt: Date({1})".format(start, end) + "}}'" \
                          + " --out {0}".format(path)
            else:
                command = "mongodump --host {0} -u {1} -p{2} --db ceilometer --collection {3} ".format(host_ip,
                                                                                                       username,
                                                                                                       password,
                                                                                                       item) + \
                          " --out {0}".format(path)
            print "Exporting collection {0} to {1}...".format(item, path)
            try:
                execut = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = execut.communicate()
                if err:
                    raise Exception("%s" % err)
                else:
                    print out
            except:
                e = sys.exc_info()[1]
                print "Error: %s" % e

        print "Zipping {0} to {1}".format(path, zipath)
        command = "zip -r {0}backup-{1}-{2} {3}".format(zipath, self.year, self.month-1, path)
        try:
            execut = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = execut.communicate()
            if err:
                raise Exception("%s" % err)
            else:
                print out
        except:
            e = sys.exc_info()[1]
            print "Error: %s" % e

        print "Deleting temporary files..."
        subprocess.Popen("rm -r {0}".format(path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print "Success"

if __name__ == '__main__':
    manager = Arcus()
    manager.dump_collections()
