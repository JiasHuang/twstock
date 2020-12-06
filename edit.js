
String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function getTagsText(s) {
  if ('tags' in s && s.tags.length) {
    return s.tags.join('\n');
  }
  return '';
}

function getFltsText(s) {
  if ('flts' in s && s.flts.length) {
    return s.flts.join('\n');
  }
  return '';
}

function getNotesText(s) {
  if ('notes' in s && s.notes.length) {
    return s.notes.join('\n');
  }
  return '';
}

function parseStockJSON(obj) {
  var text = '';

  console.log(obj);

  text += '<table id="stocks">';
  text += '<tr><th>code</th><th>name</th><th>tags</th><th>flts</th><th>notes</th></tr>';

  for (var i=0; i<obj.stocks.length; i++) {
    let s = obj.stocks[i];
    text += '<tr>';
    text += String.format('<td contenteditable=true>{0}</td>', s.code);
    text += String.format('<td contenteditable=true>{0}</td>', s.name);
    text += String.format('<td contenteditable=true>{0}</td>', getTagsText(s));
    text += String.format('<td contenteditable=true>{0}</td>', getFltsText(s));
    text += String.format('<td contenteditable=true>{0}</td>', getNotesText(s));
    text += '</tr>';
  }

  for (var i=0; i<10; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>'.repeat(5);
    text += '</tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function onTimeout() {
  console.log('timeout');
}

function loadStockJSON() {
  $.ajax({
    url: 'load.py',
    dataType: 'json',
    error: onTimeout,
    success: parseStockJSON,
    timeout: 2000
  });
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
      let obj = {};
      obj.code = code;
      obj.name = name;
      obj.tags = tags.split('\n');
      obj.flts = flts.split('\n');
      obj.notes = notes.split('\n');
      jsons.push(JSON.stringify(obj));
    }
  }
  let data = '{"stocks":[\n\t' + jsons.join(',\n\t') + '\n]}';
  console.log(data);
  $.ajax({
    type: 'POST',
    url: 'upload.py',
    data: {data: data},
  });
}

function onDocumentReady() {
  loadStockJSON();
}

