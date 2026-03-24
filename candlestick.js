
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
    d.indexLabel = `${d.x.toLocaleDateString('zh-Tw')} ${d.y[3]}`;
  }

}

function updateChart(data) {
  var dp_price = [], dp_mv = [], dp_ma = [], dp_close = [];
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
        dataPoints : dp_price
      }]
    },
    {
      height: 100,
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
        name: "MV%",
        dataPoints : dp_mv
      }]
    },
    {
      height: 100,
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

  mark_price(dp_price);

  // dp_mv
  for (var i = 0; i < data.length; i++) {
    var pct = null;
    var sma = calculate_sma(data, i, mv_days, 'volume');
    if (sma != null)
      pct = data[i].volume / sma * 100;
    dp_mv.push({x: new Date(data[i].date), y: pct});
  }

  // dp_ma
  for (var i = 0; i < data.length; i++) {
    var pct = null;
    var sma = calculate_sma(data, i, ma_days);
    if (sma != null)
      pct = (data[i].close / sma - 1) * 100;
    dp_ma.push({x: new Date(data[i].date), y: pct});
  }

  // dp_close
  for (let d of data) {
    dp_close.push({x: new Date(d.date), y: Number(d.close)});
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
  const cols = ['date', 'close', 'MA', 'MA%', 'volume', 'MV%'];

  text += '<table><tr><th>' + cols.join('</th><th>'); + '</tr>';

  const tail = Math.min(data.length, 5);

  for (var i=0; i<tail; i++) {
    let idx = data.length - tail + i;
    let d = data[idx];
    let y = idx > 0 ? data[idx-1].close:data[idx].close;
    let ma = calculate_sma(data, idx, ma_days);
    let mv = calculate_sma(data, idx, mv_days, 'volume');
    let ma_pct_str = ((d.close / ma - 1) * 100).toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
    let mv_pct_str = (d.volume / mv * 100).toLocaleString('en-US', {maximumFractionDigits:2});
    let vals = [d.date, pz_fmt(d.close, y, true), ma.toFixed(2), ma_pct_str, d.volume.toLocaleString(), mv_pct_str];
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
