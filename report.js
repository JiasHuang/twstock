
// Chart Globals Settings
Chart.defaults.global.animation.duration = 0;
Chart.defaults.global.hover.animationDuration = 0;
Chart.defaults.global.hover.responsiveAnimationDuration = 0;
Chart.defaults.global.title.display = true;
Chart.defaults.global.title.fontSize = 16;
Chart.defaults.global.events = ['click'];


String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function getBiasText(pz, ma) {
  var chg = pz - ma;
  var ratio = chg / ma * 100;
  return String.format('{0} ({1}, {2}%)', pz.toFixed(2), chg.toFixed(2), ratio.toFixed(2));
}

function parseWAPByYear(wap, Y) {
  var hi = null;
  var lo = null;
  var a_hi = null;
  var a_lo = null;
  var total_A = 0;
  var total_B = 0;
  var year_wap = 0;

  for (var i=0; i<wap.length; i++) {
    if (wap[i][0] == Y) {
      let h = parseFloat(wap[i][2]);
      let l = parseFloat(wap[i][3]);
      let a = parseFloat(wap[i][4]);
      let A = parseFloat(wap[i][5]);
      let B = parseFloat(wap[i][6]);

      if (!hi || h > hi) {
        hi = h;
      }
      if (!lo || l < lo) {
        lo = l;
      }
      if (!a_hi || a > a_hi) {
        a_hi = a;
      }
      if (!a_lo || a < a_lo) {
        a_lo = a;
      }

      total_A += A;
      total_B += B;
    }
  }

  year_wap = total_A / total_B;

  return [hi, lo, year_wap, a_hi, a_lo];
}

function getWAPHTMLText(wap, z) {
  var text = '';
  var Y = null;
  var parsed = null;

  text += '<table>';

  for (var i=0; i<wap.length; i++) {
    if (Y != wap[i][0]) {
      Y = wap[i][0];
      text += '</table><table>';
      text += '<tr><th>年</th><th>月</th><th>最高</th><th>最低</th><th>平均</th><th></th></tr>';
      parsed = parseWAPByYear(wap, Y);
      let note = '';
      note += String.format('最高：{0}<br>', getBiasText(parsed[0], z));
      note += String.format('最低：{0}<br>', getBiasText(parsed[1], z));
      note += String.format('平均：{0}<br>', getBiasText(parsed[2], z));
      //note += String.format('月均最高：{0}<br>', getBiasText(parsed[3], z));
      //note += String.format('月均最低：{0}<br>', getBiasText(parsed[4], z));
      text += '<tr><td colspan=5></td><td rowspan=13>' + note + '</td></tr>';
    }
    let c1 = (wap[i][2] == parsed[0]) ? 'red' : '';
    let c2 = (wap[i][3] == parsed[1]) ? 'green' : '';
    let c3 = (wap[i][4] == parsed[3]) ? 'red' : ((wap[i][4] == parsed[4]) ? 'green' : '');
    text += String.format('<tr><td>{0}</td><td>{1}</td><td><span class={2}>{3}</span></td><td><span class={4}>{5}</span></td><td><span class={6}>{7}</span></td></tr>',
      wap[i][0], wap[i][1], c1, wap[i][2], c2, wap[i][3], c3, wap[i][4]);
  }

  for (var i=0; i<(12-wap[wap.length-1][1]); i++) {
    text += '<tr>' + '<td>-</td>'.repeat(5) + '</tr>';
  }

  text += '</table><br>';

  return text;
}

function getMAs(obj) {
  var MAs = [];
  for (var i=0; i<obj.length; i++) {
    MAs.push(obj[i][4]);
  }
  return MAs;
}

