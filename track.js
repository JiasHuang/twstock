
var hdrs = null;
var tracks = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

class bstat {
  constructor(bno, bname, qty, avg, date) {
    this.bno = bno;
    this.bname = bname;
    this.qty = qty;
    this.avg = avg;
    this.date = date;
  }
}

function to_signed(n) {
  return  (n<=0? '':'+') + n.toLocaleString();
}

function toggle_tracks_by_btn() {
  let bno = $(this).attr('bno');
  $('input[type="checkbox"]').prop('checked', false);
  $('input[type="checkbox"][bno="'+bno+'"]').prop('checked', true);
  $('table').filter('.tracks').hide();
  $('#tbl_bno_' + bno).show();
}

function toggle_tracks_by_chk() {
  let bno = $(this).attr('bno');
  if ($(this)[0].checked)
    $('#tbl_bno_' + bno).show();
  else
    $('#tbl_bno_' + bno).hide();
}

function updateResult() {
  var text = '';
  var stat_text = '';
  var idx = 0;
  var bstats = [];

  for (var h=0; h<hdrs.length; h++) {
    let qty = 0;
    let cost = 0;
    let avg = 0;
    let hdr = hdrs[h];
    let idx_start = idx + hdr.cnt - 20;
    text += '<table class="tracks" id="tbl_bno_' + hdr.bno + '">';
    text += '<tr><th colspan=8>' + hdr.bname + '</th></tr>';
    text += '<tr><th>日期</th><th>買張</th><th>均價</th><th>賣張</th><th>均價</th><th>買賣超</th><th>張數</th><th>均價</th></tr>';
    for (var i=idx; i<idx+hdr.cnt; i++) {
      let x = tracks[i];
      qty += x.b_qty - x.s_qty;
      if (qty > 0) {
        cost = (cost + x.b_qty * x.b_pz) / (qty + x.s_qty) * qty;
        avg = cost / qty;
      } else {
        qty = cost = avg = 0;
      }
      if (i >= idx_start) {
        text += String.format('<tr><td>{' + Array.from(Array(8).keys()).join('}</td><td>{') + '}</td></tr>',
          x.date, to_signed(x.b_qty), x.b_pz, to_signed(-x.s_qty), x.s_pz,
          to_signed(x.b_qty - x.s_qty), qty.toLocaleString(), avg.toFixed(2));
      }
    }
    idx += hdr.cnt;
    bstats.push(new bstat(hdr.bno, hdr.bname, qty, avg, tracks[idx - 1].date));
  }

  text += '</table>';

  stat_text += '<table>';
  stat_text += '<tr><th>券商</th><th>張數</th><th>均價</th><th>日期</th><th></th></tr>';
  for (var i=0; i<bstats.length; i++) {
    let x = bstats[i];
    let btn = '<button onclick=toggle_tracks_by_btn.call(this) bno="' + x.bno + '">check</button>';
    let chk = '<input type="checkbox" onclick=toggle_tracks_by_chk.call(this) bno="' + x.bno + '" />';
    stat_text += String.format('<tr><td>{' + Array.from(Array(5).keys()).join('}</td><td>{') + '}</td></tr>',
      x.bname, x.qty.toLocaleString(), x.avg.toFixed(2), x.date, btn + chk);
  }
  stat_text += '</table>';

  $('#result').html(stat_text + text);
  $('table').filter('.tracks').hide();
}

function onTimeout() {
  console.log('timeout');
}

function parseJSON(obj) {
  console.log(obj);
  hdrs = obj.hdrs;
  tracks = obj.tracks;
  updateResult();
}

function loadJSON() {
  $.ajax({
    url: 'populate.py' + window.location.search,
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  loadJSON();
}

