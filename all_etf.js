
var cur_objs = null;
var sort_by = null;
var interval_id = null;

function pz_fmt(z, y, en_cls=false) {
  if (y == 0)
    return `${z}`;
  const chg = z - y;
  const chg_str = chg.toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const pct_str = (chg / y * 100).toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const cls = (en_cls && chg != 0) ? (chg > 0 ? 'inc':'dec'):'';
  return `${z} (${chg_str}, <span class="${cls}">${pct_str}%</span>)`;
}

function updateResult() {
  var text = '';
  var stocks = cur_objs;

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort((a, b) => b.mv_pct - a.mv_pct);
  } else if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort((a, b) => b.z/b.y - a.z/a.y);
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort((b, a) => b.z/b.y - a.z/a.y);
  } else if (sort_by == 'nav_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.nav/b.z - a.nav/a.z);
  } else if (sort_by == 'nav_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.nav/b.z - a.nav/a.z);
  } else if (sort_by == 'ma_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.ma_pct - a.ma_pct);
  } else if (sort_by == 'ma_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.ma_pct - a.ma_pct);
  } else if (sort_by == 'h_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.h_pct - a.h_pct);
  } else if (sort_by == 'h_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.h_pct - a.h_pct);
  }

  const cols = ['code', 'name', 'pz', 'nav', 'MA', 'MA%', 'high', 'low', 'H%', 'vol'];

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
    const link = `<a href="chart.html?c=${s.code}" target="_blank">${s.code}</a>`;
    const pz_str = pz_fmt(s.z, s.y, true);
    const nav_str = pz_fmt(s.nav, s.z) + ` <span class="nav_time">${s.nav_time}</span>`;
    const vol_str = `${s.v.toLocaleString()} (${s.mv_pct}%)`;
    const vals = [link, s.name, pz_str, nav_str, s.ma.toFixed(2), s.ma_pct.toFixed(2), s.days_hi, s.days_lo, s.h_pct, vol_str];
    text += '<tr><td>' + vals.join('</td><td>') + '</td></tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function parseStockJSON(objs) {

  // add ma_pct and mv_pct
  for (let s of objs) {
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

function updateStockInfo() {
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

function onDateChange() {
  const date = $(this).val().replace(/-/g, "");
  $.ajax({
    url: `load.py?n=etf&d=${date}`,
    dataType: 'json',
    success: parseStockJSON,
    timeout: 30000, // 30s
  });

  if (interval_id)
    clearInterval(interval_id);
}

