
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

function getNotesText(s) {
  if ('notes' in s && s.notes.length) {
    return s.notes.join('\n');
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

  if (!is_StockTags_loaded) {
    updateTags(stocks);
    is_StockTags_loaded = true;
  }

  text += '<table id="stocks">';
  text += '<tr><th>code</th><th>name</th><th>tags</th><th>flts</th><th>notes</th></tr>';

  for (var i=0; i<stocks.length; i++) {
    let s = stocks[i];
    text += String.format('<tr class="stockinfo {0}">', s.tags.join(' '));
    text += String.format('<td contenteditable=true>{0}</td>', s.code);
    text += String.format('<td contenteditable=true>{0}</td>', s.name);
    text += String.format('<td contenteditable=true>{0}</td>', getTagsText(s));
    text += String.format('<td contenteditable=true>{0}</td>', getFltsText(s));
    text += String.format('<td contenteditable=true>{0}</td>', getNotesText(s));
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>'.repeat(5);
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

function onTimeout() {
  console.log('timeout');
}

function loadStockJSON() {
  $.ajax({
    url: 'load.py?j=stocks.json',
    dataType: 'json',
    error: onTimeout,
    success: parseStockJSON,
    timeout: 2000
  });
}

function onSuccess() {
  window.location.href = 'edit.html';
}

function onSave() {
  var table = document.getElementById("stocks");
  var jsons = [];
  for (var i = 1, row; row = table.rows[i]; i++) {
    let code = row.cells[0].textContent;
    let name = row.cells[1].textContent;
    let tags = row.cells[2].textContent;
    let flts = row.cells[3].textContent;
    let notes = row.cells[4].textContent;
    if (code.length) {
      let obj = {
        code: code,
        name: name,
        tags: (tags.length)? tags.split(/[ ,]+/) : [],
        flts: (flts.length)? flts.split(/[ ,]+/) : [],
        notes: (notes.length)? notes.split('\n') : [],
      };
      jsons.push(JSON.stringify(obj));
    }
  }
  let data = '{"stocks":[\n\t' + jsons.join(',\n\t') + '\n]}';
  console.log(data);
  $.ajax({
    type: 'POST',
    url: 'upload.py?j=stocks.json',
    data: {data: data},
    success: onSuccess,
  });
}

function onDocumentReady() {
  loadStockJSON();
}

