
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var cur_stock_json = null;

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

  if (!is_StockTags_loaded) {
    updateTags(stocks);
    is_StockTags_loaded = true;
  }

  text += '<table id="stocks">';

  for (var i=0; i<stocks.length; i++) {
    const s = stocks[i];
    const k_list = [s.code, s.name];
    const kv_list = [
      ['Report', `report.html?c=${s.code}`],
      ['Chart', `chart.html?c=${s.code}`],
      ['Quote', `loadpng.py?c=${s.code}`],
      ['新聞', `https://tw.stock.yahoo.com/q/h?s=${s.code}`],
      ['股利', `https://www.wantgoo.com/stock/etf/${s.code}/dividend-policy/ex-dividend`],
      ['CMoney', `https://www.cmoney.tw/forum/stock/${s.code}`],
      ['玩股網', `https://www.wantgoo.com/stock/${s.code}`],
      ['鉅亨網', `https://www.cnyes.com/twstock/${s.code}`],
    ];

    text += `<tr class="stockinfo ${s.tags.join(' ')}">`;

    for (const k of k_list)
      text += `<td>${k}</td>`;

    for (const [k, v] of kv_list)
      text += `<td><a href="${v}" target="_blank">${k}</a></td>`;

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
  console.log('updateStockInfo');
  $.ajax({
    url: 'load.py?n=stocks' + window.location.search,
    dataType: 'json',
    success: parseStockJSON,
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
}

