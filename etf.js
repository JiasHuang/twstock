
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

  if (sort_by == 'nav') {
    stocks = stocks.slice(0).sort((a, b) => b.nav_pct - a.nav_pct);
  } else if (sort_by == 'nav_chg') {
    stocks = stocks.slice(0).sort((a, b) => b.nav_chg_pct - a.nav_chg_pct);
  } else if (sort_by == 'amount') {
    stocks = stocks.slice(0).sort((a, b) => b.amount - a.amount);
  }

  const cols = ['code', 'name', 'amount (百萬)', 'pz', 'nav', 'nav_y', 'nav%', 'nav_chg%', 'time'];

  text += '<table id="stocks">';
  text += '<tr><th>' + cols.join('</th><th>') + '</th></tr>';

  for (let s of stocks) {
    const link = `<a href="report.html?c=${s.code}" target="_blank">${s.code}</a>`;
    const time = s.nav_date + ' ' + s.nav_time;
    const vals = [link, s.name, s.amount.toLocaleString(), s.pz, s.nav, s.nav_y, pct_fmt(s.nav_pct), pct_fmt(s.nav_chg_pct), time];
    text += '<tr><td>' + vals.join('</td><td>') + '</td></tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function parseStockJSON(objs) {

  // add pct
  for (let s of objs) {
    s.nav_pct = (s.nav && s.pz) ? (s.nav / s.pz * 100 - 100) : 0;
    s.nav_chg_pct = (s.nav && s.nav_y) ? (s.nav / s.nav_y * 100 - 100) : 0;
    s.amount = (s.nav && s.units) ? (s.nav * s.units / 1000000) : 0; // 百萬
  }

  cur_objs = objs;
  updateResult();
}

function updateStockInfo() {

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const q = urlParams.get('q');

  $.ajax({
    url: 'load.py?n=etf',
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

