
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
      <option value="range.html">Range</option>
      <option value="report.html">Report</option>
      <option value="strategy.html">Strategy</option>
      <option value="calendar.html">Calendar</option>
      <option value="etf.html">ETF</option>
    </select>
    </td>
  `;

  text += '</tr>';
  text += '</table>';
  text += '<hr>';

  const path = window.location.pathname.split('/');
  const file = path[path.length - 1];
  const queryString = window.location.search;
  text = text.replace('"' + file + queryString + '"', '"' + file + queryString + '" selected');

  $('#topmenu').html(text);
}

function in_progress(a_h, a_m, b_h, b_m) {
  const today = new Date();
  const isWeekend = today.getDay()%6==0;
  const h = today.getHours();
  const m = today.getMinutes();

  if (isWeekend)
    return false;

  if (h < a_h || (h == a_h && m < a_m))
    return false;

  if (h > b_h || (h == b_h && m > b_m))
    return false;

  return true;
}
