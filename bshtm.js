
var db = null;
var foreign = ['1360','1380','1440','1470','1480','1520','1560','1570','1590','1650','8440','8890','8900','8960'];

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

class stockmap {
  constructor(stockno, idx_start, idx_end) {
    this.stockno = stockno;
    this.idx_start = idx_start;
    this.idx_end = idx_end;
  }
}

function getSortedStockTableText(sorted, title, cnt=-1, flt=null) {
  var text = '';

  text += '<table>';
  text += String.format('<tr><th colspan=6>{0}</th></tr>', title);
  text += '<tr><th>券商</th><th>買張</th><th>均價</th><th>賣張</th><th>均價</th><th>買賣超</th></tr>';

  if (cnt < 0 || cnt > sorted.length) {
    cnt = sorted.length;
  }

  for (var i=0; i<cnt; i++) {
    let x = sorted[i];
    if (flt && !eval(flt)) {
      continue;
    }
    text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>',
      x.bname, x.buy_qty.toLocaleString(), x.buy_avg.toFixed(2), (-x.sell_qty).toLocaleString(), x.sell_avg.toFixed(2),
      (x.buy_qty - x.sell_qty).toLocaleString());
  }

  text += '</table>';

  return text;
}

function getStockTableText(idx_start, idx_end) {
  var text = '';

  var total_buy_qty = 0;
  var total_sell_qty = 0;
  var foreign_qty = 0;

  for (var i=idx_start; i<idx_end; i++) {
    let x = db[i];
    total_buy_qty += x.buy_qty;
    total_sell_qty += x.sell_qty
    if (foreign.includes(x.bno)) {
      foreign_qty += x.buy_qty - x.sell_qty;
    }
  }

  text += String.format('<hr><span id="stockno_{0}" class="stat">{0}</span><span class="stat"> 成交張數：{1}，外資券商：{2} ({3}%)</span><br>',
    db[idx_start].stockno,
    Math.max(total_buy_qty, total_sell_qty).toLocaleString(),
    foreign_qty.toLocaleString(),
    (foreign_qty * 100 / Math.max(total_buy_qty, total_sell_qty)).toFixed(2));

  sorted = db.slice(idx_start, idx_end).sort(function (a, b) {
    let v0 = a.buy_qty - a.sell_qty;
    let v1 = b.buy_qty - b.sell_qty;
    if (v0 > v1) return -1;
    if (v0 < v1) return 1;
    return 0;
  });

  text += getSortedStockTableText(sorted, '買超 TOP10', 10);

  sorted = db.slice(idx_start, idx_end).sort(function (a, b) {
    let v0 = a.sell_qty - a.buy_qty;
    let v1 = b.sell_qty - b.buy_qty;
    if (v0 > v1) return -1;
    if (v0 < v1) return 1;
    return 0;
  });

  text += getSortedStockTableText(sorted, '賣超 TOP10', 10);

  sorted = db.slice(idx_start, idx_end).sort(function (a, b) {
    let v0 = a.buy_qty - a.sell_qty;
    let v1 = b.buy_qty - b.sell_qty;
    if (v0 > v1) return -1;
    if (v0 < v1) return 1;
    return 0;
  });

  text += getSortedStockTableText(sorted, '外資券商買超', -1, flt='foreign.includes(x.bno) && (x.buy_qty > x.sell_qty)');

  sorted = db.slice(idx_start, idx_end).sort(function (a, b) {
    let v0 = a.sell_qty - a.buy_qty;
    let v1 = b.sell_qty - b.buy_qty;
    if (v0 > v1) return -1;
    if (v0 < v1) return 1;
    return 0;
  });

  text += getSortedStockTableText(sorted, '外資券商賣超', -1, flt='foreign.includes(x.bno) && (x.sell_qty > x.buy_qty)');

  return text;
}

function updateMap(maps) {
  var text = '';

  for (var i=0; i<maps.length; i++) {
    text += String.format('<span class="link"><a href="#stockno_{0}">{0}</a></span><br>', maps[i].stockno);
  }

  $('#map').html(text);
}

function parseStocksJSON(obj) {
  for (var i=0; i<obj.stocks.length; i++) {
    let msg = obj.stocks[i].msg;
    let y = parseFloat(msg.y).toFixed(2);
    let z = parseFloat(msg.z).toFixed(2);
    let text = String.format('{0} {1} ${2} ({3}%) ',
      msg.c, msg.n, z, ((z - y) / y * 100).toFixed(2));
    $('#stockno_' + msg.c).html(text);
  }
}

function loadStocksJSON(maps) {
  var codes = [];

  for (var i=0; i<maps.length; i++) {
    codes.push(maps[i].stockno);
  }

  $.ajax({
    url: String.format('view.py?c={0}', codes.join(',')),
    dataType: 'json',
    error: onTimeout,
    success: parseStocksJSON,
    timeout: 10000
  });
}


function updateResult() {
  var text = '';
  var currno = null;
  var idx = 0;
  var maps = [];

  for (var i=0; i<db.length; i++) {
    let x = db[i];
    if (currno != x.stockno) {
      if (currno) {
        maps.push(new stockmap(db[idx].stockno, idx, i));
        idx = i;
      }
      idx = i;
      currno = x.stockno;
    }
  }

  if (db.length) {
    maps.push(new stockmap(db[idx].stockno, idx, db.length));
  }

  maps.sort(function (a, b) {
    if (a.stockno < b.stockno) return -1;
    if (a.stockno > b.stockno) return 1;
    return 0;
  });

  for (var i=0; i<maps.length; i++) {
    text += getStockTableText(maps[i].idx_start, maps[i].idx_end);
  }

  $('#result').html(text);
  updateMap(maps);
  loadStocksJSON(maps);
}

function onTimeout() {
  console.log('timeout');
}

function parseJSON(obj) {
  console.log(obj); 
  db = obj.db;
  updateResult();
}

function loadJSON() {
  $.ajax({
    url: 'populate.py?a=bshtm',
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  loadJSON();
}