function updateInfo(obj) {
  var text = '';

  text += String.format('<span class="title">{0} {1} (${2})</span>', obj.code, obj.n, obj.z);

  text += String.format('<span class="link"><a href="https://fubon-ebrokerdj.fbs.com.tw/z/zc/zca/zca_{0}.djhtm" target="_blank">基本</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_{0}.djhtm" target="_blank">營收</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://fubon-ebrokerdj.fbs.com.tw/Z/ZC/ZCV/ZCV_{0}.djhtm" target="_blank">訊息</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcw/zcw_{0}.djhtm" target="_blank">Ｋ線</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcw/zcwg/zcwg_{0}.djhtm" target="_blank">分價</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://goodinfo.tw/StockInfo/StockFinDetail.asp?RPT_CAT=IS_M_QUAR_ACC&STOCK_ID={0}" target="_blank">損益</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={0}" target="_blank">GoodInfo</a></span>', obj.code);
  text += String.format('<span class="link"><a href="https://www.moneydj.com/KMDJ/search/searchHome.aspx?_Query_={0}&_QueryType_=Main" target="_blank">MoneyDJ</a></span>', obj.nf);
  text += String.format('<span class="link"><a href="https://www.twse.com.tw/pdf/ch/{0}_ch.pdf" target="_blank">整合資訊</a></span>', obj.code);

  $('title').html(obj.n);
  $('#info').html(text);
}

function updateNews(news) {
  var text = '';

  if (news.length) {
    text += '<hr>';
    for (var i=0; i<news.length; i++) {
      text += String.format('<span class="news"><a href="{0}" target="_blank">{1} {2}</a></span>', news[i][2], news[i][0], news[i][1]);
    }
  }

  $('#news').html(text);
}

function updateMAChart(wap) {
  var ctx = document.getElementById('chart_MA').getContext('2d');
  var labels = [];
  var data = [];
  var datasets = [];

  for (var i=0; i<wap.length; i++) {
    labels.push(wap[i][0] + '/' + wap[i][1]);
    data.push(wap[i][4]);
  }

  datasets.push({
    label: 'MA',
    data: data,
    borderColor: 'DarkBlue',
    backgroundColor: 'DarkBlue',
    fill: false,
  });

  var lineChart = new Chart(ctx, {
    type: 'line',
    options: {
      title: {
        text: '月均線'
      }
    },
    data: {
      labels:labels,
      datasets: datasets,
    }
  });
}

function getWAPsByYear(wap, Y) {
  var ret = [];
  for (var i=0; i<wap.length; i++) {
    if (wap[i][0] == Y) {
      ret.push({x: wap[i][1], y: wap[i][4]});
    }
  }
  return ret;
}

function updateMAChartByYear(wap) {
  var ctx = document.getElementById('chart_MA_by_year').getContext('2d');
  var datasets = [];
  var labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
  var colors = ['Grey', 'SteelBlue', 'Blue'];
  var colors_idx = 0;
  var Y = null;

  for (var i=0; i<wap.length; i++) {
    if (Y != wap[i][0]) {
      Y = wap[i][0];
      datasets.push({
        label: Y,
        data: getWAPsByYear(wap, Y),
        borderColor: colors[colors_idx],
        backgroundColor: colors[colors_idx],
        fill: false,
      });
      colors_idx++;
    }
  }

  var lineChart = new Chart(ctx, {
    type: 'line',
    options: {
      title: {
        text: '年度月均線',
      }
    },
    data: {
      labels:labels,
      datasets: datasets,
    }
  });

}

function getEPSsByYear(eps, Y, cumulative) {
  var ret = [];
  var accu = 0;
  var val = 0;

  for (var i=0; i<eps.length; i++) {
    if (eps[i][0] != Y) {
      continue;
    }
    let x = 'Q' + eps[i][1];
    val = parseFloat(eps[i][3]); // After Tax
    if (cumulative) {
      accu += val;
      ret.push({x: x, y: accu.toFixed(2)});
    }
    else {
      ret.push({x: x, y: val});
    }
  }
  return ret;
}

