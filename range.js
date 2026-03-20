
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var cur_stock_json = null;

function percent_string(x) {
  let optionsAlways = { signDisplay: 'always', maximumFractionDigits:2 };
  return x.toLocaleString('en-US', optionsAlways)+'%';
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

function updateTags(stocks) {
  var text = '';
  var tags = [];

  for (var i=0; i<stocks.length; i++) {
    for (var j=0; j<stocks[i].tags.length; j++) {
      if (!tags.includes(stocks[i].tags[j])) {
        tags.push(stocks[i].tags[j]);
      }
    }
  }

  if (tags.length) {
    text += '<button onclick=selectInnerTag("all")>all</button>';
    for (var i=0; i<tags.length; i++) {
      text += `<button onclick=selectTag("${tags[i]}")>${tags[i]}</button>`;
    }
    text += '<button onclick=selectInnerTag("na")>na</button>';
  }

  $('#tags').html(text);
}

function getTagsText(s) {
  if ('tags' in s && s.tags.length) {
    return s.tags.join(', ');
  }
  return '';
}

function getFltsText(s) {
  if ('flts' in s && s.flts.length) {
    return s.flts.join(', ');
  }
  return '';
}

function filterTag() {
  if (selected_tag) {
    $('tr').filter('.stockinfo').hide();
    $('tr').filter('.stockinfo.'+selected_tag).show();
  }  else if (selected_innerTag == 'na') {
    $('tr').filter('.stockinfo').hide();
    $('tr[class="stockinfo "]').show();
  }
}

function updateResult() {
  var text = '';
  var stocks = cur_stock_json.stocks;
  var r_min = -20;
  var r_max = 20;
  var r_step = 2.5;
  var optionsAlways = { signDisplay: 'always' };

  if (!is_StockTags_loaded) {
    updateTags(stocks);
    is_StockTags_loaded = true;
  }

  text += '<table id="stocks">';
  text += '<tr><th>code</th><th>name</th><th>Pz</th><th>MA%</th>';

  for (var r=r_min; r<=r_max; r+=r_step) {
    let s = r == 0 ? 'MA':percent_string(r);
    text += `<th>${s}</th>`;
  }

  text += '</tr>';

  for (var i=0; i<stocks.length; i++) {
    let s = stocks[i];
    let pct = (s.z / s.ma - 1) * 100;
    let pct_cls = pct < 0 ? 'bg_dec':'bg_inc';
    text += `<tr class="stockinfo ${s.tags.join(' ')}">`;
    text += `<td><a href="candlestick.html?c=${s.code}" target="_blank">${s.code}</a></td>`;
    text += `<td>${s.name}</td>`;
    text += `<td>${s.z}</td>`;
    text += `<td><span class=${pct_cls}>${percent_string(pct)}</span></td>`;
    for (var r=r_min; r<=r_max; r+=r_step) {
      let x = (s.ma * (100 + r) / 100).toFixed(2);
      let c = '';
      c = (r == 0 && s.z > x) ? 'bg_inc' : c;
      c = (r == 0 && s.z < x) ? 'bg_dec' : c;
      c = (r > 0 && s.z >= x) ? 'bg_inc' : c;
      c = (r < 0 && s.z <= x) ? 'bg_dec' : c;
      text += `<td class=${c}>${x}</td>`;
    }

    text += '</tr>';
  }

  text += '</table>';

  $('#result').html(text);
  filterTag();
}

function parseStockJSON(obj) {
  cur_stock_json = obj;
  updateResult();
}

function updateStockInfo() {
  $.ajax({
    url: 'stock.py' + window.location.search,
    dataType: 'json',
    success: parseStockJSON,
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
  setInterval(updateStockInfo, 30000); // 30s
}

