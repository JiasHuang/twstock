
var db = null;
var stocks = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function updateResult() {
  var text = '';
  var currno = null;
  var idx = 0;

  for (var i=0; i<db.length; i++) {
    let x = db[i];
    if (currno != x.no) {
      if (currno) {
        text += '</table>';
      }
      text += '<table>';
      text += String.format('<tr><th colspan=4><a href="track.html?a=track&no={0}" target="_blank">{0} {1}</a> (${2})</th></tr>', x.no, stocks[idx].msg.n, stocks[idx].z);
      text += '<tr><th>券商</th><th>張數</th><th>均價</th><th>日期</th></tr>';
      currno = x.no;
      idx++;
    }
    text += String.format('<tr><td>{' + Array.from(Array(4).keys()).join('}</td><td>{') + '}</td></tr>',
      x.bname, x.qty.toLocaleString(), x.avg.toFixed(2), x.date);
  }

  if (db.length) {
    text += '</table>';
  }

  $('#result').html(text);
}

function onTimeout() {
  console.log('timeout');
}

function parseStocksJSON(obj) {
  console.log(obj);
  stocks = obj.stocks;
  updateResult();
}

function loadStocksJSON(obj) {
  var codes = [];

  for (var i=0; i<db.length; i++) {
    if (!codes.includes(db[i].no)) {
      codes.push(db[i].no);
    }
  }

  $.ajax({
    url: String.format('view.py?c={0}', codes.join(',')),
    dataType: 'json',
    error: onTimeout,
    success: parseStocksJSON,
    timeout: 10000
  });
}

function parseJSON(obj) {
  console.log(obj);
  db = obj.db.sort(function (a, b) {
    if (a.no < b.no) return -1;
    if (a.no > b.no) return 1;
    if (a.qty > b.qty) return -1;
    if (a.qty < b.qty) return 1;
    return 0;
  });
  loadStocksJSON();
}

function loadJSON() {
  $.ajax({
    url: 'populate.py?a=broker',
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  loadJSON();
}

