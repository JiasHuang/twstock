
var db = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function to_signed(n) {
  return  (n<=0? '':'+') + n.toLocaleString();
}

function updateResult() {
  var text = '';
  var qty = 0;
  var cost = 0;
  var avg = 0;
  var idx_start = db.length - 20;

  text += '<table>';
  text += '<tr><th>日期</th><th>買張</th><th>均價</th><th>賣張</th><th>均價</th><th>買賣超</th><th>張數</th><th>均價</th></tr>'
  for (var i=0; i<db.length; i++) {
    let x = db[i];
    qty += x.b_qty - x.s_qty;
    if (qty > 0) {
      cost = (cost + x.b_qty * x.b_pz) / (qty + x.s_qty) * qty;
      avg = cost / qty;
    } else {
      qty = cost = avg = 0;
    }
    if (i >= idx_start) {
      text += String.format('<tr><td>{' + Array.from(Array(8).keys()).join('}</td><td>{') + '}</td></tr>',
        x.date, to_signed(x.b_qty), x.b_pz, to_signed(-x.s_qty), x.s_pz,
        to_signed(x.b_qty - x.s_qty), qty.toLocaleString(), avg.toFixed(2));
    }
  }

  text += '</table>';

  $('#result').html(text);
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
    url: 'populate.py' + window.location.search,
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  loadJSON();
}

