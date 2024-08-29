
/*
    This function is not used anywhere, this function can be used for a reference
*/


import * as Chart from 'chart.js';

export function ChartData(serveData) {
    var lineGraph = [];
    for (let i = 0; i <= 3; i++) {
        lineGraph[i] =
            serveData.CPA110[i] + serveData.CPA430[i] + serveData.CPA530[i];
    }
    var bar_chart = new Chart("barChart", {
        type: "bar",
        data: {
            labels: serveData.names,
            datasets: [
                {
                    label: "CPA110",
                    data: serveData.CPA110,
                    backgroundColor: "#ffd800",
                    hoverBorderWidth: 3,
                    hoverBorderColor: "lightgrey"
                },
                {
                    label: "EJA430E",
                    data: serveData.CPA430,
                    backgroundColor: "#6fb98f",
                    hoverBorderWidth: 3,
                    hoverBorderColor: "lightgrey"
                },
                {
                    label: "EJA530E",
                    data: serveData.CPA530,
                    backgroundColor: "#2c7873",
                    hoverBorderWidth: 3,
                    hoverBorderColor: "lightgrey"
                },
                {
                    type: "scatter",
                    label: "Total",
                    data: lineGraph,
                    backgroundColor: "#004445"
                }
            ]
        },
        options: {
            responsive: true,
            animation: {
                duration: 10
            },
            scales: {
                xAxes: [
                    {
                        stacked: true,
                        ticks: {
                            fontColor: "black",
                            fontSize: 12,
                            stepSize: 500,
                            beginAtZero: true
                        }
                    }
                ],
                yAxes: [
                    {
                        stacked: true,
                        ticks: {
                            fontColor: "black",
                            fontSize: 12,
                            stepSize: 500,
                            beginAtZero: true
                        }
                    }
                ]
            },
            legend: { display: true },
            title: {
                display: true,
                text: 'Pending Order\'s Status',
                fontSize: 16,
            }
        }
    });
}