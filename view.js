
var is_StockInfo_loaded = false;
var is_StockTags_loaded = false;
var selected_tag = null;
var selected_innerTag = null;
var strategy = null;

String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function getStrategyText(code, pz, class_name) {
  var text = '';
  if (strategy) {
    for (var i=0; i<strategy.stocks.length; i++) {
      let s = strategy.stocks[i];
      if (s.code == code) {
        for (var j=2; j>=0; j--) {
          let ref = parseFloat(s.ref_pz) * (9 - j) / 10;
          if (pz <= ref) {
            text += String.format('<span class="{0}">分批{1}</span>', class_name, j + 1);
            break;
          }
        }
      }
    }
  }
  return text;
}

function getFltText(flts, flts_ret, class_name, class_name_false = '') {
  var vec = [];
  for (var i=0; i<flts.length; i++) {
      vec.push(String.format('<span class="{0}">{1}</span>', flts_ret[i] ? class_name : class_name_false, flts[i]));
  }
  return vec.join('，')
}

function getNoteText(notes, class_name = '') {
  var vec = [];
  for (var i=0; i<notes.length; i++) {
      vec.push(String.format('<span class="{0}">{1}</span>', class_name, notes[i]));
  }
  return vec.join('<br>');
}

function getStockTableText(s) {
  var c;
  var chg, ratio;
  var text = '';

  text += String.format('<table class="stockinfo {0}">', s.tags.join(' '));

  text += '<tr>';

  text += '<th rowspan=2>';
  text += String.format('<a href="report.html?c={0}" target="_blank">{0}<br>{1}</a>', s.code, s.msg.n);
  text += '</th>';

  text += '<td>';
  chg = s.z - s.y;
  ratio = chg / s.y * 100;
  c = ''
  c = (ratio > 0) ? ((ratio >= 9) ? 'bg_red' : 'red') : c;
  c = (ratio < 0) ? ((ratio <= -9) ? 'bg_green' : 'green') : c;
  text += String.format('<span class={0}>${1} ({2}, {3}%)</span>', c, s.z, chg.toFixed(2), ratio.toFixed(2));
  text += '</td>';

  text += '<td>';
  ratio = s.v / s.avg['30d_vol'] * 100;
  c = (ratio >= 120) ? 'bg_gold' : '';
  text += String.format('<span class={0}>#{1} ({2}%)</span>', c, s.v, ratio.toFixed(2));
  text += '</td>';

  text += '</tr>';

  text += '<tr>';

  text += '<td>';

  if (s.h) {
    chg = s.h - s.y
    ratio = chg / s.y * 100;
    text += String.format('Hi {0} ({1}, {2}%)', s.h.toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  if (s.l) {
    chg = s.l - s.y
    ratio = chg / s.y * 100;
    text += String.format('<br> Lo {0} ({1}, {2}%)', s.l.toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  if ('1m_pz' in s.avg) {
    chg = s.z - s.avg['1m_pz'];
    ratio = chg / s.avg['1m_pz'] * 100;
    text += String.format('<br> 月 {0} ({1}, {2}%)', s.avg['1m_pz'].toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  if ('3m_pz' in s.avg) {
    chg = s.z - s.avg['3m_pz'];
    ratio = chg / s.avg['3m_pz'] * 100;
    text += String.format('<br> 季 {0} ({1}, {2}%)', s.avg['3m_pz'].toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  if ('1y_pz' in s.avg) {
    chg = s.z - s.avg['1y_pz'];
    ratio = chg / s.avg['1y_pz'] * 100;
    text += String.format('<br> 年 {0} ({1}, {2}%)', s.avg['1y_pz'].toFixed(2), chg.toFixed(2), ratio.toFixed(2));
  }

  text += '</td>';

  text += '<td>';
  text += getFltText(s.flts, s.flts_ret, 'bg_yellow');
  text += getStrategyText(s.code, s.z, 'bg_yellow margin_left');
  if (s.flts.length && s.notes.length) {
    text += '<br>'
  }
  text += getNoteText(s.notes, 'note');
  text += '</td>';


  text += '</tr>';

  text += '</table>';

  return text;
}

function selectTag(tag) {

  selected_tag = tag;
  selected_innerTag = null;

  $('table').filter('.stockinfo').hide();
  $('table').filter('.stockinfo.'+tag).show();

}

function selectInnerTag(tag) {

  selected_tag = null;
  selected_innerTag = tag

  if (tag == 'all') {
    $('table').filter('.stockinfo').show();
  }

  else if (tag == 'hl') {
    $('table').filter('.stockinfo').hide();
    $('span').filter('.bg_red, .bg_green, .bg_yellow, .bg_gold').closest('table').show();
  }

}

function getTagsText(obj) {
  var text = '';
  var tags = [];

  for (var i=0; i<obj.stocks.length; i++) {
    for (var j=0; j<obj.stocks[i].tags.length; j++) {
      if (!tags.includes(obj.stocks[i].tags[j])) {
        tags.push(obj.stocks[i].tags[j]);
      }
    }
  }

  if (tags.length) {
    text += '<button onclick=selectInnerTag("all")>all</button>';
    text += '<button onclick=selectInnerTag("hl")>hl</button>';
    for (var i=0; i<tags.length; i++) {
      text += String.format('<button onclick=selectTag("{0}")>{0}</button>', tags[i]);
    }
  }

  return text;
}

function getExchangeRateTableText(objs) {
  var text = '';

  if (objs.length) {
    text += '<table>';
    text += '<tr><th>幣別</th><th>匯率</th><th></th></tr>';
    for (var i=0; i<objs.length; i++) {
      let obj = objs[i];
      let flt_txt = getFltText(obj.flts, obj.flts_ret, 'bg_yellow', 'grey');
      text += String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>', obj.currency, obj.sell_spot, flt_txt);
    }
    text += '</table>';
  }

  return text
}

function parseStockJSON(obj) {
  var text = '';

  if (!is_StockTags_loaded) {
    $('#tags').html(getTagsText(obj));
    is_StockTags_loaded = true;
  }

  for (var i=0; i<obj.stocks.length; i++) {
    text += getStockTableText(obj.stocks[i]);
  }

  $('#result').html(text);

  if (selected_tag)
    selectTag(selected_tag);
  if (selected_innerTag)
    selectInnerTag(selected_innerTag);

  is_StockInfo_loaded = true;
}

function parseExchangeRateJSON(obj) {
  $('#exrs').html(getExchangeRateTableText(obj.ExchangeRates));
}

function onTimeout () {
  console.log('timeout');
}

function showLoading() {
  $('#result').html('<span class="loading">Loading ...</span>');
}

function updateStockInfo() {
  $.ajax({
    url: 'view.py' + window.location.search,
    dataType: 'json',
    error: onTimeout,
    success: parseStockJSON,
    timeout: 2000
  });
}

function initStockInfo() {
  var api_url = 'view.py' + window.location.search;

  api_url += (window.location.search != '') ? '&s=1' : '?s=1';

  showLoading();
  $.ajax({
    url: api_url,
    dataType: 'json',
    error: onTimeout,
    success: parseStockJSON,
    timeout: 20000
  });
}

function updateExchangeRateInfo() {
  var api_url = 'exr.py' + window.location.search;

  $.ajax({
    url: api_url,
    dataType: 'json',
    error: onTimeout,
    success: parseExchangeRateJSON,
    timeout: 2000
  });
}

function updateInfoIfNeeded() {
  var date = new Date;
  var h = date.getHours();
  var m = date.getMinutes();
  var hhmm = h * 100 + m;
  if (hhmm >= 0900 && hhmm <= 1330) {
    if (is_StockInfo_loaded) {
      updateStockInfo();
    }
  }
  if (hhmm >= 0900 && hhmm <= 1530) {
    updateExchangeRateInfo();
  }
}

function parseStrategyJSON(obj) {
  strategy = obj;
}

function loadStrategyJSON() {
  $.ajax({
    url: 'load.py?j=strategy.json',
    dataType: 'json',
    error: onTimeout,
    success: parseStrategyJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  loadStrategyJSON();
  initStockInfo();
  updateExchangeRateInfo();
  setInterval(updateInfoIfNeeded, 5000);
}

