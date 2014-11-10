Arcus-Openstack-Energy-Monitoring-Tool
====================

The Arcus energy monitoring tool is a tool to understand how energy is consumed
in an Openstack cluster. At present, it extracts information
from Ceilometer and displays it on a reasonably straightforward
quite interactive Ember-JS based frontend.  

#Requirements

*Kwapi
*Peewee
*Mysql

##Mysql

Create a new database named *arcus* with an user [default aoem]
with all granted access.

#Scheduling Tasks

With cron or any other scheduler set to run the python scripts on Tools folder
every hour. *Do not forget to change the configuration file with the proper settings*


Developed by the ICCLab in ZHAW - mainly http://about.me/brunograz

Code distributed under Apache 2.0 license.
