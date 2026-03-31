
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var cur_stock_json = null;
var sort_by = null;

function pct_str(x, en_cls=false) {
  var cls = '';
  if (en_cls)
    cls = x > 0 ? 'inc' : (x < 0 ? 'dec':'');
  let str = x.toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  return `<span class="${cls}">${str}%</span>`;
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

  if (sort_by == 'inc') {
    stocks = stocks.slice(0).sort((a, b) => b.z/b.y - a.z/a.y);
  } else if (sort_by == 'dec') {
    stocks = stocks.slice(0).sort((b, a) => b.z/b.y - a.z/a.y);
  } else if (sort_by == 'ma_inc') {
    stocks = stocks.slice(0).sort((a, b) => b.ma_pct - a.ma_pct);
  } else if (sort_by == 'ma_dec') {
    stocks = stocks.slice(0).sort((b, a) => b.ma_pct - a.ma_pct);
  }

  if (!is_StockTags_loaded) {
    updateTags(stocks);
    is_StockTags_loaded = true;
  }

  var cols = ['code', 'name', 'Pz', 'Pz%', 'MA%']
  for (var r=r_min; r<=r_max; r+=r_step)
    cols.push(r == 0 ? 'MA':pct_str(r));

  text += '<table id="stocks">';
  text += '<tr><th>' + cols.join('</th><th>') + '</th><tr>';

  for (var i=0; i<stocks.length; i++) {
    let s = stocks[i];
    let link = `<a href="candlestick.html?c=${s.code}" target="_blank">${s.code}</a>`;
    let pct = (s.z / s.y - 1) * 100;
    let vals = [link, s.name, s.z,  pct_str(pct, true), pct_str(s.ma_pct, true)];
    text += `<tr class="stockinfo ${s.tags.join(' ')}">`;
    text += '<td>' + vals.join('</td><td>') + '</td>';

    for (var r=r_min; r<=r_max; r+=r_step) {
      let x = s.ma * (100 + r) / 100;
      let c = '';
      if (r == 0)
        c = (s.z >= x) ? 'bg_inc':'bg_dec';
      else if (r > 0)
        c = (s.z >= x) ? 'bg_inc':'';
      else
        c = (s.z <= x) ? 'bg_dec':'';
      x_str = x.toLocaleString('en-US', {maximumFractionDigits:2});
      text += `<td class=${c}>${x_str}</td>`;
    }

    text += '</tr>';
  }

  text += '</table>';

  $('#result').html(text);
  filterTag();
}

function parseStockJSON(obj) {

  // add ma_pct
  for (let s of obj.stocks) {
    s.ma_pct = (s.z && s.ma) ? (s.z / s.ma * 100 - 100) : 0;
  }

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

  const today = new Date();
  const isWeekend = today.getDay()%6==0;

  if (!isWeekend)
    setInterval(updateStockInfo, 30000); // 30s
}

function onSelectChange() {
  sort_by = $(this).val();
  updateResult();
}

