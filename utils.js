
function onGotoSelectChange() {
  window.location.href = $(this).val();;
}

function loadTopMenu() {
  var text = '';

  const path = window.location.pathname.split('/');
  const file = path[path.length - 1];

  text += '<table>';
  text += '<tr>';
  text += '<td><select onchange="onGotoSelectChange.call(this)">\n';

  const opts = ['stock', 'edit', 'report', 'range', 'dividend', 'calendar', 'etf'];
  var found = false;

  for (let opt of opts) {
    let attr = '';
    if (file == opt + '.html') {
      attr = 'selected';
      found = true;
    }
    text += `<option value="${opt}.html" ${attr}>${opt}</option>\n`;
  }

  if (!found) {
    text += `<option value="" selected></option>\n`;
  }

  text += '</td>';
  text += '</tr>';
  text += '</table>';
  text += '<hr>';

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
