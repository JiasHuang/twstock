
var strategy = null;
var info = null;
var in_stock = [];

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

  if (!strategy || !info) {
    return;
  }

  text += '<table id="stocks">';
  text += '<tr><th>代碼</th><th>名稱</th><th>參考價</th>'; // 0:代碼, 1:名稱, 2:參考價
  text += '<th>市價</th><th>漲跌</th><th>殖利率</th><th>備註</th>'; // 3:市價, 4:漲跌, 5:殖利率, 6:備註
  text += '</tr>';

  for (var i=0; i<strategy.stocks.length; i++) {

    let info_stock = null;

    for (var j=0; j<info.stocks.length; j++)
    {
      if (strategy.stocks[i].code == info.stocks[j].code)
      {
        info_stock = info.stocks[j];
        break;
      }
    }

    let s = strategy.stocks[i];
    let st = getStat(s);
    let z = info_stock ? info_stock.z : 0;
    let z_diff = z - s.ref_pz;
    let z_ratio = (z_diff / s.ref_pz * 100).toFixed(2);
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
    text += String.format('<td class="edit grey" contenteditable=true>{0}</td>', s.ref_pz);
    text += String.format('<td><a href="report.html?c={0}">', s.code);
    text += String.format('<span class="curpz">{0}</span>', z.toFixed(2));
    text += String.format('</a></td>');
    text += String.format('<td><span class="{0}">{1}%</span></td>', z_ratio < 0 ? 'green':'grey', z_ratio);
    text += String.format('<td><span class="{0}">{1}%</span></td>', yield > 5 ? '':'grey', yield);
    text += String.format('<td class="note" contenteditable=true>{0}</td>', s.note);
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>'.repeat(4);
    text += td_na.repeat(3);
    text += '</tr>';
  }

  text += '</table>';

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
    url: 'jsons/strategy.json',
    dataType: 'json',
    error: onTimeout,
    success: parseStrategyJSON,
    timeout: 2000
  });
}

function onSuccess() {
  window.location.href = 'strategy.html';
}

function onSave() {
  var table = document.getElementById("stocks");
  var objs = [];
  var objs_move = [];
  var jsons = [];

  for (var i = 1, row; row = table.rows[i]; i++) {
    let code = row.cells[0].textContent;
    let name = row.cells[1].textContent;
    let ref_pz = row.cells[2].textContent;
    let note = row.cells[6].textContent;
    if (code.length) {
      let obj = {};
      obj.code = code;
      obj.name = name;
      obj.ref_pz = ref_pz;
      obj.note = note;
      if (code.indexOf('>') != -1) {
        sep_index = obj.code.indexOf('>');
        obj.code = code.substring(0, sep_index);
        obj.target_code = code.substring(sep_index + 1);
        obj.target_offset = 1;
        objs_move.push(obj);
      }
      else if (code.indexOf('<') != -1) {
        sep_index = obj.code.indexOf('<');
        obj.code = code.substring(0, sep_index);
        obj.target_code = code.substring(sep_index + 1);
        obj.target_offset = 0;
        objs_move.push(obj);
      }
      else
        objs.push(obj);
    }
  }

  for (var i = 0; i < objs_move.length; i++) {
    let obj = objs_move[i];
    let target_code = obj.target_code;
    let target_offset = obj.target_offset;
    delete obj.target_code; // delete temp attr
    delete obj.target_offset; // delete temp attr
    for (var j = 0; j < objs.length; j++) {
      if (objs[j].code == target_code) {
        objs.splice(j + target_offset, 0, obj);
        break;
      }
    }
    // not found
    if (j == objs.length)
      objs.push(obj);
  }

  for (var i = 0; i < objs.length; i++)
    jsons.push(JSON.stringify(objs[i]));

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
  loadStrategyJSON();
}

