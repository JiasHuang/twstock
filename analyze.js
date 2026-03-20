
var cur_stock_json = null;
var sort_by = null;

function pz_fmt(z, y, en_cls=false) {
  const chg = z - y;
  const chg_str = chg.toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  const pct_str = (chg / y * 100).toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  var cls = '';
  if (en_cls)
    cls = chg > 0 ? 'inc' : (chg < 0 ? 'dec':'');
  return `${z} (${chg_str}, <span class="${cls}">${pct_str}%</span>)`;
}

function updateResult() {
  var text = '';
  var stocks = cur_stock_json;

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort((a, b) => b.vol_pct - a.vol_pct);
  } else if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort((a, b) => b.chg/(b.z-b.chg) - a.chg/(a.z-a.chg));
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort((b, a) => b.chg/(b.z-b.chg) - a.chg/(a.z-a.chg));
  } else if (sort_by == 'nav_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.nav/b.z - a.nav/a.z);
  } else if (sort_by == 'nav_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.nav/b.z - a.nav/a.z);
  }

  const cols = ['code', 'name', 'pz', 'nav', 'vol'];

  text += '<table id="stocks">';
  text += '<tr><th>' + cols.join('</th><th>') + '</th></tr>';

  for (let s of stocks) {
    const link = `<a href="candlestick.html?c=${s.code}" target="_blank">${s.code}</a>`;
    const pz_str = pz_fmt(s.z, s.z - s.chg, true);
    const nav_str = pz_fmt(s.nav, s.z) + ` <span class="nav_time">${s.nav_time}</span>`;
    const vol_str = `${s.v.toLocaleString()} (${s.vol_pct}%)`;
    const vals = [link, s.name, pz_str, nav_str, vol_str];
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
  loadTopMenu();
  updateStockInfo();
  setInterval(updateStockInfo, 30000); // 30s
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

