
const mv_days = 30;
const ma_days = 60;

function pct_fmt(pct) {
  let cls = pct == 0 ? '' : (pct < 0 ? 'dec' : 'inc');
  let str = pct.toLocaleString('en-US', {signDisplay:'always', maximumFractionDigits:2});
  return `<span class="${cls}">${str}%</span>`;
}

function calculate_sma(data, idx, days, attr='close') {
  if (idx < days)
    return null;
  var sum = 0;
  for (var i=0; i<days; i++)
    sum += data[idx-1-i][attr];
  return sum / days;
}

function mark_price(data) {
  var hi = null;
  var lo = null;

  for (let d of data) {
    if (hi == null || d.y > hi.y)
      hi = d;
    if (lo == null || d.y < lo.y)
      lo = d;
  }

  for (let d of [hi, lo]) {
    d.indexLabel = `${d.y}`;
    d.indexLabelFontColor = "white";
    d.indexLabelBackgroundColor = "black";
    d.indexLabelFontSize = 12;
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

function add_strip_line(data) {
  const vals = data.map(x => x.close);
  const pz = vals[vals.length - 1];
  const hi = Math.max(...vals);
  const lo = Math.min(...vals);
  const pz_pct = (pz - hi) / (hi - lo) * 100;
  const pcts = [-23.6, -38.2, -61.8];
  var lines = [];

  for (const pct of pcts) {
    const v = hi + (hi - lo) * pct / 100;
    lines.push({
      value:v,
      color:"grey",
      label:`${v.toFixed(1)} (${pct.toFixed(0)}%)`,
      labelPlacement:"inside",
      labelAlign:"far",
      labelFontColor:"grey",
      labelFontSize:14,
      lineDashType: "dash",
      thickness: 1.5,
    });
  }

  lines.push({
    value:pz,
    color:"red",
    label:`${pz} (${pz_pct.toFixed(0)}%)`,
    labelPlacement:"inside",
    labelAlign:"far",
    labelFontColor:"red",
    labelBackgroundColor:"white",
    labelFontSize:14,
    lineDashType: "dash",
    thickness: 1.5,
  });

  return [hi, lo, lines];
}

function updateChart(obj) {
  const data = obj.data;
  const pz = data[data.length - 1].close;
  const [hi, lo, strip_line] = add_strip_line(data);
  var dp_pz = [], dp_vol = [], dp_ma = [];
  var stockChart = new CanvasJS.StockChart("chartContainer",{
    theme: "light2",
    title: {
      text: `${obj.code} ${obj.name}`,
      fontSize: 20
    },
    charts: [{
      toolTip: {
        shared: true,
        contentFormatter: function (e) {
          return `pz ${e.entries[0].dataPoint.y}`;
        }
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
        stripLines:strip_line,
        minimum: lo,
        maximum: hi,
      },
      legend: {
        verticalAlign: "top",
        horizontalAlign: "left"
      },
      data: [{
        name: "Price",
        yValueFormatString: "#,###.##",
        type: "line",
        dataPoints : dp_pz,
        color: "DodgerBlue"
      }]
    },
    {
      height: 100,
      title: {
        text: "Vol"
      },
      toolTip: {
        shared: true,
        content: "vol {y}"
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
        name: "Vol",
        dataPoints : dp_vol
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
      enabled: false
    }
  });

  // dp_price
  for (let d of data)
    dp_pz.push({x: new Date(d.date), y: Number(d.close)});
  mark_price(dp_pz);

  // dp_vol
  for (let d of data)
    dp_vol.push({x: new Date(d.date), y: Number(d.volume)});

  // dp_ma
  if (data.length > ma_days) {
    for (var i = 0; i < data.length; i++) {
      var pct = null;
      var sma = calculate_sma(data, i, ma_days);
      if (sma != null)
        pct = data[i].close / sma * 100 - 100;
      dp_ma.push({x: new Date(data[i].date), y: pct});
    }
    mark_label(dp_ma);
  }

  stockChart.render();

  const ma_list = [[20, '#E45EF3'], [60, '#369B45']];
  const ma_opts = {
    type: "line",
    showInLegend: true,
    yValueFormatString: "#,###.00",
  };

  for (const [ma, clr] of ma_list) {
    var vals = [];
    for (var i=0; i<data.length; i++)
      vals.push({x: new Date(data[i].date), y: calculate_sma(data, i, ma)});
    stockChart.charts[0].addTo("data", Object.assign({dataPoints: vals, name: "MA"+ma, color:clr}, ma_opts))
  }


  const pct_list = [30, 20, 10, -10, -20, -30];
  const pct_opts = {
    type: "line",
    showInLegend: true,
    yValueFormatString: "#,###.00",
    lineThickness:1,
    lineDashType: "dash"
  };

  for (const pct of pct_list) {
    var vals = [];
    for (var i=0; i<data.length; i++) {
      const v = calculate_sma(data, i, ma_days);
      vals.push({x: new Date(data[i].date), y: (v ? v * (100 + pct) / 100 : null)});
    }
    stockChart.charts[0].addTo("data", Object.assign({dataPoints: vals, name: `${pct}%`}, pct_opts))
  }

}

function updateResult(obj) {
  const data = obj.data;
  const cols = ['date', 'close', 'chg%', 'MA20', 'MA20%', 'MA60', 'MA60%', 'H%', 'vol', 'MV%'];
  const tail = Math.min(data.length, 5);
  const vals = data.map(x => x.close);
  const hi = Math.max(...vals);
  const lo = Math.min(...vals);

  var text = '';

  text += '<table><tr><th>' + cols.join('</th><th>'); + '</tr>';

  for (var i=0; i<tail; i++) {
    let idx = data.length - tail + i;
    let d = data[idx];
    let pz_pct = idx > 0 ? (d.close / data[idx-1].close * 100 - 100): 0;
    let ma20 = calculate_sma(data, idx, 20);
    let ma20_pct = ma20 ? (d.close / ma20 * 100 - 100) : 0;
    let ma60 = calculate_sma(data, idx, 60);
    let ma60_pct = ma60 ? (d.close / ma60 * 100 - 100) : 0;
    let mv = calculate_sma(data, idx, mv_days, 'volume');
    let mv_pct = mv ? Math.round(d.volume / mv * 100) : 0;
    let h_pct = Math.round((d.close - hi) / (hi - lo) * 100);
    let vals = [d.date, d.close, pct_fmt(pz_pct),  ma20 ? ma20.toFixed(2):'-', pct_fmt(ma20_pct), ma60 ? ma60.toFixed(2):'-', pct_fmt(ma60_pct), h_pct, d.volume.toLocaleString(), mv ? mv_pct:'-'];
    text += '<tr><td>' + vals.join('</td><td>') + '</tr>';
  }

  text += '</table>'
  $('#result').html(text);
}

function parseJson(obj) {
  updateChart(obj);
  updateResult(obj);
}

function onDocumentReady() {
  var api_url = 'load.py' + window.location.search + '&n=csv';
  $.getJSON(api_url, parseJson);
}