function updateEPSChart(eps, cumulative) {
  var ctx = document.getElementById(cumulative ? 'chart_cumulative_EPS' : 'chart_EPS').getContext('2d');
  var datasets = [];
  var labels = ['Q1','Q2','Q3','Q4'];
  var colors = ['Grey', 'SteelBlue', 'Blue'];
  var colors_idx = 0;
  var Y = null;

  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i][0]) {
      Y = eps[i][0];
      datasets.push({
        label: Y,
        data: getEPSsByYear(eps, Y, cumulative),
        borderColor: colors[colors_idx],
        backgroundColor: colors[colors_idx],
        fill: false,
      });
      colors_idx++;
    }
  }

  var lineChart = new Chart(ctx, {
    type: 'line',
    options: {
      title: {
        text: cumulative ? '年度累季EPS' : '年度單季EPS',
      }
    },
    data: {
      labels:labels,
      datasets: datasets,
    }
  });
}

function getRevenueByYear(rev, Y, cumulative) {
  var ret = [];
  var accu = 0;
  var val = 0;

  for (var i=0; i<rev.length; i++) {
    if (rev[i][0] != Y) {
      continue;
    }
    val = parseFloat(rev[i][2] / 100000); //單位：1億
    if (cumulative) {
      accu += val;
      ret.push({x: rev[i][1], y: accu});
    }
    else {
      ret.push({x: rev[i][1], y: val});
    }
  }
  return ret;
}

function updateRevenueChart(rev, cumulative) {
  var ctx = document.getElementById(cumulative ? 'chart_cumulative_revenue' : 'chart_revenue').getContext('2d');
  var datasets = [];
  var labels = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
  var colors = ['Grey', 'SteelBlue', 'Blue'];
  var colors_idx = 0;
  var Y = null;

  for (var i=0; i<rev.length; i++) {
    if (Y != rev[i][0]) {
      Y = rev[i][0];
      datasets.push({
        label: Y,
        data: getRevenueByYear(rev, Y, cumulative),
        borderColor: colors[colors_idx],
        backgroundColor: colors[colors_idx],
        fill: false,
      });
      colors_idx++;
    }
  }

  var lineChart = new Chart(ctx, {
    type: 'line',
    options: {
      title: {
        text: cumulative ? '年度累月營收（單位：億）' : '年度單月營收（單位：億）',
      }
    },
    data: {
      labels:labels,
      datasets: datasets,
    }
  });
}

function getEPSHTMLText(obj) {
  var text = '';
  var Y = null;
  var eps = obj.eps;

  text += '<table>';

  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i][0]) {
        Y = eps[i][0];
        text += '</table><table>';
        text += '<tr><th>年</th><th>季</th><th>稅前EPS</th><th>稅後EPS</th><th></th></tr>';
        let note = '';
        let cumulative_eps = getEPSsByYear(eps, Y, true);
        let year_eps = cumulative_eps[cumulative_eps.length - 1].y;
        let year_wap = parseWAPByYear(obj.wap, Y)[2].toFixed(2);
        note += String.format('累季EPS：{0}<br>', year_eps);
        if (cumulative_eps.length == 4) {
          note += String.format('年度均價：{0}<br>', year_wap);
          note += String.format('本益比：{0}<br>', (year_wap / year_eps).toFixed(2));
          note += String.format('收益率：{0}%<br>', (year_eps / year_wap * 100).toFixed(2));
        }
        else {
          let last4Q_eps = 0;
          for (var j=0; j<4; j++) {
            last4Q_eps += parseFloat(eps[eps.length-1-j][3]); // After Tax
          }
          note += String.format('近四季累計EPS：{0}<br>', last4Q_eps.toFixed(2));
          let price_to_earning = (obj.z / last4Q_eps).toLocaleString();
          let earning_yield = (last4Q_eps / obj.z * 100).toLocaleString();
          note += String.format('近四季本益比：{0}<br>', price_to_earning);
          note += String.format('近四季收益率：{0}%<br>', earning_yield);
        }
        text += '<tr><td colspan=4></td><td rowspan=5>' + note + '</td></tr>';
    }
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>',
      eps[i][0], eps[i][1], eps[i][2], eps[i][3]);
  }

  for (var i=0; i<(4-eps[eps.length-1][1]); i++) {
    text += '<tr>' + '<td>-</td>'.repeat(4) + '</tr>';
  }

  text += '</table><br>';

  return text;
}

