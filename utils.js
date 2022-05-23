
String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function onGotoSelectChange() {
  window.location.href = $(this).val();;
}

function loadTopMenu() {
  var text = '';

  text += '<table>';
  text += '<tr>';

  text += `
    <td>
    <select onchange="onGotoSelectChange.call(this)">
      <option value="stock.html">Stock</option>
      <option value="edit.html">Edit</option>
      <option value="account.html">Account</option>
      <option value="report.html">Report</option>
      <option value="strategy.html">Strategy</option>
      <option value="broker.html">Broker</option>
      <option value="bshtm.html">bshtm</option>
      <option value="track.html">Track</option>
    </select>
    </td>
  `;
  
  text += '</tr>';
  text += '</table>';
  text += '<hr>';

  var path = window.location.pathname.split('/');
  var file = path[path.length - 1];
  text = text.replace('"' + file + '"', '"' + file + '" selected');

  $('#topmenu').html(text);
}

function numFmt(n, p=2) {
  return ((n > 0) ? '+':'') + n.toFixed(p);
}
