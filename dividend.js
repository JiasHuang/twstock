
var cur_objs = null;

function updateResult() {
  var stocks = cur_objs;
  var text = '';
  var cols = ['code', 'name', 'pz', '股利', 'date', '殖利率'];

  text += '<table id="stocks">';
  text += '<tr><th>' + cols.join('</th><th>') + '</th><tr>';

  for (var i=0; i<stocks.length; i++) {
    let s = stocks[i];
    let link = `<a href="report.html?c=${s.code}" target="_blank">${s.code}</a>`;
    let yield = s.dividend.cash / s.z * 100;
    let cash = s.dividend.cash;
    let date = s.dividend.date;
    let vals = [link, s.name, s.z,  cash.toFixed(3), date, yield.toFixed(2)];

    text += `<tr>`;
    text += '<td>' + vals.join('</td><td>') + '</td>';
    text += '</tr>';
  }

  text += '</table>';

  $('#result').html(text);
}

function parseStockJSON(objs) {
  cur_objs = objs;
  updateResult();
}

function updateStockInfo() {
  $.ajax({
    url: 'load.py?n=dividend',
    dataType: 'json',
    success: parseStockJSON,
    timeout: 30000, // 30s
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
}

