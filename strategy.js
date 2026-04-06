
function updateResult(obj) {
  var text = '';
  var td_na = '<td><span class="grey">-</span></td>';

  text += '<table id="stocks">';
  text += '<tr><th>代碼</th><th>名稱</th><th>參考價</th>'; // 0:代碼, 1:名稱, 2:參考價
  text += '<th>市價</th><th>漲跌</th><th>殖利率</th><th>備註</th>'; // 3:市價, 4:漲跌, 5:殖利率, 6:備註
  text += '</tr>';

  for (const s of obj.stocks) {
    let z_pct = ((s.z / s.ref_pz - 1) * 100).toFixed(2);
    let z_pct_cls = z_pct < 0 ? 'dec':'grey';

    var regexp = /現金股利\s*([\d|.]+)/g;
    var m = regexp.exec(s.note);
    var yield = m ? (parseFloat(m[1]) / s.z * 100).toFixed(2) : 0;
    var yield_cls = yield > 0 ? '':'grey';

    text += '<tr>';
    text += `<td class="edit" contenteditable=true>${s.code}</td>`;
    text += `<td>${s.name}</td>`;
    text += `<td class="edit" contenteditable=true><span class="grey">${s.ref_pz}</span></td>`;
    text += `<td>${s.z}</td>`;
    text += `<td><span class="${z_pct_cls}">${z_pct}%</span></td>`;
    text += `<td><span class="${yield_cls}">${yield}%</span></td>`;
    text += `<td class="note" contenteditable=true>${s.note}</td>`;
    text += '</tr>';
  }

  for (var i=0; i<3; i++) {
    text += '<tr>';
    text += '<td contenteditable=true></td>';
    text += td_na;
    text += '<td contenteditable=true></td>';
    text += td_na.repeat(3);
    text += '<td contenteditable=true></td>';
    text += '</tr>';
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
    let note = row.cells[6].textContent;
    if (code.length) {
      let obj = {};
      obj.code = code;
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

