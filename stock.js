
var is_StockInfo_loaded = false;
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var cur_stock_json = null;
var sort_by = null;

function pct_str(val, chg, pct, cls='', pct_cls='') {
  let val_str = val.toLocaleString('en-US', {maximumFractionDigits:2});
  let chg_str = chg.toLocaleString('en-US', {signDisplay:'always', maximumFractionDigits:2});
  let pct_str = pct.toLocaleString('en-US', {signDisplay:'always', maximumFractionDigits:2});
  return `<span class="${cls}">${val_str} (${chg_str}, <span class="${pct_cls}">${pct_str}%</span>)</span>`;
}

function getFltText(obj, flts, cls_true, cls_false) {
  var vec = [];
  for (let flt of flts) {
      let ret = eval("obj." + flt);
      let cls = ret ? cls_true : cls_false;
      vec.push(`<span class="${cls}">${flt}</span>`);
  }
  return vec.join('，')
}

function getStockTableText(s) {
  var chg;
  var pct;
  var cls;
  var text = '';

  text += `<table class="stockinfo ${s.tags.join(' ')}">`;
  text += '<tr>';

  text += '<td class="link">';
  text += `<a href="candlestick.html?c=${s.code}" target="_blank">${s.code}<br>${s.name}</a>`;
  text += '</td>';

  var prices = [];

  chg = s.z - s.y;
  pct = chg / s.y * 100;
  cls = ''
  cls = (pct > 0) ? ((pct >= 9) ? 'bg_inc' : 'inc') : cls;
  cls = (pct < 0) ? ((pct <= -9) ? 'bg_dec' : 'dec') : cls;
  prices.push(pct_str(s.z, chg, pct, cls));

  if (s.h) {
    chg = s.h - s.y
    pct = chg / s.y * 100;
    prices.push(`Hi ${pct_str(s.h, chg, pct)}`);
  }

  if (s.l) {
    chg = s.l - s.y
    pct = chg / s.y * 100;
    prices.push(`Lo ${pct_str(s.l, chg, pct)}`);
  }

  text += '<td class="price">' + prices.join('<br>') +'</td>';

  var notes = [];

  pct = Math.round(s.v / s.mv * 100);
  const hv = pct >= 120 ? '<span class="bg_hv">★ </span>':'';
  const flt = getFltText(s, s.flts, 'flt bg_hl', 'flt');
  notes.push(`#${s.v.toLocaleString()} (${pct}%)${hv} ${flt}`);

  if (s.nav) {
    chg = s.nav - s.z;
    pct = chg / s.z * 100;
    let time = s.nav_time.substring(0, 5);
    let time_str = `<span class="nav_time">${time}</span>`;
    notes.push(`<span class="nav">淨值 ${pct_str(s.nav, chg, pct)}</span> ${time_str}`);
  }

  if (s.ma) {
    chg = s.z - s.ma
    pct = chg / s.ma * 100;
    cls = (pct <= -10) ? 'bg_hl' : '';
    notes.push(`<span class="MA">均線 ${pct_str(s.ma, chg, pct, '', cls)}</span>`);
  }

  text += '<td class="note">' + notes.join('<br>') + '</td>';

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
      text += `<button onclick=selectTag("${tags[i]}")>${tags[i]}</button>`;
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
      let flt_txt = getFltText(obj, obj.flts, 'bg_hl', 'grey');
      text += `<tr><td>${obj.currency}</td><td>${obj.buy_spot}</td><td>${obj.sell_spot}</td><td>${flt_txt}</td></tr>`;
    }
    text += '</table>';
  }

  return text
}

function sort_by_vol_ratio(a, b) {
  let a_ratio = a.v / a.mv * 100;
  let b_ratio = b.v / b.mv * 100;
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

function sort_by_inc_ma_ratio(a, b) {
  let a_ratio = (a.z - a.ma) / a.ma * 100;
  let b_ratio = (b.z - b.ma) / b.ma * 100;
  if (a_ratio < b_ratio) {
    return 1;
  }
  if (a_ratio > b_ratio) {
    return -1;
  }
  return 0;
}

function sort_by_dec_ma_ratio(a, b) {
  return sort_by_inc_ma_ratio(b, a);
}

function filterTag() {
  if (selected_tag) {
    $('table').filter('.stockinfo').hide();
    $('table').filter('.stockinfo.'+selected_tag).show();
  }
  else if (selected_innerTag == 'hl') {
    $('table').filter('.stockinfo').hide();
    $('span').filter('.bg_inc, .bg_dec, .bg_hl').closest('table').show();
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
  } else if (sort_by == 'dec_ma') {
    stocks = stocks.slice(0).sort(sort_by_dec_ma_ratio);
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

  showLoading();
  $.ajax({
    url: api_url,
    dataType: 'json',
    success: parseStockJSON,
  });
}

function updateExchangeRateInfo() {
  var api_url = 'exr.py' + window.location.search;

  $.ajax({
    url: api_url,
    dataType: 'json',
    success: parseExchangeRateJSON,
  });
}

function updateInfoIfNeeded() {
  if (is_StockInfo_loaded) {
    updateStockInfo();
  }
  updateExchangeRateInfo();
}

function onDocumentReady() {
  loadTopMenu();
  initStockInfo();
  updateExchangeRateInfo();
  setInterval(updateInfoIfNeeded, 30000); // 30s
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

