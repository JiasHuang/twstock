
var selected_tag = null;
var selected_innerTag = null;

function selectTag(tag) {
  selected_tag = tag;
  selected_innerTag = null;
  filterTag();
}

function selectInnerTag(tag) {
  selected_tag = null;
  selected_innerTag = tag;
  filterTag();
}

function updateTags(objs) {
  var text = '';
  var tags = [];

  for (const s of objs) {
    for (const tag of s.tags) {
      if (!tags.includes(tag))
        tags.push(tag);
    }
  }

  if (tags.length) {
    text += '<button onclick=selectInnerTag("all")>all</button>';
    for (const tag of tags)
      text += `<button onclick=selectTag("${tag}")>${tag}</button>`;
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
  }  else if (selected_innerTag == 'all') {
    $('tr').filter('.stockinfo').show();
  }
}

function updateResult(objs) {
  var text = '';

  text += '<table id="stocks">';
  text += '<tr><th>code</th><th>name</th><th>tags</th><th>flts</th></tr>';

  for (const s of objs) {
    text += `<tr class="stockinfo ${s.tags.join(' ')}">`;
    text += `<td contenteditable=true>${s.code}</td>`;
    text += `<td>${s.name}</td>`;
    text += `<td contenteditable=true>${getTagsText(s)}</td>`;
    text += `<td contenteditable=true>${getFltsText(s)}</td>`;
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>';
    text += '<td>-</td>';
    text += '<td contenteditable=true></td>'.repeat(2);
    text += '</tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function parseStockJSON(objs) {
  updateTags(objs);
  updateResult(objs);
}

function updateStockInfo() {
  $.ajax({
    url: 'load.py?n=watchlist',
    dataType: 'json',
    success: parseStockJSON,
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
    let tags = row.cells[2].textContent;
    let flts = row.cells[3].textContent;
    if (code.length) {
      let obj = {
        code: code,
        tags: (tags.length)? tags.split(/[ ,]+/) : [],
        flts: (flts.length)? flts.split(/[ ,]+/) : [],
      };
      jsons.push(JSON.stringify(obj));
    }
  }
  let data = '[\n\t' + jsons.join(',\n\t') + '\n]';
  $.ajax({
    type: 'POST',
    url: 'upload.py?j=stocks.json',
    data: {data: data},
    success: onSuccess,
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
}

