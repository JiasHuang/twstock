
var db = null;
var dbmaps = [];

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

class dbmap {
  constructor(no, idx_start, idx_end, date) {
    this.no = no;
    this.idx_start = idx_start;
    this.idx_end = idx_end;
    this.date = date;
  }
}

function updateResult() {
  var text = '';

  for (var i=0; i<dbmaps.length; i++) {
    text += '<table>';
    text += String.format('<tr><th colspan=4 id="stockno_{0}"><a href="track.html?no={0}" target="_blank">{0}</a></th></tr>', dbmaps[i].no);
    text += '<tr><th>券商</th><th>張數</th><th>均價</th><th>日期</th></tr>';
    for (var j=dbmaps[i].idx_start; j<dbmaps[i].idx_end; j++) {
      let x = db[j];
      text += String.format('<tr><td>{' + Array.from(Array(4).keys()).join('}</td><td>{') + '}</td></tr>',
        x.bname, x.qty.toLocaleString(), x.avg.toFixed(2), x.date);
    }
    text += '</table>';
  }

  $('#result').html(text);
}

function onTimeout() {
  console.log('timeout');
}

function parseStocksJSON(obj) {
  console.log(obj);
  for (var i=0; i<obj.stocks.length; i++) {
    let msg = obj.stocks[i].msg;
    let text = String.format('<a href="track.html?no={0}" target="_blank">{0}{1}</a>(${2})', msg.c, msg.n, msg.z);
    $('#stockno_'+msg.c).html(text);
  }
}

function loadStocksJSON(obj) {
  var codes = [];
  for (var i=0; i<dbmaps.length; i++) {
    codes.push(dbmaps[i].no);
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

  var curr = null;
  for (var i=0; i<db.length; i++) {
    let x = db[i];
    if (!curr || curr.no != x.no) {
      if (curr) {
        curr.idx_end = i;
      }
      curr = new dbmap(x.no, i, db.length, x.date);
      dbmaps.push(curr);
    }
    if (curr.date < x.date)
      curr.date = x.date;
  }

  dbmaps.sort(function (a, b) {
    if (a.date > b.date) return -1;
    if (a.date < b.date) return 1;
    return 0;
  });

  updateResult();
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

