
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

function updateResult(objs) {
  var text = '';

  text += '<table id="stocks">';

  for (const s of objs) {
    const k_list = [s.code, s.name];
    const kv_list = [
      ['Report', `report.html?c=${s.code}`],
      ['Chart', `chart.html?c=${s.code}`],
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

function parseStockJSON(objs) {
  updateTags(objs);
  updateResult(objs);
}

function updateStockInfo() {
  console.log('updateStockInfo');
  $.ajax({
    url: 'load.py?n=edit',
    dataType: 'json',
    success: parseStockJSON,
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
}

