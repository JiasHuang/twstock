
function updateInfo(obj) {
  const code = obj.code;
  const dict = {
    '基本':`https://fubon-ebrokerdj.fbs.com.tw/z/zc/zca/zca_${code}.djhtm`,
    '獲利':`https://fubon-ebrokerdj.fbs.com.tw/z/zc/zce/zce_${code}.djhtm`,
    '營收':`https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_${code}.djhtm`,
    '新聞':`https://tw.stock.yahoo.com/q/h?s=${code}`,
    'Ｋ線':`chart.html?c=${code}`,
    '股利':`https://www.wantgoo.com/stock/etf/${code}/dividend-policy/ex-dividend`,
    'CMoney':`https://www.cmoney.tw/forum/stock/${code}`,
    '玩股網':`https://www.wantgoo.com/stock/${code}`,
    '鉅亨網':`https://www.cnyes.com/twstock/${code}`,
    '整合資訊':`https://www.twse.com.tw/pdf/ch/${code}_ch.pdf`,
  };
  const dict_etf = {
    '持股':`https://www.cmoney.tw/forum/stock/${code}?s=constituent`,
    '新聞':`https://tw.stock.yahoo.com/q/h?s=${code}`,
    'Ｋ線':`chart.html?c=${code}`,
    '股利':`https://www.wantgoo.com/stock/etf/${code}/dividend-policy/ex-dividend`,
    'CMoney':`https://www.cmoney.tw/forum/stock/${code}`,
    '玩股網':`https://www.wantgoo.com/stock/${code}`,
    '鉅亨網':`https://www.cnyes.com/twstock/${code}`,
  };

  var text = '';
  if (obj.pz && obj.nav)
    text += `<span class="title">${code} ${obj.name} (${obj.pz}, 淨值 ${obj.nav})</span><br>`;
  else
    text += `<span class="title">${code} ${obj.name}</span><br>`;

  for (const [name, link] of Object.entries(code.startsWith('00') ? dict_etf : dict)) {
    text += `<span class="link"><a href="${link}" target="_blank">${name}</a></span>`;
  }

  $('title').html(`${code} ${obj.name}`);
  $('#info').html(text);
}

function updateQuote(obj) {
  let text = `<img src="loadpng.py?c=${obj.code}">`;
  $('#quote').html(text);
}

function updateChart(id, dp_data) {
  var chart = new CanvasJS.Chart(id, {
    title: {
      text: id
    },
    theme: "light2",
    toolTip: {
      borderThickness: 0,
      cornerRadius: 0
    },
    axisX: {
      labelFontSize: 14,
      crosshair: {
        enabled: true,
        snapToDataPoint: true
      }
    },
    axisY: {
      gridThickness: 0,
      labelFontSize: 14,
      lineThickness: 2,
      crosshair: {
        enabled: true,
        snapToDataPoint: true
      }
    },
    data: [
      {
        type: "spline",
        dataPoints: dp_data
      }
    ]
  });

  chart.render();
}

function updateEPSChart(obj) {

  if (!obj.eps.length) {
    $('#EPS').hide();
    return;
  }

  var dp_data = [];

  for (let d of obj.eps) {
    let date = `${d.Y}-${d.Q * 3}-1`;
    dp_data.push({x: new Date(date), y: Number(d.eps)});
  }

  updateChart('EPS', dp_data);
}

function updateRevenueChart(obj) {

  if (!obj.revenue.length) {
    $('#Revenue').hide();
    return
  }

  var dp_data = [];

  for (let d of obj.revenue) {
    let date = `${d.Y}-${d.M}-1`;
    dp_data.push({x: new Date(date), y: Number(d.rev)});
  }

  updateChart('Revenue', dp_data);
}

function updateResult(obj) {

  if (!obj.per_year.length)
    return;

  var text = '';

  const pz = obj.close;
  const eps = pz / obj.per;
  const kv_list0 = [
    ['年度', obj.per_year],
    ['最高本益比', obj.per_max],
    ['最低本益比', obj.per_min],
    ['現金股利', obj.dividend_cash],
    ['股票股利', obj.dividend_stock]
  ];

  text += '<table>';
  for (const [k, v] of kv_list0)
    text += '<tr><td>' + k + '</td><td>' + v.join('</td><td>') + '</td></tr>';
  text += '</table>';

  const kv_list1 = [
    ['收盤價', pz],
    ['淨值', obj.nav],
    ['股數(億)', obj.capital_stock / 10],
    ['股價淨值比', pz / obj.nav],
    ['股東權益報酬率ROE', eps / obj.nav * 100],
    ['負債比例', obj.debt_ratio * 100],
    ['本益比', obj.per],
    ['EPS', eps]
  ];

  text += '<table>';
  for (const [k, v] of kv_list1)
    text += '<tr><td>' + k + '</td><td>' + v.toFixed(2) + '</td></tr>';
  text += '</table>'

  $('#result').html(text);
}

function parseJSON(obj) {
  console.log(obj);
  updateInfo(obj);
  updateQuote(obj);
  updateEPSChart(obj);
  updateRevenueChart(obj);
  updateResult(obj);
}

function updateStockReport() {
  var params = (new URL(window.location)).searchParams;
  var code = params.get('c');
  $.ajax({
    url: `load.py?n=report&c=${code}`,
    dataType: 'json',
    success: parseJSON,
  });
}

function updateReportByInput() {
  var code = document.getElementById('input_code').value;
  if (code != '')
    window.location.href = 'report.html?c=' + code;
}

function onDocumentReady() {
  loadTopMenu();
  if (window.location.search != '') {
    updateStockReport();
  }
}

