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

__author_ = 'gaea'

from django.shortcuts import render_to_response
from django.template import RequestContext
import json
from django.http import HttpResponse
import keystoneclient.v2_0.client as ksclient
from user import UserManager
from adm import AdminManager
import ConfigParser


config = ConfigParser.RawConfigParser()
config.read('/home/icclab/Ember-Django/Arcus/energy/arcus.conf')

_user = config.get('keystone_credentials', 'user')
_passw = config.get('keystone_credentials', 'password')
_auth_url = config.get('keystone_credentials', 'auth_url')
_tenant = config.get('keystone_credentials', 'tenant')


def login(request):
    return render_to_response("home.html",
                              {}, context_instance=RequestContext(request))


def authenticate_token(tok):
    keystone = dict(username=_user, password=_passw, auth_url=_auth_url,
                    tenant_name=_tenant)
    kclient = ksclient.Client(**keystone)
    try:
        kclient.get_raw_token_from_identity_service(token=tok, auth_url=_auth_url)
        return True
    except:
        return False


def is_admin(token):
    kclient = ksclient.Client(token=token, auth_url=_auth_url)
    tenants = kclient.tenants.list()
    adm = False
    for tenant in tenants:
        if tenant.name == 'admin':
            adm = True
            break
    return adm


def authentication_request(request):
    user = str(request.GET.get('user', ''))
    passw = str(request.GET.get('pass', ''))
    try:
        token = get_credentials(user, passw)
        if token['admin']:
            return HttpResponse(json.dumps({'status': 1,
                                            'user': token['user'],
                                            'token': token['token']}))
        else:
            return HttpResponse(json.dumps({'status': 0,
                                            'user': token['user'],
                                            'token': token['token']}))
    except:
        return HttpResponse(status=422)


def get_credentials(username, password):
    keystone = dict(username=username, password=password, auth_url=_auth_url)
    adm = False
    tenant_name = ''
    clients = ksclient.Client(**keystone)
    tenants = clients.tenants.list()
    user = clients.auth_ref
    username = user['user']['username']
    for tenant in tenants:
        tenant_name = tenant.name
        if tenant.name == 'admin':
            adm = True
            break
    keystone = dict(username=username, password=password, auth_url=_auth_url,
                    tenant_name=tenant_name)
    client2 = ksclient.Client(**keystone)
    token = client2.auth_token
    return dict(admin=adm, user=username, token=token)


def get_overview_menu(request):
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        user2 = UserManager(token)
        return HttpResponse(json.dumps([user2.overview()]))
    else:
        return HttpResponse(status=422)


def get_vm_menu(request):
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        user = UserManager(token)
        return HttpResponse(json.dumps([user.consumption_vm()]))
    else:
        return HttpResponse(status=422)


def get_project_menu(request):
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        user = UserManager(token)
        return HttpResponse(json.dumps([user.consumption_project()]))
    else:
        return HttpResponse(status=422)


def get_variation(request):
    start = str(request.GET.get('month', ''))
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        user = UserManager(token)
        return HttpResponse(json.dumps([user.variation(start)]))
    else:
        return HttpResponse(status=422)


def get_admin_hosts(request):
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        if is_admin(token):
            user = AdminManager(token)
            return HttpResponse(json.dumps([user.consumption_hosts()]))
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=422)


def get_admin_project_menu(request):
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        if is_admin(token):
            user = AdminManager(token)
            return HttpResponse(json.dumps([user.consumption_projects()]))
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=422)


def get_admin_variation(request):
    start = str(request.GET.get('month', ''))
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        if is_admin(token):
            user = AdminManager(token)
            return HttpResponse(json.dumps([user.variation(start)]))
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=422)


def get_admin_overview(request):
    token = str(request.GET.get('token', ''))
    if authenticate_token(token):
        if is_admin(token):
            user = AdminManager(token)
            return HttpResponse(json.dumps([user.overview()]))
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=422)