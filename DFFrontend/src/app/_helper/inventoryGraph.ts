import * as Chart from 'chart.js';

export function inventoryGraph(serveData) {
    var bar_chart = new Chart("inventoryGraph", {
        type: "bar",
        data: {
            labels: serveData['date'],
            datasets: [
                { data: serveData['CPA_Cost'],type:'line', label: 'CPA Cost',backgroundColor: '#BDF47E', yAxisID: 'A',
                borderColor: "#58508d", borderDash: [3, 3]},
                { data: serveData['KDP_Cost'],type:'line', label: 'KDP Cost',backgroundColor: '#E9F47E', yAxisID: 'A',
                borderColor: "#003f5c", borderDash: [6, 6]},
                { data: serveData['Total_Inventory'],type:'line', label: 'Total Inventory Cost',backgroundColor: '#7EF4DF', yAxisID: 'A', },
                { data: serveData['CPA_total'],type:'line', label: 'CPA Total',yAxisID: 'B', fill:false,
                backgroundColor: '#4A948F',borderColor: "#ffa600", borderDash: [9, 9]},

                { data: serveData['CPA110Y'], label: 'CPA110Y', stack: 'a', backgroundColor: '#DAB700', yAxisID: 'B', },
                { data: serveData['CPA530Y'], label: 'CPA430Y', stack: 'a', backgroundColor: '#428B64',  yAxisID: 'B',},
                { data: serveData['CPA430Y'], label: 'CPA430Y', stack: 'a', backgroundColor: '#4A948F', yAxisID: 'B',},
            ]
        },
options: {
    scales: {
        yAxes: [{
            id: 'A',
            position: 'right',
        }, {
            id: 'B',
            position: 'left',
            ticks : {
            beginAtZero: true,
            fontColor: "Black",
            },
        }]
        },
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
    legend: {
        display: true,
    },
    title: {
        display: true,
        text: 'Inventory Status',
        fontSize: 18,                
    },
},        

    });
}

