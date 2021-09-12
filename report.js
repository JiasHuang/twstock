
// Chart Globals Settings
Chart.defaults.global.animation.duration = 0;
Chart.defaults.global.hover.animationDuration = 0;
Chart.defaults.global.hover.responsiveAnimationDuration = 0;
Chart.defaults.global.title.display = true;
Chart.defaults.global.title.fontSize = 16;
Chart.defaults.global.events = ['click'];

var colors = ['DarkGrey', 'Grey', 'SteelBlue', 'Blue'];
var def_color = colors[colors.length - 1];

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function init_colors_idx(vec, subidx)
{
  var subid =  null;
  var cnt = 0;
  for (var i=0; i<vec.length; i++) {
    if (subid != vec[i][subidx]) {
      subid = vec[i][subidx];
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
      for (var m=1; m<wap[i][1]; m++) {
        text += '<tr>' + '<td>-</td>'.repeat(5) + '</tr>';
      }
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

function getLinkDict(code, nf) {
  var dict = [];
  dict.push({key:'基本', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zca/zca_{0}.djhtm', code)});
  dict.push({key:'獲利', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zce/zce_{0}.djhtm', code)});
  dict.push({key:'財務', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr0.djhtm?b=Y&a={0}', code)});
  dict.push({key:'資產', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_{0}.djhtm', code)});
  dict.push({key:'損益', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_{0}.djhtm', code)});
  dict.push({key:'營收', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_{0}.djhtm', code)});
  dict.push({key:'新聞', val:String.format('https://tw.stock.yahoo.com/q/h?s={0}', code)});
  dict.push({key:'法人持股', val:String.format('https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl_{0}.djhtm', code)});
  dict.push({key:'持股分級', val:String.format('https://goodinfo.tw/StockInfo/EquityDistributionClassHis.asp?STOCK_ID={0}', code)});
  dict.push({key:'券商買賣', val:String.format('https://histock.tw/stock/branch.aspx?no={0}', code)});
  dict.push({key:'Ｋ線', val:String.format('https://goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID={0}&CHT_CAT2=DATE', code)});
  dict.push({key:'股利', val:String.format('https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID={0}', code)});
  dict.push({key:'除權息', val:String.format('https://goodinfo.tw/StockInfo/StockDividendSchedule.asp?STOCK_ID={0}', code)});
  dict.push({key:'GoodInfo', val:String.format('https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={0}', code)});
  dict.push({key:'MoneyDJ', val:String.format('https://www.moneydj.com/KMDJ/search/searchHome.aspx?_Query_={0}&_QueryType_=Main', nf)});
  dict.push({key:'Anue', val:String.format('https://invest.cnyes.com/twstock/TWS/{0}/overview', code)});
  dict.push({key:'HiStock', val:String.format('https://histock.tw/stock/{0}', code)});
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

  text += '<span class="link"><a href="#result">#result</a></span>';

  $('title').html(String.format('{0} {1} (${2})', obj.code, obj.n, obj.z));
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
    if (wap[i][0] == Y) {
      ret.push({x: wap[i][1].toString(), y: wap[i][4]});
    }
  }
  return ret;
}

function updateMAChartByYear(wap) {
  var ctx = document.getElementById('chart_MA_by_year').getContext('2d');
  var datasets = [];
  var labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
  var colors_idx = init_colors_idx(wap, 0);
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
    val = parseFloat(eps[i][11]);
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

// 0年 1季 2營業收入 3營業成本 4營業毛利 5毛利率 6營業利益 7營益率 8業外收支 9稅前淨利 10稅後淨利 11EPS(元)
function getProfitMarginByYear(eps, Y) {
  var ret = [];

  for (var i=0; i<eps.length; i++) {
    if (eps[i][0] != Y) {
      continue;
    }
    let x = 'Q' + eps[i][1];
    let rev = parseFloat(eps[i][2].replaceAll(',', ''));
    let net_profit = parseFloat(eps[i][6].replaceAll(',', ''));
    let profit_margin = net_profit / rev * 100;
    ret.push({x: x, y: profit_margin.toFixed(2)});
  }

  return ret;
}

function updateEPSChart(eps, cumulative) {
  var ctx = document.getElementById(cumulative ? 'chart_cumulative_EPS' : 'chart_EPS').getContext('2d');
  var datasets = [];
  var labels = ['Q1','Q2','Q3','Q4'];
  var colors_idx = init_colors_idx(eps, 0)
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

// 0年 1季 2營業收入 3營業成本 4營業毛利 5毛利率 6營業利益 7營益率 8業外收支 9稅前淨利 10稅後淨利 11EPS(元)
function updateProfitMarginChart(eps) {
  var ctx = document.getElementById('chart_profit_margin').getContext('2d');
  var datasets = [];
  var data = [];
  var labels = [];

  for (var i=0; i<eps.length; i++) {
    let rev = parseFloat(eps[i][2].replaceAll(',', ''));
    let net_profit = parseFloat(eps[i][6].replaceAll(',', ''));
    let profit_margin = net_profit / rev * 100;
    data.push(profit_margin.toFixed(2));
    labels.push(eps[i][0] + 'Q' + eps[i][1]);
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
  var colors_idx = init_colors_idx(eps, 0);
  var Y = null;

  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i][0]) {
      Y = eps[i][0];
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
    if (rev[i][0] != Y) {
      continue;
    }
    val = parseFloat(rev[i][2]) / 100000; //單位：1億
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

function getRevenueByYearQ(rev, Y, Q) {
  var vol = 0;
  var months = 0;

  for (var i=0; i<rev.length; i++) {
    if (rev[i][0] != Y) {
      continue;
    }
    if (Math.ceil(parseInt(rev[i][1]) / 3) != Q) {
      continue;
    }
    vol += parseFloat(rev[i][2]) / 100000; //單位：仟->億
    months += 1;
  }

  return {vol:vol, months:months};
}

function updateRevenueChart(rev, cumulative) {
  var ctx = document.getElementById(cumulative ? 'chart_cumulative_revenue' : 'chart_revenue').getContext('2d');
  var datasets = [];
  var labels = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
  var colors_idx = init_colors_idx(rev, 0);
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

  // 0年 1季 2營業收入 3營業成本 4營業毛利 5毛利率 6營業利益 7營益率 8業外收支 9稅前淨利 10稅後淨利 11EPS(元)
  // 單位：千股 / 百萬元
  for (var i=0; i<eps.length; i++) {
    if (Y != eps[i][0]) {
        Y = eps[i][0];
        text += '</table><table>';
        text += '<tr><th>年</th><th>季</th><th>營收(億)</th><th>營利(億)</th><th>營益率(%)</th><th>業外(億)</th><th>本業(%)</th><th>EPS</th><th></th></tr>';
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
            last4Q_eps += parseFloat(eps[eps.length-1-j][11]);
          }
          let price_to_earning = (obj.z / last4Q_eps).toFixed(2);
          let earning_yield = (last4Q_eps / obj.z * 100).toFixed(2);
          note += String.format('近四季EPS：{0} (累季：{1})<br>', last4Q_eps.toFixed(2), year_eps);
          note += String.format('目前股價：{0}<br>', obj.z);
          note += String.format('近四季本益比：{0}<br>', price_to_earning);
        }
        text += '<tr><td colspan=8></td><td rowspan=5>' + note + '</td></tr>';
        for (var q=1; q<eps[i][1]; q++) {
          text += '<tr>' + '<td>-</td>'.repeat(8) + '</tr>';
        }
    }
    let rev = parseFloat(eps[i][2].replaceAll(',', ''));
    let profit = parseFloat(eps[i][6].replaceAll(',', ''));
    let profit_other = parseFloat(eps[i][8].replaceAll(',', ''));
    let profit_rate = (profit >= 0 && profit_other >=0) ? (profit / (profit + profit_other) * 100).toFixed(2) : '-';
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>',
      eps[i][0], eps[i][1], (rev / 100).toFixed(2), (profit / 100).toFixed(2), eps[i][7], (profit_other / 100).toFixed(2), profit_rate, eps[i][11]);
  }

  for (var Q=parseInt(eps[eps.length-1][1])+1; Q<=4; Q++) {
    let rev = getRevenueByYearQ(obj.revenue, Y, Q);
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td>{3}</tr>',
      Y, Q, rev.vol.toFixed(2), '<td>-</td>'.repeat(5));
  }

  text += '</table><br>';

  return text;
}

function getDividendHTMLText(obj) {
  var text = '';
  var div = obj.dividend;

  text += '<table>';
  text += '<tr><th>股利所屬年度</th></th><th colspan=3>現金股利<br>盈餘/公積/合計</th><th colspan=3>股票股利<br>盈餘/公積/合計</th><th>現金殖利率(%)</th><th>盈餘分配率(%)</th></tr>';

  for (var i=0; i<div.length; i++) {
    let d = div[i];
    let cash_dividend_a = parseFloat(d[1]);
    let cash_dividend_b = parseFloat(d[2]);
    let cash_dividend = cash_dividend_a + cash_dividend_b;
    let stock_dividend_a = parseFloat(d[3]);
    let stock_dividend_b = parseFloat(d[4]);
    let stock_dividend = stock_dividend_a + stock_dividend_b;
    let dividend_yield = '-';
    let era = parseInt(d[0]) - 1911;
    let era_txt = d[0].replace(parseInt(d[0]), era);
    let eps = getEPSsByYear(obj.eps, era, true);
    let parsed = parseWAPByYear(obj.wap, era);
    let payout_ratio = '-';
    if (eps.length == 4) {
      payout_ratio = (cash_dividend / eps[3].y * 100).toFixed(2);
    }
    if (parsed[2]) {
      dividend_yield = (cash_dividend / parsed[2] * 100).toFixed(2);
    }
    text += String.format('<tr><td>{' + Array.from(Array(9).keys()).join('}</td><td>{') + '}</td></tr>',
      era_txt, cash_dividend_a.toFixed(2), cash_dividend_b.toFixed(2), cash_dividend.toFixed(2),
      stock_dividend_a.toFixed(2), stock_dividend_b.toFixed(2), stock_dividend.toFixed(2),
      dividend_yield, payout_ratio);
  }

  text += '</table><br>';

  return text;
}

function getOverallHTMLText(obj) {
  var text = '';
  var per_max_total_weight = 0;
  var per_max_total_sum = 0;
  var per_min_total_weight = 0;
  var per_min_total_sum = 0;

  text += String.format('<table><tr><th colspan={0}>PER</th></tr>', obj.per_year.length + 1);

  text += '<tr><td>年度</td>';
  for (var i=0; i<obj.per_year.length; i++)
    text += String.format('<td>{0}</td>', obj.per_year[i]);
  text += '</tr>';

  text += '<tr><td>最高本益比</td>';
  for (var i=0; i<obj.per_max.length; i++)
    text += String.format('<td>{0}</td>', obj.per_max[i]);
  text += '</tr>';

  text += '<tr><td>最低本益比</td>';
  for (var i=0; i<obj.per_min.length; i++)
    text += String.format('<td>{0}</td>', obj.per_min[i]);
  text += '</tr>';

  text += '</table><br>';

  for (var i=0; i<Math.min(4, obj.per_max.length); i++) {
    if (obj.per_max[i] <= 0)
      continue;
    let weight = Math.pow(0.67, i);
    per_max_total_sum += weight * obj.per_max[i];
    per_max_total_weight += weight;
  }

  for (var i=0; i<Math.min(4, obj.per_min.length); i++) {
    if (obj.per_min[i] <= 0)
      continue;
    let weight = Math.pow(0.67, i);
    per_min_total_sum += weight * obj.per_min[i];
    per_min_total_weight += weight;
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

  text += String.format('<tr><td colspan=2></td><td rowspan=7>');
  text += String.format('推估PER：{0} ~ {1}<br>', per_min.toFixed(2), per_max.toFixed(2));
  text += String.format('推估最高價：{0} ({1}%)<br>', pz_max.toFixed(2), ((pz_max - pz) / pz * 100).toFixed(2));
  text += String.format('推估中間價：{0} ({1}%)<br>', pz_mid.toFixed(2), ((pz_mid - pz) / pz * 100).toFixed(2));
  text += String.format('推估最低價：{0} ({1}%)<br>', pz_min.toFixed(2), ((pz_min - pz) / pz * 100).toFixed(2));
  text += String.format('</td></tr>', pz_min.toFixed(2));

  text += String.format('<tr><td>收盤價</td><td>{0}</td></tr>', pz.toFixed(2));
  text += String.format('<tr><td>淨值 (NAV)</td><td>{0}</td></tr>', obj.nav.toFixed(2));
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
  text += getDividendHTMLText(obj);
  text += getOverallHTMLText(obj);

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

function onTimeout () {
  console.log('timeout');
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
    error: onTimeout,
    success: parseJSON,
    timeout: 20000
  });
}

function updateReportByInput() {
  var code = document.getElementById('input_code').value;
  window.location.href = 'report.html?c=' + code;
}

function onDocumentReady() {
  loadTopMenu();
  if (window.location.search != '') {
    updateStockReport();
  }
}

