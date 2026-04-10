
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var cur_objs = null;
var sort_by = null;
var interval_id = null;
var interval_id_exr = null;

function pct_fmt(val, pct, pct_cls='') {
  let val_str = val.toLocaleString('en-US', {maximumFractionDigits:2});
  let pct_str = pct.toLocaleString('en-US', {signDisplay:'always', maximumFractionDigits:2});
  return `${val_str} (<span class="${pct_cls}">${pct_str}%</span>)`;
}

function pz_fmt(val, chg, pct, cls='', pct_cls='') {
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
  text += `<a href="report.html?c=${s.code}" target="_blank">${s.code}<br>${s.name}</a>`;
  text += '</td>';

  var prices = [];

  chg = s.z - s.y;
  cls = ''
  cls = (s.pz_pct > 0) ? ((s.pz_pct >= 9) ? 'bg_inc' : 'inc') : cls;
  cls = (s.pz_pct < 0) ? ((s.pz_pct <= -9) ? 'bg_dec' : 'dec') : cls;
  prices.push(pz_fmt(s.z, chg, s.pz_pct, cls));

  if (s.h) {
    chg = s.h - s.y
    pct = chg / s.y * 100;
    prices.push(`Hi ${pz_fmt(s.h, chg, pct)}`);
  }

  if (s.l) {
    chg = s.l - s.y
    pct = chg / s.y * 100;
    prices.push(`Lo ${pz_fmt(s.l, chg, pct)}`);
  }

  text += '<td class="price">' + prices.join('<br>') +'</td>';

  var notes = [];

  const mv_pct_cls = s.mv_pct >= 150 ? 'bg_hv':'';
  const flt_str = getFltText(s, s.flts, 'flt bg_hl', 'flt');
  notes.push(`#${s.v.toLocaleString()} (<span class="${mv_pct_cls}">${s.mv_pct}%</span>) ${flt_str}`);

  if (s.nav) {
    let nav_pct = (s.nav / s.z - 1) * 100;
    let time = s.nav_time.substring(0, 5);
    let time_str = `<span class="nav_time">${time}</span>`;
    notes.push(`<span class="nav">淨值 ${pct_fmt(s.nav, nav_pct)}</span> ${time_str}`);
  }

  if (s.ma) {
    let ma_pct_cls = (s.ma_pct <= -10) ? 'bg_hl' : '';
    let ma_str = `<span class="MA">均線 ${pct_fmt(s.ma, s.ma_pct, ma_pct_cls)}</span>`;
    let h_str = `<span class="h_pct">H(${s.h_pct})</span>`;
    notes.push(`${ma_str} ${h_str}`);
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

function getTagsText(objs) {
  var text = '';
  var tags = [];

  for (const s of objs) {
    for (const tag of s.tags) {
      if (!tags.includes(tag))
        tags.push(tag);
    }
  }

  if (tags.length) {
    text += '<button onclick=selectInnerTag("all")>all</button>';
    text += '<button onclick=selectInnerTag("hl")>hl</button>';
    text += '<button onclick=selectInnerTag("hv")>hv</button>';
    for (const tag of tags)
      text += `<button onclick=selectTag("${tag}")>${tag}</button>`;
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
      let flt_str = getFltText(obj, obj.flts, 'bg_hl', 'grey');
      text += `<tr><td>${obj.currency}</td><td>${obj.buy_spot}</td><td>${obj.sell_spot}</td><td>${flt_str}</td></tr>`;
    }
    text += '</table>';
  }

  return text
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
  var stocks = cur_objs;

  if (!is_StockTags_loaded) {
    $('#tags').html(getTagsText(cur_objs));
    is_StockTags_loaded = true;
  }

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort((a, b) => b.mv_pct - a.mv_pct);
  } else if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort((a, b) => b.pz_pct - a.pz_pct);
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort((b, a) => b.pz_pct - a.pz_pct);
  } else if (sort_by == 'ma_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.ma_pct - a.ma_pct);
  } else if (sort_by == 'ma_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.ma_pct - a.ma_pct);
  }

  for (const s of stocks)
    text += getStockTableText(s);

  $('#result').html(text);

  filterTag();
}

function parseStockJSON(objs) {

  // add pct
  for (let s of objs) {
    s.pz_pct = s.y ? (s.z / s.y * 100 - 100) : 0;
    s.ma_pct = s.ma ? (s.z / s.ma * 100 - 100) : 0;
    s.mv_pct = s.mv ? Math.round(s.v / s.mv * 100) : 0;
    s.h_pct =  s.days_hi ? Math.round((s.z - s.days_hi) / (s.days_hi - s.days_lo) * 100) : 0;
  }

  cur_objs = objs;
  updateResult();

  if (interval_id == null)
  {
    const today = new Date();
    const isWeekend = today.getDay()%6==0;
    if (!isWeekend)
      interval_id = setInterval(updateStockInfo, 30000); // 30s
  }

}

function parseExchangeRateJSON(objs) {
  $('#exrs').html(getExchangeRateTableText(objs));

  if (interval_id_exr == null)
  {
    const today = new Date();
    const isWeekend = today.getDay()%6==0;
    if (!isWeekend)
      interval_id_exr = setInterval(updateExchangeRateInfo, 60000); // 60s
  }

}

function showLoading() {
  $('#result').html('<span class="loading">Loading ...</span>');
}

function updateStockInfo() {
  $.ajax({
    url: 'load.py?n=stock&nav=1',
    dataType: 'json',
    success: parseStockJSON,
    timeout: 30000, // 30s
  });
}

function updateExchangeRateInfo() {
  $.ajax({
    url: 'load.py?n=exr',
    dataType: 'json',
    success: parseExchangeRateJSON,
    timeout: 30000, // 30s
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
  updateExchangeRateInfo();
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

