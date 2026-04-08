
var cur_objs = null;
var sort_by = null;
var interval_id = null;

function updateResult() {
  var text = '';
  var stocks = cur_objs;

  if (sort_by == 'vol') {
    stocks = stocks.slice(0).sort((a, b) => b.mv_pct - a.mv_pct);
  } else if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort((a, b) => b.z/b.y - a.z/a.y);
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort((b, a) => b.z/b.y - a.z/a.y);
  } else if (sort_by == 'ma_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.ma_pct - a.ma_pct);
  } else if (sort_by == 'ma_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.ma_pct - a.ma_pct);
  }

  const cols = ['code', 'name', 'pz', 'pz%', 'MA', 'MA%', 'high', 'low', 'H%', 'vol', 'MV%'];

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
    const pz_pct = s.y != 0 ? (s.z / s.y  - 1) * 100 : 0;
    const vals = [link, s.name, s.z, pz_pct.toFixed(2), s.ma.toFixed(2), s.ma_pct.toFixed(2), s.days_hi, s.days_lo, s.h_pct, s.v.toLocaleString(), s.mv_pct];
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

