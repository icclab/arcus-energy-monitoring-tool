/*App.graphController = Ember.ArrayController.create({
    content : Ember.A([]),

    createGraph : function(renderTo, graphType) {
        var chart = App.ChartConfig.create();
        chart.set('renderToId', renderTo);
        chart.set('graphType', graphType);
        chart.setChart();
        this.pushObject(chart);
    },

    renderCharts : function() {
        //$('.overview-chart').highcharts(this);
        this.forEach(this.renderChart, this);
    },

    renderChart : function(config) {
        new Highcharts.Chart($.extend({}, config));
    },

    switchTypes : function() {
        this.forEach(function(chart) {
            var newType = chart.graphType == 'line' ? 'column' : 'line';
            chart.set('graphType', newType);
            chart.setChart();
        });
        this.renderCharts();
    }
});

App.graphController.createGraph('overview-chart', 'line');
App.graphController.renderCharts();
/*


/* Test
App.ChartConfig = Ember.Object.extend({
    chart : null,

    setChart : function() {
        var chart = {
            renderTo : this.get('renderToId'),
            defaultSeriesType : this.get('graphType')
        };
        this.set('chart', chart);
    },

    xAxis : {
        categories : [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                'Sep', 'Oct', 'Nov', 'Dec' ]
    },

    series : [
            {
                name : 'Test',
                data : [ 29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5,
                        216.4, 194.1, 95.6, 54.4 ]
            },
            {
                name : 'Test2',
                data : [ 30.9, 56.5, 90.4, 160.2, 140.0, 150.0, 190.6, 200.5,
                        150.4, 210.1, 100.6, 80.4 ]
            } ],

    plotOptions : {
        series : {
            cursor : 'pointer',
            allowPointSelect : true,
            point : {
                events : {
                    click : function() {
                        App.graphController.switchTypes();
                    }
                }
            }
        }
    },

    renderTo : null,

    graphType : null

});
*/
