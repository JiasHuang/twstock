
var account = null;
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

function parsePolicyJSON(obj) {
  var text = '';

  console.log(obj);

  text += '<table id="stocks">';
  text += '<tr><th>代碼</th><th>名稱</th><th>參考價</th><th>預估張數</th><th colspan=2>分批1</th><th colspan=2>分批2</th><th colspan=2>分批3</th><th colspan=3>統計</th></tr>';

  for (var i=0; i<obj.stocks.length; i++) {
    let s = obj.stocks[i];
    let st = getStat(s);
    text += '<tr>';
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.code);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.name);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.ref_pz);
    text += String.format('<td class="edit" contenteditable=true>{0}</td>', s.ref_qty);
    for (var j=0; j<3; j++) {
      text += String.format('<td><={0}</td>', st.ref[j]);
      if (st.qty[j]) {
        let avg = st.cost[j] / 1000 / st.qty[j];
        text += String.format('<td>均價：{0}，張數：{1}</td>', avg.toFixed(2), st.qty[j]);
      } else {
        text += String.format('<td> - </td>');
      }
    }
    if (st.total_cost) {
      let total_avg = st.total_cost / 1000 / st.total_qty;
      text += String.format('<td>張數：{0}</td>', st.total_qty);
      text += String.format('<td>剩餘：{0}</td>', s.ref_qty - st.total_qty);
      text += String.format('<td>均價：{0}，成本：{1}</td>', total_avg.toFixed(2), st.total_cost.toLocaleString());
    } else {
      text += '<td> - </td>'.repeat(3);
    }
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>'.repeat(4);
    text += '<td> - </td>'.repeat(9);
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

function loadPolicyJSON() {
  $.ajax({
    url: 'load.py?j=policy.json',
    dataType: 'json',
    error: onTimeout,
    success: parsePolicyJSON,
    timeout: 2000
  });
}

function parseAccountJSON(obj) {
  console.log(obj);
  account = obj;
  loadPolicyJSON();
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
  window.location.href = 'policy.html';
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
    url: 'upload.py?j=policy.json',
    data: {data: data},
    success: onSuccess,
  });
}

function onDocumentReady() {
  loadAccountJSON();
}

