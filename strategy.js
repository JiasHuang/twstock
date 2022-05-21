
var strategy = null;
var account = null;
var info = null;
var in_stock = [];
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
    this.total_buy_qty = 0;
    this.total_sell_qty = 0;
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

  for (var i=0; i<in_stock.length; i++) {
    let a = in_stock[i];
    if (a.code == s.code) {
      for (var j=0; j<a.events.length; j++) {
        let e = a.events[j];
        let qty = parseInt(e.qty);
        let pz = parseFloat(e.pz);
        if (e.type == 'buy') {
          for (var x=2; x>=0; x--) {
            if (!x || e.pz <= st.ref[x]) {
              let cost = pz * qty * 1000;
              st.qty[x] += qty;
              st.cost[x] += cost;
              st.total_buy_qty += qty;
              st.total_qty += qty;
              st.total_cost += cost;
              break;
            }
          }
        } else if (e.type == 'sell') {
          let avg = st.total_cost / st.total_qty;
          st.total_sell_qty += qty;
          st.total_qty -= qty;
          st.total_cost = avg * st.total_qty;
        }
      }
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

  if (strategy.stocks.length && strategy.stocks.length != info.stocks.length) {
    console.log('strategy/info mismatch');
    return;
  }

  text += '<table id="stocks">';
  text += '<tr><th>代碼</th><th>名稱</th><th>參考價</th>'; // 0:代碼, 1:名稱, 2:參考價
  text += '<th>市價</th><th>批1</th><th>批2</th><th>批3</th>'; // 3:市價, 4:批1, 5:批2, 6:批3
  text += '<th>備註</th>'; // 7:備註
  text += '<th>買入</th><th>賣出</th><th>均價</th><th>成本</th>';
  text += '</tr>';

  for (var i=0; i<strategy.stocks.length; i++) {
    let s = strategy.stocks[i];
    let st = getStat(s);
    let z = info.stocks[i].z;
    let z_diff = z - s.ref_pz;
    let z_ratio = Math.round(z_diff / s.ref_pz * 100);
    let r_cls = Array(3).fill('grey');

    if (z < s.ref_pz) {
      for (var j=2; j>=0; j--) {
        if (z <= st.ref[j]) {
          r_cls[j] = 'bg_yellow';
          break;
        }
      }
    }

    var regexp = /現金股利\s*([\d|.]+)/g;
    var m = regexp.exec(s.note);
    var yield = m ? (parseFloat(m[1]) / z * 100).toFixed(2) : 0;

    text += '<tr>';
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.code);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.name);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.ref_pz);
    text += String.format('<td><a href="report.html?c={0}" style="text-decoration: none">', s.code);
    text += String.format('<span class="curpz">{0}</span>', z.toFixed(2));
    text += String.format('\n<span class="{0}">{1} ({2}%)</span>', z_diff < 0 ? 'green':'grey', numFmt(z_diff), numFmt(z_ratio));
    text += String.format(' | <span class="{0}">殖利率 {1}%</span>', yield > 5 ? 'green':'grey', yield);
    text += String.format('</a></td>');
    for (var j=0; j<3; j++) {
      text += String.format('<td><span class="{0}"><={1}</span>\n', r_cls[j], st.ref[j].toFixed(2));
      if (st.qty[j]) {
        let avg = st.cost[j] / 1000 / st.qty[j];
        let avg_cls = (!j && avg > st.ref[0]) ? "batch_avg_warn" : "batch_avg";
        text += String.format('<span class="batch_qty">#{0}</span>', st.qty[j]);
        text += String.format('<span class="{0}">${1}</span>', avg_cls, avg.toFixed(2));
      } else {
        text += '<span class="batch_avg_na">-</span>';
      }
      text += '</td>';
    }
    text += String.format('<td class="note" contenteditable=true>{0}</td>', s.note);
    if (st.total_cost) {
      let avg = st.total_cost / 1000 / st.total_qty;
      let cost = Math.round(st.total_cost);
      let gain = z - avg;
      let gain_ratio = Math.round(gain / avg * 100);
      let gain_cls = (gain_ratio < 0) ? "gain_ratio_warn" : "gain_ratio";
      text += String.format('<td>{0}</td>', st.total_buy_qty);
      text += String.format('<td>{0}</td>', st.total_sell_qty);
      text += String.format('<td><span class="avg">{0}</span>', avg.toFixed(2));
      text += String.format('\n<span class="{0}">{1} ({2}%)</span></td>', gain_cls, gain.toFixed(2), gain_ratio);
      text += String.format('<td>{0}</td>', cost.toLocaleString());
      all_total_cost += cost;
    } else {
      text += td_na.repeat(4);
    }
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>'.repeat(4);
    text += td_na.repeat(8);
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
  console.log('--- stocks ---');
  console.log(obj);
  info = obj;
  updateResult();
}

function loadStocksJSON() {
  var codes = [];

  for (var i=0; i<strategy.stocks.length; i++) {
    codes.push(strategy.stocks[i].code);
  }

  $.ajax({
    url: String.format('stock.py?c={0}', codes.join(',')),
    dataType: 'json',
    error: onTimeout,
    success: parseStocksJSON,
    timeout: 10000
  });
}

function parseStrategyJSON(obj) {
  console.log('--- strategy ---');
  console.log(obj);
  strategy = obj;
  loadStocksJSON();
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
  console.log('--- account ---');
  console.log(obj);
  for (var i=0; i<obj.stocks.length; i++) {
    let a = obj.stocks[i];
    let total = 0;
    for (var j=0; j<a.events.length; j++) {
      let e = a.events[j];
      if (e.type == 'buy')
        total += parseInt(e.qty);
      else if (e.type == 'sell')
        total -= parseInt(e.qty);
    }
    if (total)
      in_stock.push(a);
  }
  account = obj;
  console.log(in_stock);
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
    let note = row.cells[7].textContent;
    if (code.length) {
      let obj = {};
      obj.code = code;
      obj.name = name;
      obj.ref_pz = ref_pz;
      obj.note = note;
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
  loadTopMenu();
  loadAccountJSON();
  loadStrategyJSON();
}

