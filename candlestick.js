
const mv_days = 30;
const ma_days = 60;

function pz_fmt(z, y, en_cls=false) {
  const chg = z - y;
  const chg_str = chg.toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const pct_str = (chg / y * 100).toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const cls = (en_cls && chg != 0) ? (chg > 0 ? 'inc':'dec'):'';
  return `${z} (${chg_str}, <span class="${cls}">${pct_str}%</span>)`;
}

function calculate_sma(data, idx, count, attr='close') {
  if (idx < count - 1)
    return null;
  var sum = 0;
  for (var i=0; i<count; i++)
    sum += data[idx-i][attr];
  return sum / count;
}

function mark_price(data) {
  var hi = null;
  var lo = null;

  for (let d of data) {
    if (hi == null || d.y[3] > hi.y[3])
      hi = d;
    if (lo == null || d.y[3] < lo.y[3])
      lo = d;
  }

  for (let d of [hi, lo]) {
    d.indexLabel = `${d.y[3]}`;
    d.indexLabelFontColor = "white";
    d.indexLabelBackgroundColor = "black";
  }

}

function mark_label(data) {
  var hi = null;
  var lo = null;

  for (let d of data) {
    if (d.y == null)
      continue;
    if (hi == null || d.y > hi.y)
      hi = d;
    if (lo == null || d.y < lo.y)
      lo = d;
  }

  for (let d of [hi, lo]) {
    d.indexLabel = `${d.y.toLocaleString('en-US', {maximumFractionDigits:2})}`;
    d.indexLabelFontColor = "white";
    d.indexLabelBackgroundColor = "black";
  }

}


function updateChart(data) {
  const pz = data[data.length - 1].close;
  var dp_price = [], dp_mv = [], dp_ma = [], dp_close = [];
  var stockChart = new CanvasJS.StockChart("chartContainer",{
    theme: "light2",
    charts: [{
      toolTip: {
        shared: true
      },
      axisX: {
        lineThickness: 5,
        tickLength: 0,
        crosshair: {
          enabled: true,
          snapToDataPoint: true,
          valueFormatString: "YY/MM/DD"
        }
      },
      axisY: {
        crosshair: {
          enabled: true,
          snapToDataPoint: true
        },
			  stripLines:[
			    {
				    value:pz,
				    color:"red",
            label:pz,
            labelAlign:"center",
            labelFontColor:"white",
            labelBackgroundColor:"black",
			    }
        ]
      },
      legend: {
        verticalAlign: "top",
        horizontalAlign: "left"
      },
      data: [{
        name: "Price",
        yValueFormatString: "#,###.##",
        type: "candlestick",
        risingColor: "green",
        fallingColor: "red",
        dataPoints : dp_price
      }]
    },
    {
      height: 100,
      title: {
        text: "MV%"
      },
      toolTip: {
        shared: true,
        content: "MV% {y}"
      },
      axisX: {
        crosshair: {
          enabled: true,
          snapToDataPoint: true,
          valueFormatString: "YY/MM/DD"
        }
      },
      axisY: {
        crosshair: {
          enabled: true,
          snapToDataPoint: true
        }
      },
      data: [{
        yValueFormatString: "#,###.##",
        name: "MV%",
        dataPoints : dp_mv
      }]
    },
    {
      height: 100,
      title: {
        text: "MA%"
      },
      toolTip: {
        shared: true,
        content: "MA% {y}"
      },
      axisX: {
        crosshair: {
          enabled: true,
          snapToDataPoint: true,
          valueFormatString: "YY/MM/DD"
        }
      },
      axisY: {
        crosshair: {
          enabled: true,
          snapToDataPoint: true
        }
      },
      data: [{
        yValueFormatString: "#,###.##",
        name: "MA%",
        dataPoints : dp_ma
      }]
    }],
    navigator: {
      data: [{
        dataPoints: dp_close
      }],
    }
  });

  // dp_price
  for (let d of data) {
    dp_price.push({x: new Date(d.date), y: [Number(d.open), Number(d.high), Number(d.low), Number(d.close)]});
  }

  // dp_mv
  for (var i = 0; i < data.length; i++) {
    var pct = null;
    var sma = calculate_sma(data, i, mv_days, 'volume');
    if (sma != null)
      pct = Math.round(data[i].volume / sma * 100);
    dp_mv.push({x: new Date(data[i].date), y: pct});
  }

  // dp_ma
  for (var i = 0; i < data.length; i++) {
    var pct = null;
    var sma = calculate_sma(data, i, ma_days);
    if (sma != null)
      pct = data[i].close / sma * 100 - 100;
    dp_ma.push({x: new Date(data[i].date), y: pct});
  }

  // dp_close
  for (let d of data) {
    dp_close.push({x: new Date(d.date), y: Number(d.close)});
  }

  mark_price(dp_price);
  mark_label(dp_ma);
  mark_label(dp_mv);

  stockChart.render();
  const ma_list = [[5, '#F29A5F'], [20, '#E45EF3'], [60, '#5DDBF4']];
  for (const [ma, clr] of ma_list) {
    var vals = [];
    for (var i=0; i<data.length; i++)
      vals.push({x: new Date(data[i].date), y: calculate_sma(data, i, ma)});
    stockChart.charts[0].addTo("data", { type: "line", dataPoints: vals, showInLegend: true, yValueFormatString: "#,###.00", name: "MA"+ma, color: clr})
  }

  for (const rate of [1.3, 1.2, 1.1, 0.9, 0.8, 0.7]) {
    var vals = [];
    for (var i=0; i<data.length; i++) {
      y = calculate_sma(data, i, 90);
      y = (y != null) ? y * rate : null;
      vals.push({x: new Date(data[i].date), y: y});
    }
    stockChart.charts[0].addTo("data", { type: "line", dataPoints: vals, showInLegend: true, yValueFormatString: "#,###.00", name: "rate"+rate, lineThickness:1, lineDashType: "dash"})
  }

}

function updateResult(data) {
  var text = '';
  const cols = ['date', 'close', 'MA5', 'MA20', 'MA', 'MA%', 'volume', 'MV%'];

  text += '<table><tr><th>' + cols.join('</th><th>'); + '</tr>';

  const tail = Math.min(data.length, 5);

  for (var i=0; i<tail; i++) {
    let idx = data.length - tail + i;
    let d = data[idx];
    let y = idx > 0 ? data[idx-1].close:data[idx].close;
    let ma5 = calculate_sma(data, idx, 5);
    let ma20 = calculate_sma(data, idx, 20);
    let ma = calculate_sma(data, idx, ma_days);
    let mv = calculate_sma(data, idx, mv_days, 'volume');
    let ma_pct_str = (d.close / ma * 100 - 100).toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
    let mv_pct = Math.round(d.volume / mv * 100);
    let vals = [d.date, pz_fmt(d.close, y, true), ma5.toFixed(2), ma20.toFixed(2), ma.toFixed(2), ma_pct_str, d.volume.toLocaleString(), mv_pct];
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
