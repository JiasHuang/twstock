
var Calendar = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function get_weeks_by_q(q) {
  var weeks = 0;
  for (var i=0; i<q.months.length; i++) {
    weeks += q.months[i].weeks.length;
  }
  return weeks;
}

function get_week_html(q, m, w) {
  var text = '<tr>';
  var first_w = w == m.weeks[0];
  var cls = m.M % 2 == 0 ? 'even':'';

  if (first_w && (m.M == 1 || m.M == 4 || m.M == 7 || m.M == 10)) {
    text += String.format('<td rowspan={0}>Q{1}</td>', get_weeks_by_q(q), q.Q);
  }

  if (first_w) {
    text += String.format('<td rowspan={0}>M{1}</td>', m.weeks.length, m.M);
    text += String.format('<td id="M{0}" rowspan={1} class="edit" contenteditable=true>{2}</td>', m.M, m.weeks.length, m.note);
  }

  text += String.format('<td class="{0}">W{1}</td>', cls, w.W);

  var today = new Date();

  for (var i=0; i<7; i++) {
    if (today.getMonth() + 1 == m.M && today.getDate() == w.days[i])
      text += String.format('<td id="today" class="{0}"><span class="bg_yellow">{1}</span></td>', cls, w.days[i]);
    else
      text += String.format('<td class="{0}"><span class="grey">{1}</span></td>', cls, w.days[i]);
  }

  text += String.format('<td id="M{0}W{1}" class="edit" contenteditable=true>{2}</td>', m.M, w.W, w.note);
  text += '</tr>';
  return text;
}

function updateResult() {
  var text = '';

  text += String.format('<h1>{0}</h1>', Calendar.Y);
  text += '<table>';
  text += '<tr><th>Quarter</th><th>Month</th><th>Note</th><th>Week</th>';

  var weekdays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

  for (var i=0; i < weekdays.length; i++)
    text += String.format('<th class="grey">{0}</th>', weekdays[i]);

  text += '<th>Note</th>';
  text += '</tr>';

  for (var i=0; i<Calendar.quarters.length; i++) {
    let q = Calendar.quarters[i];
    for (var j=0; j<q.months.length; j++) {
      let m = q.months[j];
      for (var k=0; k<m.weeks.length; k++) {
        let w = m.weeks[k];
        text += get_week_html(q, m, w);
      }
    }
  }

  $('#result').html(text);
}

function onTimeout() {
  console.log('timeout');
}

function parseCalendarJSON(obj) {
  console.log('--- Calendar ---');
  console.log(obj);
  Calendar = obj;
  updateResult();
  window.location.hash = '#today';
  window.history.replaceState({}, document.title, "calendar.html");
}

function loadCalendarJSON() {
  $.ajax({
    url: 'load.py?j=calendar.json',
    dataType: 'json',
    error: onTimeout,
    success: parseCalendarJSON,
    timeout: 2000
  });
}

function onSuccess() {
  window.location.href = 'calendar.html';
}

function onSave() {

  for (var i=0; i<Calendar.quarters.length; i++) {
    let q = Calendar.quarters[i];
    for (var j=0; j<q.months.length; j++) {
      let m = q.months[j];
      m.note = document.getElementById("M" + m.M).textContent;
      console.log(m.note);
      for (var k=0; k<m.weeks.length; k++) {
        let w = m.weeks[k];
        console.log("M"+m.M+"W"+w.W);
        w.note = document.getElementById("M" + m.M + "W" + w.W).textContent;
        console.log(w.note);
      }
    }
  }

  $.ajax({
    type: 'POST',
    url: 'upload.py?j=calendar.json',
    data: {data: JSON.stringify(Calendar, null, 2)},
    success: onSuccess,
  });
}

function onDocumentReady() {
  loadTopMenu();
  loadCalendarJSON();
}

