/*
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
*/
App.Router.map(function() {
  this.resource('app', {path: '/index'}, function(){
    this.route('energyVm');
    this.route('energyProject');
    this.route('variation');
  });
  this.resource('admin', {path: '/adm'}, function(){
    this.route('hosts');
    this.route('project');
    this.route('variation');
  });
  this.resource('index', {path:'/'});
  this.resource('session');
});

App.IndexRoute = Ember.Route.extend({
  init: function(){
    this.set('loginFailed', false);
    this.set('isProcessing', false);
    this.set('users', null);
    this.set('token', null);
  }
});

App.LoadingRoute = Ember.Route.extend({
  beforeModel: function(){
   $("body").prepend("<div class=\"spinner\"><div/><div/><div/></div>");
  },
  afterModel: function(){
    $(".spinner").remove();
   },
  actions: {
    error: function(error,transition){
      if(error && error.status === 422){
        this.controllerFor('index').set('sessionTimeout', true);
        $(".spinner").remove();
        return this.transitionTo('index');
      }else if(error && error.status === 403){
        $(".spinner").remove();
        return this.transitionTo('session');
      }
    }
  }
});

App.AppIndexRoute = App.LoadingRoute.extend({
  model: function(){
    if (data === ''){
      var token = { token: this.controllerFor('application').get('token')};
      data = Ember.$.ajax({url: '/overview', dataType: 'json', data: token}).then(function(data){
        return {data: data, series: data[0].chart}})
      return data
    }else return data
  },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  },
  actions: {
    error: function(error,transition){
      if(error && error.status === 422){
        this.controllerFor('index').set('sessionTimeout', true);
        $(".spinner").remove();
        return this.transitionTo('index');
      }
    }
  }
});

App.AppEnergyVmRoute = App.LoadingRoute.extend({
  model: function(){
    if (dataVM === ''){
      var token = { token: this.controllerFor('application').get('token')};
      dataVM = Ember.$.ajax({url: '/getEnergyVm', dataType: 'json', data: token}).then(function(data){
        return {data:data, series: data[0].chart}})
      return dataVM;
      }
      else return dataVM;
    },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  }
});

App.AppVariationRoute = App.LoadingRoute.extend({
  model: function(){
    if (dataVariation === ''){
      var date = new Date();
      var month = { month: String(date.getMonth()), token: this.controllerFor('application').get('token')};
      dataVariation = $.ajax({url: '/getVariation', dataType: 'json', data: month}).then(function(data){
        return {data: data, series: data[0].chart}});
      return dataVariation;
    } else
        return dataVariation;
    },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  }
});

App.AppEnergyProjectRoute = App.LoadingRoute.extend({
  model: function(){
    if (dataProject === ''){
    var token = { token: this.controllerFor('application').get('token')};
      dataProject = Ember.$.ajax({url: '/getProject', dataType: 'json', data: token}).then(function(data){
      return {data: data, series: data[0].chart}})
    return dataProject
    }
    else return dataProject
      },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  }
});

App.AdminIndexRoute = Ember.Route.extend({
  model: function(){
    if (dataAdmin === ''){
      var token = { token: this.controllerFor('application').get('token')};
      dataAdmin =  Ember.$.ajax({url: '/admOverview', dataType: 'json', data: token}).then(function(data){
        return {data: data, series: data[0].chart}})
      return dataAdmin;
    }else return dataAdmin;
  },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  },
  actions: {
    error: function(error,transition){
      if(error && error.status === 422){
        this.controllerFor('index').set('sessionTimeout', true);
        $(".spinner").remove();
        return this.transitionTo('index');
      }else if(error && error.status === 403){
        $(".spinner").remove();
        return this.transitionTo('session');
      }
    }
  }
});

App.AdminHostsRoute = App.LoadingRoute.extend({
  model: function(){
    if (dataAdminHost === ''){
      var token = { token: this.controllerFor('application').get('token')};
      dataAdminHost =  Ember.$.ajax({url: '/admHosts', dataType: 'json', data: token}).then(function(data){
        return {data: data, series: data[0].chart}})
      return dataAdminHost
    }else return dataAdminHost;
  },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  }
});

App.AdminProjectRoute = App.LoadingRoute.extend({
  model: function(){
    if (dataAdminProject === ''){
      var token = { token: this.controllerFor('application').get('token')};
      dataAdminProject =  Ember.$.ajax({url: '/admProj', dataType: 'json', data: token}).then(function(data){
        return {data: data, series: data[0].chart}})
      return dataAdminProject;
    }else return dataAdminProject;
  },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  }
});


App.AdminVariationRoute = App.LoadingRoute.extend({
  model: function(){
    if (dataAdminVariation === ''){
      var date = new Date();
      var month = { month: String(date.getMonth()), token: this.controllerFor('application').get('token')};
      dataAdminVariation = Ember.$.ajax({url: '/admVariation', dataType: 'json', data: month}).then(function(data){
        return {data: data, series: data[0].chart}})
      return dataAdminVariation;
    }else return dataAdminVariation;
    },
  setupController: function(controller, model) {
    controller.set('data', model.data);
    controller.set('series', model.series);
  }
});
