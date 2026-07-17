
var cur_objs = null;
var sort_by = null;

function pct_fmt(pct) {
  let cls = pct == 0 ? '' : (pct < 0 ? 'dec' : 'inc');
  let str = pct.toLocaleString('en-US', {signDisplay:'always', maximumFractionDigits:2});
  return `<span class="${cls}">${str}%</span>`;
}

function updateResult() {
  var text = '';
  var stocks = cur_objs;

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort((a, b) => b.mv_pct - a.mv_pct);
  } else if (sort_by == 'amount') {
    stocks = stocks.slice(0).sort((a, b) => (b.z * b.v) - (a.z * a.v));
  } else if (sort_by == 'change') {
    stocks = stocks.slice(0).sort((a, b) => b.pz_pct - a.pz_pct);
  } else if (sort_by == 'ma20') {
    stocks = stocks.slice(0).sort((a, b) => b.ma20_pct - a.ma20_pct);
  } else if (sort_by == 'ma60') {
    stocks = stocks.slice(0).sort((a, b) => b.ma60_pct - a.ma60_pct);
  } else if (sort_by == 'range') {
    stocks = stocks.slice(0).sort((a, b) => b.r_pct - a.r_pct);
  }

  const cols = ['code', 'name', 'pz', 'chg%', 'MA20', 'MA20%', 'MA60', 'MA60%', 'high', 'low', 'R%', 'vol', 'MV%'];

  text += '<table id="stocks">';
  text += '<tr><th>' + cols.join('</th><th>') + '</th></tr>';

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const flt = urlParams.get('f');
  const conds = flt ? flt.split(',') : [];

  for (let s of stocks) {

    var flt_ret = true;

    for (let cond of conds) {
      if (!eval('s.'+cond)) {
        flt_ret = false;
        break;
      }
    }

    if (!flt_ret)
      continue;
    const link = `<a href="report.html?c=${s.code}" target="_blank">${s.code}</a>`;
    const vals = [link, s.name, s.z, pct_fmt(s.pz_pct), s.ma20.toFixed(2), pct_fmt(s.ma20_pct), s.ma60.toFixed(2), pct_fmt(s.ma60_pct), s.days_hi, s.days_lo, s.r_pct, s.v.toLocaleString(), s.mv_pct];
    text += '<tr><td>' + vals.join('</td><td>') + '</td></tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function parseStockJSON(objs) {

  // add pct
  for (let s of objs) {
    s.pz_pct = s.y ? (s.z / s.y * 100 - 100) : 0;
    s.ma20_pct = s.ma20 ? (s.z / s.ma20 * 100 - 100) : 0;
    s.ma60_pct = s.ma60 ? (s.z / s.ma60 * 100 - 100) : 0;
    s.mv_pct = s.mv ? Math.round(s.v / s.mv * 100) : 0;
    s.r_pct =  s.days_hi ? Math.round((s.z - s.days_lo) / (s.days_hi - s.days_lo) * 100) : 0;
  }

  cur_objs = objs;
  updateResult();
}

function updateStockInfo() {

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const q = urlParams.get('q');

  $.ajax({
    url: 'load.py?n=sheet&q='+q,
    dataType: 'json',
    success: parseStockJSON,
    timeout: 30000, // 30s
  });
}

function onDocumentReady() {

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const sort = urlParams.get('s');

  if (sort) {
    const selectElement = document.getElementById('sort');
    selectElement.value = sort;
    sort_by = sort;
  }

  loadTopMenu();
  updateStockInfo();
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

