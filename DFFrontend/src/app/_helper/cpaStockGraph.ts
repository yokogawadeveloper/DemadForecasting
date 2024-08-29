import * as Chart from 'chart.js';

export function CpaStockChartData(serveData) {
    var bar_chart = new Chart("CpaStockBarChart", {
        type: "bar",
        data: {
            labels: ['Pending;Total', 'Stock;Total', 'Pending;Current Month', 'Stock;Current Month',
                 'Pending;Next Month', 'Stock;Next Month', 'Pending;2 Months and above', 'Stock;2 Months and above'],
            datasets: [
                { data: serveData['EJA110STOCK'], label: 'EJA110E STOCK', stack: 'a', backgroundColor: '#DAB700' },
                { data: serveData['EJA110PIPE'], label: 'EJA430E PIPE', stack: 'a', backgroundColor: '#F6D000' },
                { data: serveData['EJA430STOCK'], label: 'EJA430E STOCK', stack: 'a', backgroundColor: '#4F9870' },
                { data: serveData['EJA430PIPE'], label: 'EJA430E PIPE', stack: 'a', backgroundColor: '#428B64' },
                { data: serveData['EJA530STOCK'], label: 'EJA530E STOCK', stack: 'a', backgroundColor: '#4A948F' },
                { data: serveData['EJA530PIPE'], label: 'EJA530E PIPE', stack: 'a', backgroundColor: '#297571' },

                {
                    data: serveData['EJA110'], label: 'EJA110E', stack: 'a',
                    backgroundColor: "#ffd800",
                },
                {
                    data: serveData['EJA430'], label: 'EJA430E', stack: 'a',
                    backgroundColor: "#6fb98f",
                },
                {
                    data: serveData['EJA530'], label: 'EJA530E', stack: 'a',
                    backgroundColor: "#2c7873",
                },
            ]
        },
        options: {
            layout: {
                padding: {
                    left: 20,
                    right: 20,
                    top: 20,
                    bottom: 20
                }
            },
            tooltips: {
                enabled: true,
                titleAlign: 'center',
                titleSpacing: 1,
                caretPadding: 2,
                cornerRadius: 6,
                position: 'average',
            },
            responsive: true,
            maintainAspectRatio: true,
            scales:{
                xAxes:[
                  {
                    id:'xAxis1',
                    ticks:{
                      callback:function(label){
                        var firstAxesLabel = label.split(";")[0];
                        return firstAxesLabel;
                      }
                    }
                  },
                  {
                    id:'xAxis2',
                    gridLines: {
                      drawOnChartArea: false,
                    },
                    ticks:{
                      callback:function(label){
                        var secondAxesLabel = label.split(";")[1];                      
                        return secondAxesLabel;
                      }
                    }
                  }],
                yAxes:[{
                  ticks:{
                    beginAtZero:true
                  }
                }]
              },
            legend: {
                display: true,
            },
            title: {
                display: true,
                text: 'CPA Stock VS Pending order Status',
                fontSize: 16,
            }
        }
    });
}