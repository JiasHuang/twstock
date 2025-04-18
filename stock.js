
var is_StockInfo_loaded = false;
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var strategy = null;
var cur_stock_json = null;
var sort_by = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function getStrategyText(code, pz, cls_name) {
  var text = '';
  if (strategy) {
    for (var i=0; i<strategy.stocks.length; i++) {
      let s = strategy.stocks[i];
      if (s.code == code) {
        let ratio = Math.round((pz - s.ref_pz) / s.ref_pz * 100);
        if (ratio <= -10)
          text += String.format('<span class="{0}" title="參考價 {1}">批{2}%</span>', cls_name, s.ref_pz, ratio);
      }
    }
  }
  return text;
}

function getFltText(flts, flts_ret, class_name, class_name_false = '') {
  var vec = [];
  for (var i=0; i<flts.length; i++) {
      vec.push(String.format('<span class="{0}">{1}</span>', flts_ret[i] ? class_name : class_name_false, flts[i]));
  }
  return vec.join('，')
}

function getStockTableText(s) {
  var c;
  var chg, ratio;
  var text = '';

  text += String.format('<table class="stockinfo {0}">', s.tags.join(' '));

  text += '<tr>';

  text += '<th rowspan=2>';
  text += String.format('<a href="report.html?c={0}" target="_blank">{0}<br>{1}</a>', s.code, s.msg.n);
  text += '</th>';

  text += '<td>';
  chg = s.z - s.y;
  ratio = chg / s.y * 100;
  c = ''
  c = (ratio > 0) ? ((ratio >= 9) ? 'bg_red' : 'red') : c;
  c = (ratio < 0) ? ((ratio <= -9) ? 'bg_green' : 'green') : c;
  text += String.format('<span class={0}>${1} ({2}, {3}%)</span>', c, s.z, chg.toFixed(2), ratio.toFixed(2));
  text += '</td>';

  text += '<td>';
  ratio = s.v / s.avg['30d_vol'] * 100;
  text += String.format('#{0} ({1}%)', s.v.toLocaleString(), ratio.toFixed(2));
  if (s.v >= 1000 && ratio >= 120)
    text += '<span class=bg_hv>★ </span>';
  text += '</td>';

  text += '</tr>';

  text += '<tr>';

  text += '<td>';

  if (s.h) {
    chg = s.h - s.y
    ratio = chg / s.y * 100;
    text += String.format('Hi {0} ({1}, {2}%)', s.h.toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  if (s.l) {
    chg = s.l - s.y
    ratio = chg / s.y * 100;
    text += String.format('<br> Lo {0} ({1}, {2}%)', s.l.toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  text += '</td>';
  text += '<td>';

  text += getFltText(s.flts, s.flts_ret, 'bg_yellow');
  text += getStrategyText(s.code, s.z, 'bg_yellow margin_left');

  if (s.nav)
  {
    let diff = s.nav - s.z;
    let diff_ratio = diff / s.z * 100;
    text += String.format('<br>淨值 {0} ({1}%)', s.nav.toFixed(2), diff_ratio.toFixed(2));
  }

  text += '</td>';

  text += '</tr>';

  text += '</table>';

  return text;
}

function selectTag(tag) {
  selected_tag = tag;
  selected_innerTag = null;
  updateResult();
}

function selectInnerTag(tag) {
  selected_tag = null;
  selected_innerTag = tag;
  updateResult();
}

function getTagsText(obj) {
  var text = '';
  var tags = [];

  for (var i=0; i<obj.stocks.length; i++) {
    for (var j=0; j<obj.stocks[i].tags.length; j++) {
      if (!tags.includes(obj.stocks[i].tags[j])) {
        tags.push(obj.stocks[i].tags[j]);
      }
    }
  }

  if (tags.length) {
    text += '<button onclick=selectInnerTag("all")>all</button>';
    text += '<button onclick=selectInnerTag("hl")>hl</button>';
    text += '<button onclick=selectInnerTag("hv")>hv</button>';
    for (var i=0; i<tags.length; i++) {
      text += String.format('<button onclick=selectTag("{0}")>{0}</button>', tags[i]);
    }
    text += '<button onclick=selectInnerTag("na")>na</button>';
  }

  return text;
}

function getExchangeRateTableText(objs) {
  var text = '';

  if (objs.length) {
    text += '<table>';
    text += '<tr><th>幣別</th><th>買入匯率</th><th>賣出匯率</th> <th></th></tr>';
    for (var i=0; i<objs.length; i++) {
      let obj = objs[i];
      let flt_txt = getFltText(obj.flts, obj.flts_ret, 'bg_yellow', 'grey');
      text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>', obj.currency, obj.buy_spot, obj.sell_spot, flt_txt);
    }
    text += '</table>';
  }

  return text
}

function sort_by_vol_ratio(a, b) {
  let a_ratio = a.v / a.avg['30d_vol'] * 100;
  let b_ratio = b.v / b.avg['30d_vol'] * 100;
  if (a_ratio < b_ratio) {
    return 1;
  }
  if (a_ratio > b_ratio) {
    return -1;
  }
  return 0;
}

function sort_by_inc_ratio(a, b) {
  let a_ratio = (a.z - a.y) / a.y * 100;
  let b_ratio = (b.z - b.y) / b.y * 100;
  if (a_ratio < b_ratio) {
    return 1;
  }
  if (a_ratio > b_ratio) {
    return -1;
  }
  return 0;
}

function sort_by_dec_ratio(a, b) {
  return sort_by_inc_ratio(b, a);
}

function filterTag() {
  if (selected_tag) {
    $('table').filter('.stockinfo').hide();
    $('table').filter('.stockinfo.'+selected_tag).show();
  }
  else if (selected_innerTag == 'hl') {
    $('table').filter('.stockinfo').hide();
    $('span').filter('.bg_red, .bg_green, .bg_yellow').closest('table').show();
  }
  else if (selected_innerTag == 'hv') {
    $('table').filter('.stockinfo').hide();
    $('span').filter('.bg_hv').closest('table').show();
  }
  else if (selected_innerTag == 'na') {
    $('table').filter('.stockinfo').hide();
    $('table[class="stockinfo "]').show();
  }
}

function updateResult() {
  var text = '';
  var stocks = cur_stock_json.stocks;

  if (!is_StockTags_loaded) {
    $('#tags').html(getTagsText(cur_stock_json));
    is_StockTags_loaded = true;
  }

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort(sort_by_vol_ratio);
  } else if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort(sort_by_inc_ratio);
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort(sort_by_dec_ratio);
  }

  for (var i=0; i<stocks.length; i++) {
    text += getStockTableText(stocks[i]);
  }

  $('#result').html(text);

  filterTag();

  is_StockInfo_loaded = true;
}

function parseStockJSON(obj) {
  cur_stock_json = obj;
  updateResult();
}

function parseExchangeRateJSON(obj) {
  $('#exrs').html(getExchangeRateTableText(obj.ExchangeRates));
}

function showLoading() {
  $('#result').html('<span class="loading">Loading ...</span>');
}

function updateStockInfo() {
  $.ajax({
    url: 'stock.py' + window.location.search,
    dataType: 'json',
    success: parseStockJSON,
  });
}

function initStockInfo() {
  var api_url = 'stock.py' + window.location.search;

  api_url += (window.location.search != '') ? '&s=1' : '?s=1';

  showLoading();
  $.ajax({
    url: api_url,
    dataType: 'json',
    success: parseStockJSON,
  });
}

function updateExchangeRateInfo() {
  var api_url = 'exr.py?j=exr.json' + window.location.search;

  $.ajax({
    url: api_url,
    dataType: 'json',
    success: parseExchangeRateJSON,
  });
}

function updateInfoIfNeeded() {
  var date = new Date;
  var h = date.getHours();
  var m = date.getMinutes();
  var hhmm = h * 100 + m;
  if (hhmm >= 0900 && hhmm <= 1330) {
    if (is_StockInfo_loaded) {
      updateStockInfo();
    }
  }
  if (hhmm >= 0900 && hhmm <= 1530) {
    updateExchangeRateInfo();
  }
}

function parseStrategyJSON(obj) {
  strategy = obj;
}

function loadStrategyJSON() {
  $.ajax({
    url: 'jsons/strategy.json',
    dataType: 'json',
    success: parseStrategyJSON,
  });
}

function onDocumentReady() {
  loadTopMenu();
  loadStrategyJSON();
  initStockInfo();
  updateExchangeRateInfo();
  setInterval(updateInfoIfNeeded, 30000); // 30s
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

