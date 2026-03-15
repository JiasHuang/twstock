
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var cur_stock_json = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

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
    for (var i=0; i<tags.length; i++) {
      text += String.format('<button onclick=selectTag("{0}")>{0}</button>', tags[i]);
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
  }
  else if (selected_innerTag) {
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
    text += String.format('<th>{0}</th>', r == 0 ? 'MA': percent_string(r));
  }

  text += '</tr>';

  for (var i=0; i<stocks.length; i++) {
    let s = stocks[i];
    let pct = (s.z / s.ma - 1) * 100;
    text += String.format('<tr class="stockinfo {0}">', s.tags.join(' '));
    text += String.format('<td>{0}</td>', s.code);
    text += String.format('<td>{0}</td>', s.msg.n);
    text += String.format('<td>{0}</td>', s.z);
    text += String.format('<td><span class={0}>{1}</span></td>', pct < 0 ? 'bg_red':'bg_green', percent_string(pct));
    for (var r=r_min; r<=r_max; r+=r_step) {
      let x = (s.ma * (100 + r) / 100).toFixed(2);
      let c = '';
      c = (r == 0 && s.z > x) ? 'bg_green' : c;
      c = (r == 0 && s.z < x) ? 'bg_red' : c;
      c = (r > 0 && s.z >= x) ? 'bg_green' : c;
      c = (r < 0 && s.z <= x) ? 'bg_red' : c;
      text += String.format('<td class={0}>{1}</td>', c, x);
    }

    text += '</tr>';
  }

  text += '</table>';

  $('#result').html(text);
  filterTag();
}

function parseStockJSON(obj) {
  console.log(obj);
  cur_stock_json = obj;
  updateResult();
}

function initStockInfo() {
  var api_url = 'stock.py' + window.location.search;

  $.ajax({
    url: api_url,
    dataType: 'json',
    success: parseStockJSON,
  });
}

function onDocumentReady() {
  loadTopMenu();
  initStockInfo();
}

