
String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

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

  var text = '';
  text += String.format('<span class="title">{0} {1} (${2})</span><br>', code, obj.name, obj.close);

  for (const [name, link] of Object.entries(dict)) {
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

  text += String.format('<table><tr><th colspan={0}>本益比</th></tr>', obj.per_year.length + 1);

  text += '<tr><td>年度</td>';
  for (let year of obj.per_year)
    text += String.format('<td>{0}</td>', year);
  text += '</tr>';

  text += '<tr><td>最高本益比</td>';
  for (let per_max of obj.per_max)
    text += String.format('<td>{0}</td>', per_max);
  text += '</tr>';

  text += '<tr><td>最低本益比</td>';
  for (let per_min of obj.per_min)
    text += String.format('<td>{0}</td>', per_min);
  text += '</tr>';

  text += '<tr><td>現金股利</td>';
  for (let cash of obj.dividend_cash)
    text += String.format('<td>{0}</td>', cash);
  text += '</tr>';

  text += '<tr><td>股票股利</td>';
  for (let stock of obj.dividend_stock)
    text += String.format('<td>{0}</td>', stock);
  text += '</tr>';

  text += '</table><br>';

  const last_dividend_cash = obj.dividend_cash.slice(1, Math.min(obj.dividend_cash.length, 6));
  const last_dividend_stock = obj.dividend_stock.slice(1, Math.min(obj.dividend_stock.length, 6));
  const last_dividend_cash_sum = last_dividend_cash.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
  const last_dividend_cash_avg = last_dividend_cash_sum / last_dividend_cash.length;
  const last_dividend_stock_sum = last_dividend_stock.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
  const last_dividend_stock_avg = last_dividend_stock_sum / last_dividend_stock.length;
  const last_dividend_avg = last_dividend_cash_avg + last_dividend_stock_avg;

  var per_max_total_weight = 0;
  var per_max_total_sum = 0;
  var per_min_total_weight = 0;
  var per_min_total_sum = 0;

  for (let i in obj.per_max) {
    if (obj.per_max[i] > 0)
    {
      let weight = Math.pow(0.67, i);
      per_max_total_sum += weight * obj.per_max[i];
      per_max_total_weight += weight;
    }
  }

  for (let i in obj.per_min) {
    if (obj.per_min[i] > 0)
    {
      let weight = Math.pow(0.67, i);
      per_min_total_sum += weight * obj.per_min[i];
      per_min_total_weight += weight;
    }
  }

  var pz = obj.close;
  var eps = pz / obj.per;
  var per_max = per_max_total_sum / per_max_total_weight;
  var per_min = per_min_total_sum / per_min_total_weight;

  if (obj.per_max[0] > 0)
    per_max = Math.min(obj.per_max[0], per_max)

  if (obj.per_min[0] > 0)
    per_min = Math.min(obj.per_min[0], per_min)

  var pz_max = eps * per_max;
  var pz_min = eps * per_min;
  var pz_mid = (pz_max + pz_min) / 2;

  text += '<table><tr><th colspan=3>Overall</th></tr>';

  text += String.format('<tr><td colspan=2></td><td rowspan=9>');
  text += String.format('推估PER：{0} ~ {1}<br>', per_min.toFixed(2), per_max.toFixed(2));
  text += String.format('推估最低價：{0}<br>', pz_min.toFixed(2));
  text += String.format('推估中間價：{0}<br>', pz_mid.toFixed(2));
  text += String.format('推估最高價：{0}<br>', pz_max.toFixed(2));
  text += String.format('近期股利：{0}<br>', last_dividend_avg.toFixed(2));
  text += String.format('近期殖利率：{0}%<br>', (last_dividend_avg / pz * 100).toFixed(2));
  text += String.format('</td></tr>', pz_min.toFixed(2));

  text += String.format('<tr><td>收盤價</td><td>{0}</td></tr>', pz.toFixed(2));
  text += String.format('<tr><td>淨值 (NAV)</td><td>{0}</td></tr>', obj.nav.toFixed(2));
  text += String.format('<tr><td>股數(億)</td><td>{0}</td></tr>', (obj.capital_stock / 10).toFixed(2));
  text += String.format('<tr><td>股價淨值比  (PBR)</td><td>{0}</td></tr>', (pz / obj.nav).toFixed(2));
  text += String.format('<tr><td>股東權益報酬率 (ROE)</td><td>{0}%</td></tr>', (eps / obj.nav * 100).toFixed(2));
  text += String.format('<tr><td>負債比例</td><td>{0}%</td></tr>', (obj.debt_ratio * 100).toFixed(2));
  text += String.format('<tr><td>本益比 (PER)</td><td>{0}</td></tr>', obj.per.toFixed(2));
  text += String.format('<tr><td>EPS</td><td>{0}</td></tr>', eps.toFixed(2));

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
    url: 'report.py' + window.location.search,
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

