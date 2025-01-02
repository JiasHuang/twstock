
// Chart Globals Settings
Chart.defaults.global.animation.duration = 0;
Chart.defaults.global.hover.animationDuration = 0;
Chart.defaults.global.hover.responsiveAnimationDuration = 0;
Chart.defaults.global.title.display = true;
Chart.defaults.global.title.fontSize = 16;
Chart.defaults.global.events = ['click'];

var colors = ['DarkGrey', 'Grey', '#95B9C7', '#659EC7', '#157DEC', 'Blue'];
var def_color = colors[colors.length - 1];

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function init_colors_idx(vec)
{
  var Y = null;
  var cnt = 0;
  for (var i=0; i<vec.length; i++) {
    if (Y != vec[i].Y) {
      Y = vec[i].Y;
      cnt++;
    }
  }

  return Math.max(0, colors.length - cnt);
}

function getBiasText(pz, ma) {
  var chg = pz - ma;
  var ratio = chg / ma * 100;
  return String.format('{0} ({1}, {2}%)', pz.toFixed(2), chg.toFixed(2), ratio.toFixed(2));
}

function parseWAPByYear(wap, Y) {
  var hi = 0;
  var lo = 0;
  var year_wap = 0;
  var a_hi = 0;
  var a_lo = 0;
  var total_A = 0;
  var total_B = 0;

  for (var i=0; i<wap.length; i++) {
    if (wap[i].Y == Y) {
      let h = parseFloat(wap[i].h);
      let l = parseFloat(wap[i].l);
      let a = parseFloat(wap[i].a);
      let A = parseFloat(wap[i].A);
      let B = parseFloat(wap[i].B);

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

  if (total_A && total_B) {
    year_wap = total_A / total_B;
  }

  return [hi, lo, year_wap, a_hi, a_lo];
}

function getWAPHTMLText(wap, z) {
  var text = '';
  var Y = null;
  var parsed = null;

  if (!wap.length) {
    return '';
  }

  text += '<table>';

  for (var i=0; i<wap.length; i++) {
    if (Y != wap[i].Y) {
      Y = wap[i].Y;
      text += '</table><table>';
      text += '<tr><th>年</th><th>月</th><th>最高</th><th>最低</th><th>平均</th><th></th></tr>';
      parsed = parseWAPByYear(wap, Y);
      let note = '';
      note += String.format('最高：{0}<br>', getBiasText(parsed[0], z));
      note += String.format('最低：{0}<br>', getBiasText(parsed[1], z));
      note += String.format('平均：{0}<br>', getBiasText(parsed[2], z));
      text += '<tr><td colspan=5></td><td rowspan=13>' + note + '</td></tr>';
      for (var m=1; m<wap[i].M; m++) {
        text += '<tr>' + '<td>-</td>'.repeat(5) + '</tr>';
      }
    }
    let c1 = (wap[i].h == parsed[0]) ? 'red' : '';
    let c2 = (wap[i].l == parsed[1]) ? 'green' : '';
    let c3 = (wap[i].a == parsed[3]) ? 'red' : ((wap[i].a == parsed[4]) ? 'green' : '');
    text += String.format('<tr><td>{0}</td><td>{1}</td><td><span class={2}>{3}</span></td><td><span class={4}>{5}</span></td><td><span class={6}>{7}</span></td></tr>',
      wap[i].Y, wap[i].M, c1, wap[i].h, c2, wap[i].l, c3, wap[i].a);
  }

  for (var i=0; i<(12-wap[wap.length-1].M); i++) {
    text += '<tr>' + '<td>-</td>'.repeat(5) + '</tr>';
  }

  text += '</table><br>';

  return text;
}

function getLinkDict(code, nf) {
  var dict = [];
  dict.push({key:'基本', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zca/zca_{0}.djhtm', code)});
  dict.push({key:'獲利', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zce/zce_{0}.djhtm', code)});
  dict.push({key:'財務', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr0.djhtm?b=Y&a={0}', code)});
  dict.push({key:'資產', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_{0}.djhtm', code)});
  dict.push({key:'損益', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_{0}.djhtm', code)});
  dict.push({key:'營收', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_{0}.djhtm', code)});
  dict.push({key:'新聞', val:String.format('https://tw.stock.yahoo.com/q/h?s={0}', code)});
  dict.push({key:'Ｋ線', val:String.format('https://tw.stock.yahoo.com/quote/{0}.TWO/technical-analysis', code)});
  dict.push({key:'股利', val:String.format('https://www.wantgoo.com/stock/etf/{0}/dividend-policy/ex-dividend', code)});
  dict.push({key:'CMoney', val:String.format('https://www.cmoney.tw/forum/stock/{0}', code)});
  dict.push({key:'公開資訊', val:String.format('https://mops.twse.com.tw/mops/web/t146sb05?step=1&firstin=true&co_id={0}', code)});
  dict.push({key:'整合資訊', val:String.format('https://www.twse.com.tw/pdf/ch/{0}_ch.pdf', code)});
  return dict;
}

function updateInfo(obj) {
  var text = '';
  var dict = getLinkDict(obj.code, obj.nf);

  text += String.format('<span class="title">{0} {1} (${2})</span><br>', obj.code, obj.n, obj.z);

  for (var i=0; i<dict.length; i++) {
    text += String.format('<span class="link"><a href="{0}" target="_blank">{1}</a></span>', dict[i].val, dict[i].key);
  }

  text += '<span class="link"><a href="#result">#Result</a></span>';

  $('title').html(String.format('{0} {1} (${2})', obj.code, obj.n, obj.z));
  $('#info').html(text);
}

function updateMAChart(wap) {
  var ctx = document.getElementById('chart_MA').getContext('2d');
  var labels = [];
  var data = [];
  var datasets = [];

  for (var i=0; i<wap.length; i++) {
    labels.push(wap[i].Y + '/' + wap[i].M);
    data.push(wap[i].a.replaceAll(',', ''));
  }

  datasets.push({
    label: 'MA',
    data: data,
    borderColor: def_color,
    backgroundColor: def_color,
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
    if (wap[i].Y == Y) {
      ret.push({x: wap[i].M.toString(), y: wap[i].a.replaceAll(',', '')});
    }
  }
  return ret;
}

function updateMAChartByYear(wap) {
  var ctx = document.getElementById('chart_MA_by_year').getContext('2d');
  var datasets = [];
  var labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
  var colors_idx = init_colors_idx(wap);
  var Y = null;

  for (var i=0; i<wap.length; i++) {
    if (Y != wap[i].Y) {
      Y = wap[i].Y;
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
    if (eps[i].Y != Y) {
      continue;
    }
    let x = 'Q' + eps[i].Q;
    val = parseFloat(eps[i].eps);
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

function getProfitMarginByYear(eps, Y) {
  var ret = [];

  for (var i=0; i<eps.length; i++) {
    if (eps[i].Y != Y) {
      continue;
    }
    let x = 'Q' + eps[i].Q;
    let rev = parseFloat(eps[i].rev.replaceAll(',', ''));
    let net_profit = parseFloat(eps[i].profit.replaceAll(',', ''));
    let profit_margin = net_profit / rev * 100;
    ret.push({x: x, y: profit_margin.toFixed(2)});
  }

  return ret;
}

function updateEPSChart(eps, cumulative) {
  var ctx = document.getElementById(cumulative ? 'chart_cumulative_EPS' : 'chart_EPS').getContext('2d');
  var datasets = [];
  var labels = ['Q1','Q2','Q3','Q4'];
  var colors_idx = init_colors_idx(eps);
  var Y = null;

  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i].Y) {
      Y = eps[i].Y;
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

function updateProfitMarginChart(eps) {
  var ctx = document.getElementById('chart_profit_margin').getContext('2d');
  var datasets = [];
  var data = [];
  var labels = [];

  for (var i=0; i<eps.length; i++) {
    let rev = parseFloat(eps[i].rev.replaceAll(',', ''));
    let net_profit = parseFloat(eps[i].profit.replaceAll(',', ''));
    let profit_margin = net_profit / rev * 100;
    data.push(profit_margin.toFixed(2));
    labels.push(eps[i].Y + 'Q' + eps[i].Q);
  }

  datasets.push({
    label: 'ProfitMargin',
    data: data,
    borderColor: def_color,
    backgroundColor: def_color,
    fill: false,
  });

  var lineChart = new Chart(ctx, {
    type: 'line',
    options: {
      title: {
        text: '營益率',
      }
    },
    data: {
      labels:labels,
      datasets: datasets,
    }
  });
}

function updateProfitMarginChartByYear(eps) {
  var ctx = document.getElementById('chart_profit_margin_by_year').getContext('2d');
  var datasets = [];
  var labels = ['Q1','Q2','Q3','Q4'];
  var colors_idx = init_colors_idx(eps);
  var Y = null;

  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i].Y) {
      Y = eps[i].Y;
      datasets.push({
        label: Y,
        data: getProfitMarginByYear(eps, Y),
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
        text: '年度單季營益率',
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
    if (rev[i].Y != Y) {
      continue;
    }
    val = parseFloat(rev[i].rev) / 100000; //單位：1億
    if (cumulative) {
      accu += val;
      ret.push({x: rev[i].M, y: accu});
    }
    else {
      ret.push({x: rev[i].M, y: val});
    }
  }
  return ret;
}

function getRevenueByYearQ(rev, Y, Q) {
  var vol = 0;
  var months = 0;

  for (var i=0; i<rev.length; i++) {
    if (rev[i].Y != Y) {
      continue;
    }
    if (Math.ceil(parseInt(rev[i].M) / 3) != Q) {
      continue;
    }
    vol += parseFloat(rev[i].rev) / 100000; //單位：仟->億
    months += 1;
  }

  return {vol:vol, months:months};
}

function updateRevenueChart(rev, cumulative) {
  var ctx = document.getElementById(cumulative ? 'chart_cumulative_revenue' : 'chart_revenue').getContext('2d');
  var datasets = [];
  var labels = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
  var colors_idx = init_colors_idx(rev);
  var Y = null;

  for (var i=0; i<rev.length; i++) {
    if (Y != rev[i].Y) {
      Y = rev[i].Y;
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

  // 單位：千股 / 百萬元
  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i].Y) {
        Y = eps[i].Y;
        text += '<tr><th>年</th><th>季</th><th>營收(億)</th><th>營利(億)</th><th>營益率(%)</th><th>業外(億)</th><th>本業(%)</th><th>稅後淨利(億)</th><th>EPS</th><th></th></tr>';
        let note = '';
        let cumulative_eps = getEPSsByYear(eps, Y, true);
        let year_eps = cumulative_eps[cumulative_eps.length - 1].y;
        let year_wap = parseWAPByYear(obj.wap, Y)[2].toFixed(2);
        if (i <= eps.length - 4) {
          let parsed = parseWAPByYear(obj.wap, Y);
          let year_wap = '-';
          let year_price_to_earning = '-';
          if (parsed[2]) {
            year_wap = parsed[2].toFixed(2);
            year_price_to_earning = (year_wap / year_eps).toFixed(2);
          }
          note += String.format('年度EPS：{0}<br>', year_eps);
          note += String.format('年度均價：{0}<br>', year_wap);
          note += String.format('本益比：{0}<br>', year_price_to_earning);
        }
        else if (eps.length >= 4) {
          let last4Q_eps = 0;
          for (var j=0; j<4; j++) {
            last4Q_eps += parseFloat(eps[eps.length-1-j].eps);
          }
          let price_to_earning = (obj.z / last4Q_eps).toFixed(2);
          let earning_yield = (last4Q_eps / obj.z * 100).toFixed(2);
          note += String.format('近四季EPS：{0} (累季：{1})<br>', last4Q_eps.toFixed(2), year_eps);
          note += String.format('目前股價：{0}<br>', obj.z);
          note += String.format('近四季本益比：{0}<br>', price_to_earning);
        }
        text += '<tr><td colspan=9></td><td rowspan=5>' + note + '</td></tr>';
        for (var q=1; q<eps[i][1]; q++) {
          text += '<tr>' + '<td>-</td>'.repeat(9) + '</tr>';
        }
    }
    let rev = parseFloat(eps[i].rev.replaceAll(',', ''));
    let profit = parseFloat(eps[i].profit.replaceAll(',', ''));
    let profit_ratio = profit / rev * 100; // operating profit ratio / Operating profit Margin
    let nor = parseFloat(eps[i].nor.replaceAll(',', '')); // Total Non-operating Revenue
    let profit_rate = (profit >= 0 && nor >=0) ? (profit / (profit + nor) * 100).toFixed(2) : '-';
    let ni = parseFloat(eps[i].ni.replaceAll(',', '')); // Net Income
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td></tr>',
      eps[i].Y, eps[i].Q, (rev / 100).toFixed(2), (profit / 100).toFixed(2), profit_ratio.toFixed(2), (nor / 100).toFixed(2), profit_rate, (ni / 100).toFixed(2), eps[i].eps);
  }

  for (var Q=parseInt(eps[eps.length-1].Q)+1; Q<=4; Q++) {
    let rev = getRevenueByYearQ(obj.revenue, Y, Q);
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td>{3}</tr>',
      Y, Q, rev.vol.toFixed(2), '<td>-</td>'.repeat(6));
  }

  text += '</table><br>';

  return text;
}

function getOverallHTMLText(obj) {
  var text = '';

  text += String.format('<table><tr><th colspan={0}>Overall</th></tr>', obj.per_year.length + 1);

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

  for (let i in  obj.per_max) {
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

  var pz = obj.pz_close;
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

  text += String.format('<tr><td colspan=2></td><td rowspan=8>');
  text += String.format('推估PER：{0} ~ {1}<br>', per_min.toFixed(2), per_max.toFixed(2));
  text += String.format('推估最低價：{0}<br>', pz_min.toFixed(2));
  text += String.format('推估中間價：{0}<br>', pz_mid.toFixed(2));
  text += String.format('推估最高價：{0}<br>', pz_max.toFixed(2));
  text += String.format('近期股利：{0}<br>', last_dividend_avg.toFixed(2));
  text += String.format('近期殖利率：{0}%<br>', (last_dividend_avg / pz * 100).toFixed(2));
  text += String.format('近期殖利率股價：[7%, 5%, 3%] = [{0}, {1}, {2}]<br>', (last_dividend_avg / 0.07).toFixed(2), (last_dividend_avg / 0.05).toFixed(2), (last_dividend_avg / 0.03).toFixed(2));
  text += String.format('</td></tr>', pz_min.toFixed(2));

  text += String.format('<tr><td>收盤價</td><td>{0}</td></tr>', pz.toFixed(2));
  text += String.format('<tr><td>淨值 (NAV)</td><td>{0}</td></tr>', obj.nav.toFixed(2));
  text += String.format('<tr><td>股數(億)</td><td>{0}</td></tr>', (obj.capital_stock / 10).toFixed(2));
  text += String.format('<tr><td>股價淨值比	(PBR)</td><td>{0}</td></tr>', (pz / obj.nav).toFixed(2));
  text += String.format('<tr><td>股東權益報酬率 (ROE)</td><td>{0}%</td></tr>', (eps / obj.nav * 100).toFixed(2));
  text += String.format('<tr><td>本益比 (PER)</td><td>{0}</td></tr>', obj.per.toFixed(2));
  text += String.format('<tr><td>EPS</td><td>{0}</td></tr>', eps.toFixed(2));

  text += '</table>'

  return text;
}

function updateResult(obj) {
  var text = '';

  text += getWAPHTMLText(obj.wap, obj.z);
  if (obj.eps.length) {
    text += getEPSHTMLText(obj);
  }
  text += getOverallHTMLText(obj);

  $('#result').html(text);
}

function parseJSON(obj) {
  console.log(obj);
  updateInfo(obj);
  updateResult(obj);
  updateMAChart(obj.wap);
  updateMAChartByYear(obj.wap);
  if (obj.eps.length) {
    updateEPSChart(obj.eps, true);
    updateEPSChart(obj.eps, false);
    updateProfitMarginChart(obj.eps);
    updateProfitMarginChartByYear(obj.eps);
  }
  else {
    $('#cumulative_eps').hide();
    $('#eps').hide();
    $('#profit_margin').hide();
    $('#profit_margin_by_year').hide();
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

function showLoading(code) {
  var text = '';
  var dict = getLinkDict(code, '');

  text += String.format('<span class="title">Loading ...</span><br>');

  for (var i=0; i<dict.length; i++) {
    text += String.format('<span class="link"><a href="{0}" target="_blank">{1}</a></span>', dict[i].val, dict[i].key);
  }

  $('title').html('Loading ...');
  $('#info').html(text);
}

function updateStockReport() {
  var params = (new URL(window.location)).searchParams;
  var code = params.get('c');
  showLoading(code);
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

