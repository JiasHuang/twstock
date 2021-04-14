
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

  text += '<table class="toptbl">';
  text += '<tr><th>代碼</th><th>名稱</th><th>市價</th><th>券商</th><th>Note</th></tr>';
  for (var i=0; i<dbmaps.length; i++) {
    let x = dbmaps[i];
    let n = String.format('<span id="top_stockno_{0}_n"></span>', x.no);
    let z = String.format('<span id="top_stockno_{0}_z"></span>', x.no);
    let brokers = '';
    let note = String.format('<a href="track.html?no={0}" target="_blank">tracks</a>', x.no);

    brokers += '<table class="subtbl">';
    for (var j=x.idx_start; j<x.idx_end; j++) {
      let b = db[j];
      brokers += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>',
        b.bname, b.qty.toLocaleString(), b.avg.toFixed(2), b.date);
    }
    brokers += '</table>';

    text += String.format('<tr><td>{' + Array.from(Array(5).keys()).join('}</td><td>{') + '}</td></tr>',
      x.no, n, z, brokers, note);

  }
  text += '</table>';

  $('#result').html(text);
}

function onTimeout() {
  console.log('timeout');
}

function parseStocksJSON(obj) {
  console.log(obj);
  for (var i=0; i<obj.stocks.length; i++) {
    let msg = obj.stocks[i].msg;
    $('#top_stockno_'+msg.c+'_n').html(msg.n);
    $('#top_stockno_'+msg.c+'_z').html(msg.z);
  }
}

function loadStocksJSON(obj) {
  var codes = [];
  for (var i=0; i<dbmaps.length; i++) {
    codes.push(dbmaps[i].no);
  }
  $.ajax({
    url: String.format('view?c={0}', codes.join(',')),
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
    url: 'populate?a=broker',
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  loadTopMenu();
  loadJSON();
}

