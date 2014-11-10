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

App.ApplicationController = Ember.Controller.extend({
  needs: ['index'],
  user: localStorage.App_user,//Ember.computed.alias('controllers.index.users'),
  token: localStorage.App_auth_token,//Ember.computed.alias('controllers.index.token'),
});

App.AppController = Ember.Controller.extend({
  actions:{
    logout: function(){
      this.transitionToRoute('index');
    },
  },
});

App.SessionController = Ember.Controller.extend({
  actions:{
    logout: function(){
      this.transitionToRoute('index');
    },
  },
});

App.IndexController = Ember.Controller.extend({
  users: null,
  token: null,
  sessionTimeout: false,
  loginFailed: false,
  isProcessing: false,

  init: function(){
    this.set('loginFailed', false);
    this.set('isProcessing', false);
    this.set('users', null);
    this.set('token', null);
    localStorage.App_auth_token = this.get('token');
    localStorage.App_user = this.get('users');
  },
  actions: {
    login: function() {
      this.send('reset');
      this.set('isProcessing', true);

      var user = String($("#username").val());
      var password = String($("#password").val());
      var data1 = { user: user, pass: password };

      var request = Ember.$.ajax({url: '/authentication', dataType:'json', data: data1, success: function(data){this.send('success', data)}.bind(this)});
      request.fail(function(){this.send('failure')}.bind(this));
    },
    success: function(data) {
      this.set('users', data.user);
      this.set('token', data.token);
      localStorage.App_auth_token = this.get('token');
      localStorage.App_user = this.get('users');
      if (data.status === 1)
        this.transitionToRoute('admin');
      else this.transitionToRoute('app');
    },
    failure: function() {
      this.set("loginFailed", true);
      this.set('isProcessing', false);
    },
    reset: function() {
      this.set("loginFailed", false);
      this.set('isProcessing', false);
      this.set('sessionTimeout', false);
    }
  }
});

chartOptions = { title:
                { text: 'Energy Measurement', x: -20 },
                 subtitle: { text: '', x: -20 },
                 xAxis: {type: 'datetime' ,title: {text: 'Date'}},
                 yAxis: { title: { text: 'Power (W)' }, plotLines: [{ value: 0, width: 0.5, color: '#808080' }] },
                 tooltip: { valueSuffix: 'W' },
                 legend: { layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0 }
               };

chartOptions2 = { chart:
                 { type: 'column'},
                  title:
                 { text: 'Energy Measurement', x: -20 },
                  subtitle: { text: '', x: -20 },
                  xAxis: {title: {text: 'VMs Active'}, labels:{enabled: false}},
                  yAxis: { title: { text: 'Power (kJ)' }, plotLines: [{ value: 0, width: 1, color: '#808080' }] },
                  tooltip: { valueSuffix: 'kJ' },
                  legend: { layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0 }
               };

chartOptions3 = { chart:
                 { type: 'column'},
                  title:
                 { text: 'Energy Measurement', x: -20 },
                  subtitle: { text: '', x: -20 },
                  xAxis: {title: {text: 'Projects'}, labels:{enabled: false}},
                  yAxis: { title: { text: 'Power (kJ)' }, plotLines: [{ value: 0, width: 1, color: '#808080' }] },
                  tooltip: { valueSuffix: 'kJ' },
                  legend: { layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0 }
               };

chartOptions4 = { chart:
                 { type: 'column'},
                  title:
                 { text: 'Energy Measurement', x: -20 },
                  subtitle: { text: '', x: -20 },
                  xAxis: { labels:{enabled: false}},
                  yAxis: { title: { text: 'Power (kJ)' }, plotLines: [{ value: 0, width: 1, color: '#808080' }] },
                  tooltip: { valueSuffix: 'kJ' },
                  legend: { layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0 }
               };



App.AppIndexController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions,
});

App.AppController = Ember.Controller.extend({
  needs: ['application', 'index'],
});

App.AppEnergyVmController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions2,
});


App.AppEnergyProjectController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions3,
});


App.AppVariationController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions4,
});