function getDividendHTMLText(obj) {
  var text = '';
  var div = obj.dividend;

  text += '<table>';
  text += '<tr><th rowspan=2>股利所屬年度</th><th colspan=3>現金股利</th><th colspan=3>股票股利</th><th rowspan=2>現金殖利率</th></tr>';
  text += '<tr><th class=tbl_title>盈餘</th><th class=tbl_title>公積</th><th class=tbl_title>合計</th><th class=tbl_title>盈餘</th><th class=tbl_title>公積</th><th class=tbl_title>合計</th></tr>';

  for (var i=0; i<div.length; i++) {
    let d = div[i];
    let cash_dividend = (parseFloat(d[1]) + parseFloat(d[2])).toFixed(2);
    let stock_dividend = (parseFloat(d[3]) + parseFloat(d[4])).toFixed(2);
    let dividend_yield = (cash_dividend / obj.z * 100).toLocaleString();
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}%</td></tr>',
      d[0], d[1], d[2], cash_dividend, d[3], d[4], stock_dividend, dividend_yield);
  }

  text += '</table><br>';

  return text;
}

function getTopPricesHTMLText(obj) {
  var text = '';
  var pairs = obj.pz_vol_pairs;

  text += '<table><tr><th colspan=6>近期分價統計</th></tr>';

  text += '<tr><th>最低5檔</th>';
  for (var i=0; i<5; i++) {
    text += String.format('<td>${0} <span class="grey">#{1}</span></td>', pairs[i][0], pairs[i][1]);
  }

  pairs.reverse();
  text += '<tr><th>最高5檔</th>';
  for (var i=0; i<5; i++) {
    text += String.format('<td>${0} <span class="grey">#{1}</span></td>', pairs[i][0], pairs[i][1]);
  }

  pairs.sort(function (a, b) {
    if (a[1] < b[1]) return 1;
    if (a[1] > b[1]) return -1;
    return 0;
  });

  text += '<tr><th>最多5檔</th>';
  for (var i=0; i<5; i++) {
    text += String.format('<td>${0} <span class="grey">#{1}</span></td>', pairs[i][0], pairs[i][1]);
  }

  text += '</table>';

  return text;
}

function updateResult(obj) {
  var text = '';

  text += getWAPHTMLText(obj.wap, obj.z);
  if (obj.eps.length) {
    text += getEPSHTMLText(obj);
  }
  text += getDividendHTMLText(obj);
  text += getTopPricesHTMLText(obj);

  $('#result').html(text);
}

function parseJSON(obj) {
  console.log(obj);
  updateInfo(obj);
  updateNews(obj.news);
  updateResult(obj);
  updateMAChart(obj.wap);
  updateMAChartByYear(obj.wap);
  if (obj.eps.length) {
    updateEPSChart(obj.eps, true);
    updateEPSChart(obj.eps, false);
  }
  else {
    $('#cumulative_eps').hide();
    $('#eps').hide();
  }
  if (obj.revenue.length) {
    updateRevenueChart(obj.revenue, true);
    updateRevenueChart(obj.revenue, false);
  }
  else {
    $('#cumulative_revenue').hide();
    $('#revenue').hide();
  }
}

function onTimeout () {
  console.log('timeout');
}

function showLoading() {
  $('#info').html('<span class=title>Loading ...</span>');
}

function updateStockReport() {
  showLoading();
  $.ajax({
    url: 'report.py' + window.location.search,
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 20000
  });
}

function updateReportByInput() {
  showLoading();
  $.ajax({
    url: 'report.py?c=' + document.getElementById('input_code').value,
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 20000
  });
}

function onDocumentReady() {
  if (window.location.search != '') {
    updateStockReport();
  }
}

