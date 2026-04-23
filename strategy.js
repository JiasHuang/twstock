
function pct_str(x) {
  let cls = x == 0 ? 'grey' : (x < 0 ? 'dec':'inc');
  let str = x.toLocaleString('en-US', {signDisplay: 'always', maximumFractionDigits:2});
  return `<span class="${cls}">${str}%</span>`;
}

function get_tr_text(vals, clss) {
  var text = '';
  text += '<tr>';
  for (var i=0; i<vals.length; i++) {
    const val = vals[i];
    const cls = clss[i];
    if (cls == 'edit')
      text += `<td contenteditable=true><span class="${cls}">${val}</span></td>`;
    else if (cls == 'pct' && val != '')
      text += '<td>' + pct_str(val) + '</td>';
    else if (val == 0)
      text += `<td><span class="${cls} grey">${val}</span></td>`;
    else
      text += `<td><span class="${cls}">${val}</span></td>`;
  }
  text += '</tr>';

  return text;
}

function updateResult(objs) {
  var text = '';
  var td_na = '<td><span class="grey">-</span></td>';

  const cols = ['代碼', '名稱', '參考價', '市價', '漲跌', '股利', '殖利率', ''];

  text += '<table id="stocks">';
  text += '<tr><th>' + cols.join('</th><th>') + '</th></tr>';
  text += '</tr>';

  var cls = new Array(cols.length).fill('');
  cls[0] = 'edit';
  cls[2] = 'edit';
  cls[4] = 'pct';

  for (const s of objs) {
    let z_pct = s.ref_pz ? (s.z / s.ref_pz - 1) * 100 : 0;
    let yield = s.dividend.cash / s.z * 100;
    let notes = [];

    if (yield > 0)
      notes.push(`除息 ${s.dividend.date}`);

    let vals = [s.code, s.name, s.ref_pz, s.z, z_pct, s.dividend.cash.toFixed(3), yield.toFixed(2), notes.join('\n')];
    text += get_tr_text(vals, cls);
  }

  for (var i=0; i<3; i++) {
    let vals = new Array(cols.length).fill('');
    text += get_tr_text(vals, cls);
  }

  text += '</table>';

  $('#result').html(text);
}

function loadStrategyJSON() {
  $.ajax({
    url: `load.py?n=strategy`,
    dataType: 'json',
    success: updateResult,
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
    let ref_pz = row.cells[2].textContent;
    if (code.length) {
      let obj = {};
      obj.code = code;
      obj.ref_pz = ref_pz;
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

  let data = '[\n\t' + jsons.join(',\n\t') + '\n]';
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

