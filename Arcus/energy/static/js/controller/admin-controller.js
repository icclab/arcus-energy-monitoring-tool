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
                  xAxis: {title: {text: 'Hosts'}, labels:{enabled: false}},
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
                  xAxis: { title: {text: 'Month'}, labels:{enabled: false}},
                  yAxis: { title: { text: 'Power (kJ)' }, plotLines: [{ value: 0, width: 1, color: '#808080' }] },
                  tooltip: { valueSuffix: 'kJ' },
                  legend: { layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0 }
               };


App.AdminIndexController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions,
});

App.AdminController = Ember.Controller.extend({
  needs: ['application', 'index'],
});

App.AdminHostsController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions2,
});

App.AdminProjectController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions3,
});

App.AdminVariationController = Ember.Controller.extend({
  needs: ['index'],
  chartOptions: chartOptions4,
});
