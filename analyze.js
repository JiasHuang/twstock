
var cur_stock_json = null;
var sort_by = null;
var interval_id = null;

function pz_fmt(z, y, en_cls=false) {
  const chg = z - y;
  const chg_str = chg.toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const pct_str = (chg / y * 100).toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const cls = (en_cls && chg != 0) ? (chg > 0 ? 'inc':'dec'):'';
  return `${z} (${chg_str}, <span class="${cls}">${pct_str}%</span>)`;
}

function updateResult() {
  var text = '';
  var stocks = cur_stock_json;

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort((a, b) => b.mv_pct - a.mv_pct);
  } else if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort((a, b) => b.chg/(b.z-b.chg) - a.chg/(a.z-a.chg));
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort((b, a) => b.chg/(b.z-b.chg) - a.chg/(a.z-a.chg));
  } else if (sort_by == 'nav_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.nav/b.z - a.nav/a.z);
  } else if (sort_by == 'nav_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.nav/b.z - a.nav/a.z);
  }

  const cols = ['code', 'name', 'pz', 'nav', 'MA%', 'vol'];

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

    const link = `<a href="candlestick.html?c=${s.code}" target="_blank">${s.code}</a>`;
    const pz_str = pz_fmt(s.z, s.z - s.chg, true);
    const nav_str = pz_fmt(s.nav, s.z) + ` <span class="nav_time">${s.nav_time}</span>`;
    const vol_str = `${s.v.toLocaleString()} (${s.mv_pct}%)`;
    const vals = [link, s.name, pz_str, nav_str, s.ma_pct, vol_str];
    text += '<tr><td>' + vals.join('</td><td>') + '</td></tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function parseStockJSON(obj) {
  cur_stock_json = obj;
  updateResult();
}

function updateStockInfo() {
  $.ajax({
    url: 'analyze.py' + window.location.search,
    dataType: 'json',
    success: parseStockJSON,
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

  const today = new Date();
  const isWeekend = today.getDay()%6==0;

  if (!isWeekend)
    interval_id = setInterval(updateStockInfo, 30000); // 30s
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

function onDateChange() {
  const date = $(this).val().replace(/-/g, "");
  const search = window.location.search;
  $.ajax({
    url: search.length ? `analyze.py${search}&d=${date}` : `analyze.py?d=${date}`,
    dataType: 'json',
    success: parseStockJSON,
  });

  if (interval_id)
    clearInterval(interval_id);
}

