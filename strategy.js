
var strategy = null;
var account = null;
var info = null;
var all_total_cost = 0;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

class stat {
  constructor() {
    this.ref = [0, 0, 0];
    this.qty = [0, 0, 0];
    this.cost = [0, 0, 0];
    this.total_qty = 0;
    this.total_cost = 0;
  }
}

function getStat(s) {
  var ref_pz = parseFloat(s.ref_pz);
  var st = new stat();

  // caculate ref prize by levels
  for (var i=0; i<3; i++) {
    st.ref[i] = ref_pz * (9 - i) / 10;
  }

  for (var i=0; i<account.stocks.length; i++) {
    let a = account.stocks[i];
    if (a.code == s.code) {
      let v = [];
      for (var j=0; j<a.events.length; j++) {
        let e = a.events[j];
        if (e.type == 'buy') {
          for (var k=0; k<parseInt(e.qty); k++) {
            v.push(e.pz);
          }
        }
        else if (e.type == 'sell') {
          for (var k=0; k<parseInt(e.qty); k++) {
            v.shift();
          }
        }
      }
      for (var k=0; k<v.length; k++) {
        for (var x=2; x>=0; x--) {
          if (!x || v[k] <= st.ref[x]) {
            st.qty[x] = st.qty[x] + 1;
            st.cost[x] = st.cost[x] + (parseFloat(v[k]) * 1000);
            break;
          }
        }
      }
    }
  }

  for (var i=0; i<3; i++) {
    if (st.qty[i]) {
      st.total_qty += st.qty[i];
      st.total_cost += st.cost[i];
      all_total_cost += st.cost[i];
    }
  }

  return st;
}

function updateResult() {
  var text = '';
  var td_na = '<td><span class="grey">-</span></td>';

  if (!strategy || !account || !info) {
    return;
  }

  if (strategy.stocks.length != info.stocks.length) {
    console.log('strategy/info mismatch');
    return;
  }

  text += '<table id="stocks">';
  text += '<tr><th>代碼</th><th>名稱</th><th>參考價</th><th>預估張數</th>';
  text += '<th>市價</th><th colspan=2>批1</th><th colspan=2>批2</th><th colspan=2>批3</th><th>張數</th><th>剩餘</th><th>均價</th><th>成本</th>';
  text += '</tr>';

  for (var i=0; i<strategy.stocks.length; i++) {
    let s = strategy.stocks[i];
    let st = getStat(s);
    let z = info.stocks[i].z;
    let cls = Array(3).fill('grey');
    let z_cls = 'grey';
    let z_ratio = Math.round((z - s.ref_pz) / s.ref_pz * 100);

    for (var j=2; j>=0; j--) {
      if (z <= st.ref[j]) {
        cls[j] = z_cls = 'bg_yellow';
        break;
      }
    }

    text += '<tr>';
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.code);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.name);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.ref_pz);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.ref_qty);
    text += String.format('<td><span class="{0}">{1} ({2}%)</span></td>', z_cls, z.toFixed(2), z_ratio);
    for (var j=0; j<3; j++) {
      text += String.format('<td><span class="{0}"><={1}</span></td>', cls[j], st.ref[j].toFixed(2));
      if (st.qty[j]) {
        let avg = st.cost[j] / 1000 / st.qty[j];
        text += String.format('<td>#{0} ({1})</td>', st.qty[j], avg.toFixed(2));
      } else {
        text += td_na;
      }
    }
    if (st.total_cost) {
      let total_avg = st.total_cost / 1000 / st.total_qty;
      text += String.format('<td>{0}</td>', st.total_qty);
      text += String.format('<td>{0}</td>', s.ref_qty - st.total_qty);
      text += String.format('<td>{0}</td>', total_avg.toFixed(2));
      text += String.format('<td>{0}</td>', st.total_cost.toLocaleString());
    } else {
      text += td_na.repeat(4);
    }
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>'.repeat(4);
    text += td_na.repeat(11);
    text += '</tr>';
  }

  text += '</table>';

  text += '<hr>'
  text += String.format('<div class=total>總成本：{0}</div>', Math.round(all_total_cost).toLocaleString());

  $('#result').html(text);
}

function onTimeout() {
  console.log('timeout');
}

function parseStocksJSON(obj) {
  console.log(obj);
  info = obj;
  updateResult();
}

function loadStocksJSON(obj) {
  var codes = [];

  for (var i=0; i<strategy.stocks.length; i++) {
    codes.push(strategy.stocks[i].code);
  }

  $.ajax({
    url: String.format('view.py?c={0}', codes.join(',')),
    dataType: 'json',
    error: onTimeout,
    success: parseStocksJSON,
    timeout: 10000
  });
}

function parseStrategyJSON(obj) {
  console.log(obj);
  strategy = obj;
  loadStocksJSON(obj);
}
 
function loadStrategyJSON() {
  $.ajax({
    url: 'load.py?j=strategy.json',
    dataType: 'json',
    error: onTimeout,
    success: parseStrategyJSON,
    timeout: 2000
  });
}

function parseAccountJSON(obj) {
  console.log(obj);
  account = obj;
  updateResult();
}

function loadAccountJSON() {
  $.ajax({
    url: 'load.py?j=account.json',
    dataType: 'json',
    error: onTimeout,
    success: parseAccountJSON,
    timeout: 2000
  });
}

function onSuccess() {
  window.location.href = 'strategy.html';
}

function onSave() {
  var table = document.getElementById("stocks");
  var jsons = [];
  for (var i = 1, row; row = table.rows[i]; i++) {
    let code = row.cells[0].textContent;
    let name = row.cells[1].textContent;
    let ref_pz = row.cells[2].textContent;
    let ref_qty = row.cells[3].textContent;
    if (code.length) {
      let obj = {};
      obj.code = code;
      obj.name = name;
      obj.ref_pz = ref_pz;
      obj.ref_qty = ref_qty;
      jsons.push(JSON.stringify(obj));
    }
  }
  let data = '{"stocks":[\n\t' + jsons.join(',\n\t') + '\n]}';
  console.log(data);
  $.ajax({
    type: 'POST',
    url: 'upload.py?j=strategy.json',
    data: {data: data},
    success: onSuccess,
  });
}

function onDocumentReady() {
  loadAccountJSON();
  loadStrategyJSON();
}

