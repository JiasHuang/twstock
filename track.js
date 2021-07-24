
// Chart Globals Settings
Chart.defaults.global.animation.duration = 0;
Chart.defaults.global.hover.animationDuration = 0;
Chart.defaults.global.hover.responsiveAnimationDuration = 0;
Chart.defaults.global.title.display = true;
Chart.defaults.global.title.fontSize = 16;
Chart.defaults.global.events = ['click'];

var hdrs = null;
var tracks = null;
var limit = 30;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

class bstat_info {
  constructor(idx, qty, avg) {
    this.idx = idx;
    this.qty = qty;
    this.avg = avg;
  }
}

class bstat {
  constructor(bno, bname, qty, avg, date, infos) {
    this.bno = bno;
    this.bname = bname;
    this.qty = qty;
    this.avg = avg;
    this.date = date;
    this.infos = infos;
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
  $('div').filter('.chart').hide();
  $('#tbl_bno_' + bno).show();
  $('#chart_bno_' + bno).parent().show();
}

function toggle_tracks_by_chk() {
  let bno = $(this).attr('bno');
  if ($(this)[0].checked) {
    $('#tbl_bno_' + bno).show();
    $('#chart_bno_' + bno).parent().show();
  }
  else {
    $('#tbl_bno_' + bno).hide();
    $('#chart_bno_' + bno).parent().hide();
  }
}

function update_chart(bs) {
  var ctx = document.getElementById('chart_bno_' + bs.bno).getContext('2d');
  var labels = [];
  var data_qty = [];
  var data_avg = [];
  var datasets = [];
  var qty = 0;
  var cost = 0;
  var avg = 0;

  for (var i=0; i<bs.infos.length; i++) {
    let info = bs.infos[i];
    let x = tracks[info.idx];
    labels.push(x.date);
    data_qty.push(info.qty);
    data_avg.push(info.avg);
  }

  datasets.push({
    label: 'Qty',
    data: data_qty,
    yAxisID: 'Qty',
    borderColor: 'Blue',
    backgroundColor: 'Blue',
    fill: false,
  });

  datasets.push({
    label: 'Avg',
    data: data_avg,
    yAxisID: 'Avg',
    borderColor: 'Green',
    backgroundColor: 'Green',
    fill: false,
  });

  var lineChart = new Chart(ctx, {
    type: 'line',
    options: {
      title: {
        text: bs.bname
      },
      scales: {
        yAxes: [{
          id: 'Qty',
          type: 'linear',
          position: 'left',
        }, {
          id: 'Avg',
          type: 'linear',
          position: 'right',
        }]
      }
    },
    data: {
      labels:labels,
      datasets: datasets,
    }
  });

}

function getBrokerStatus() {

  var bstats = [];

  for (var h=0; h<hdrs.length; h++) {
    let qty = 0;
    let cost = 0;
    let avg = 0;
    let hdr = hdrs[h];
    let infos = [];
    for (var i=hdr.idx_start; i<hdr.idx_end; i++) {
      let x = tracks[i];
      let net_bs = x.b_qty - x.s_qty;
      qty += net_bs;
      if (qty > 0) {
        cost = (cost + x.b_qty * x.b_pz) / (qty + x.s_qty) * qty;
        avg = cost / qty;
      } else {
        qty = cost = avg = 0;
      }
      if (i >= Math.max(hdr.idx_start, hdr.idx_end - limit))
        infos.push(new bstat_info(i, qty, avg));
    }
    bstats.push(new bstat(hdr.bno, hdr.bname, qty, avg, tracks[hdr.idx_end - 1].date, infos));
  }

  bstats.sort(function (a, b) {
    if (a.qty > b.qty) return -1;
    if (a.qty < b.qty) return 1;
    return 0;
  });

  return bstats;
}

function updateResult() {
  var text = '';

  bstats = getBrokerStatus();
  console.log(bstats);

  // update summary table
  text += '<table>';
  text += '<tr><th colspan=5>'+hdrs[0].no+'</th></tr>';
  text += '<tr><th>券商</th><th>張數</th><th>均價</th><th>日期</th><th></th></tr>';
  for (var i=0; i<bstats.length; i++) {
    let x = bstats[i];
    let btn = '<button onclick=toggle_tracks_by_btn.call(this) bno="' + x.bno + '">check</button>';
    let chk = '<input type="checkbox" onclick=toggle_tracks_by_chk.call(this) bno="' + x.bno + '" />';
    text += String.format('<tr><td>{' + Array.from(Array(5).keys()).join('}</td><td>{') + '}</td></tr>',
      x.bname, x.qty.toLocaleString(), x.avg.toFixed(2), x.date, btn + chk);
  }
  text += '</table>';

  // update broker table
  for (var i=0; i<bstats.length; i++) {
    let bs = bstats[i];
    text += '<table class="tracks" id="tbl_bno_' + bs.bno + '">';
    text += '<tr><th colspan=8>' + bs.bname + '</th></tr>';
    text += '<tr><th>日期</th><th>買張</th><th>均價</th><th>賣張</th><th>均價</th><th>買賣超</th><th>張數</th><th>均價</th></tr>';
    for (var j=0; j<bs.infos.length; j++) {
      let info = bs.infos[j];
      let x = tracks[info.idx];
      let net_bs = x.b_qty - x.s_qty;
      let net_bs_cls = (net_bs>0)? 'red' : (net_bs<0? 'green':'');
      let net_bs_span = String.format('<span class="{0}">{1}</span>', net_bs_cls, to_signed(net_bs));
      text += String.format('<tr><td>{' + Array.from(Array(8).keys()).join('}</td><td>{') + '}</td></tr>',
        x.date, to_signed(x.b_qty), x.b_pz, to_signed(-x.s_qty), x.s_pz,
        net_bs_span, info.qty.toLocaleString(), info.avg.toFixed(2));
    }
    text += '</table>';
  }

  // update broker chart
  for (var i=0; i<bstats.length; i++) {
    let bs = bstats[i];
    text += '<div class="chart"><canvas id="chart_bno_' + bs.bno + '"></canvas></div>';
  }

  $('#result').html(text);
  $('table').filter('.tracks').hide();
  $('div').filter('.chart').hide();

  // update broker chart's content
  for (var i=0; i<bstats.length; i++) {
    update_chart(bstats[i]);
  }

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

function loadJSON(url_args) {
  $.ajax({
    url: 'populate.py' + window.location.search + url_args,
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 20000
  });
}

function updateResultByInput() {
  var code = document.getElementById('input_code').value;
  window.location.href = 'track.html?no=' + code;
}

function updateLatestResult() {
  $('#result').html('Loading ...');
  loadJSON('&a=track&latest=1');
}

function onDocumentReady() {
  loadTopMenu();
  if (window.location.search != '') {
    loadJSON('&a=track');
  }
}

