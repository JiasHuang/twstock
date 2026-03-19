
function calculate_sma(data, idx, count) {
  if (idx < count - 1)
    return null;
  var sum = 0;
  for (var i=0; i<count; i++)
    sum += data[idx-i].close;
  return sum / count;
}

function updateChart(data) {
  var dataPoints1 = [], dataPoints2 = [], dataPoints3 = [];
  var stockChart = new CanvasJS.StockChart("chartContainer",{
    exportEnabled: true,
    theme: "light2",
    charts: [{
      toolTip: {
        shared: true
      },
      axisX: {
        lineThickness: 5,
        tickLength: 0,
        labelFormatter: function(e) {
          return "";
        },
        crosshair: {
          enabled: true,
          snapToDataPoint: true,
          labelFormatter: function(e) {
            return ""
          }
        }
      },
      legend: {
        verticalAlign: "top",
        horizontalAlign: "left"
      },
      data: [{
        name: "Price",
        yValueFormatString: "#,###.##",
        axisYType: "secondary",
        type: "candlestick",
        risingColor: "green",
        fallingColor: "red",
        dataPoints : dataPoints1
      }]
    },{
      //height: 200,
      toolTip: {
        shared: true
      },
      axisX: {
        crosshair: {
          enabled: true,
          snapToDataPoint: true
        }
      },
      legend: {
        horizontalAlign: "left"
      },
      data: [{
        yValueFormatString: "#,###.##",
        axisYType: "secondary",
        name: "MA%",
        dataPoints : dataPoints2
      }]
    }],
    navigator: {
      data: [{
        dataPoints: dataPoints3
      }],
    }
  });

  // dataPoints1
  for (let d of data) {
    dataPoints1.push({x: new Date(d.date), y: [Number(d.open), Number(d.high), Number(d.low), Number(d.close)]});
  }

  // dataPoints2
  for (var i = 0; i < data.length; i++) {
    var pct = null;
    var sma = calculate_sma(data, i, 60);
    if (sma != null)
      pct = (data[i].close / sma - 1) * 100;
    dataPoints2.push({x: new Date(data[i].date), y: pct});
  }

  // dataPoints3
  for (let d of data) {
    dataPoints3.push({x: new Date(d.date), y: Number(d.close)});
  }

  stockChart.render();
  const ma_list = [[5, '#F29A5F'], [20, '#E45EF3'], [60, '#5DDBF4']];
  for (const [ma, clr] of ma_list) {
    var vals = [];
    for (var i=0; i<data.length; i++)
      vals.push({x: new Date(data[i].date), y: calculate_sma(data, i, ma)});
    stockChart.charts[0].addTo("data", { type: "line", dataPoints: vals, showInLegend: true, yValueFormatString: "#,###.00", name: "SMA"+ma, color: clr})
  }
}

function updateResult(data) {
  var text = '';
  const cols = ['date', 'close', 'MA', 'MA%'];

  text += '<table><tr><th>' + cols.join('</th><th>'); + '</tr>';

  for (var i=0; i<Math.min(data.length, 5); i++) {
    console.log(i);
    let idx = data.length - 1 - i;
    let d = data[idx];
    let ma = calculate_sma(data, idx, 60);
    let pct = (d.close / ma - 1) * 100;
    let vals = [d.date, d.close, ma.toFixed(2), pct.toFixed(2)];
    text += '<tr><td>' + vals.join('</td><td>') + '</tr>';
  }

  text += '</table>'
  $('#result').html(text);
}

function parseData(data) {
  updateChart(data);
  updateResult(data);
}

function onDocumentReady() {
  var api_url = 'loadcsv.py' + window.location.search;
  $.getJSON(api_url, parseData);
}
