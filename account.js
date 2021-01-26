
String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{" + i + "\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}

function getDividendByCode(obj, code) {
  for (var i=0; i<obj.stocks.length; i++) {
    let s = obj.stocks[i]
    if (s.code == code) {
      return s
    }
  }
  return null;
}

function updateDividendForecast(obj, stocks) {
  var text = '';
  var all_total_dividend_cash = 0;

  text += '<table>';
  text += '<tr><th>代碼</th><th>名稱</th><th>均價</th><th>張數</th><th>近期配息</th><th>近期配股</th><th>預估現金股利</th><th>預估報酬率</th><th>可賣出價</th></tr>';

  for (var i=0; i<stocks.length; i++) {
    let s = stocks[i];
    if (s.total_qty > 0) {
      let div = getDividendByCode(obj, s.code);
      let dividend_cash = parseFloat(div.dividend[0][1]) + parseFloat(div.dividend[0][2]);
      let dividend_stock = parseFloat(div.dividend[0][3]) + parseFloat(div.dividend[0][4]);
      let total_dividend_cash = Math.round(s.total_qty * 1000 * dividend_cash);
      let total_dividend_cash_ratio = dividend_cash / s.avg_pz * 100;
      let ref_sell_pz = s.avg_pz + Math.max(dividend_cash * 2, s.avg_pz * 0.1);
      all_total_dividend_cash += total_dividend_cash;
      text += String.format('<tr><td><a href=report.html?c={0} target="_blank">{0}</a></td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}%</td><td>{8}</td></tr>',
        s.code, s.name, s.avg_pz.toFixed(2), s.total_qty.toFixed(2),
        dividend_cash.toFixed(2), dividend_stock.toFixed(2),
        total_dividend_cash.toLocaleString(2), total_dividend_cash_ratio.toFixed(2),
        ref_sell_pz.toFixed(2));
    }
  }

  text += '<tr><td colspan=9 class=total>';
  text += String.format('<hr>總預估現金股利：{0}', all_total_dividend_cash.toLocaleString());
  text += '</td></tr>';

  text += '</table>';

  $('#DividendForecast').html(text);
  return;
}

function updateResult(obj) {
  var text = '';
  var all_total_cost = 0;
  var all_total_gain = 0;
  var stocks_with_qty = [];

  obj.stocks.sort(function (a, b) {
    if (Date.parse(a.events[a.events.length-1].date) < Date.parse(b.events[b.events.length-1].date)) return 1;
    if (Date.parse(a.events[a.events.length-1].date) > Date.parse(b.events[b.events.length-1].date)) return -1;
    return 0;
  });

  for (var i=0; i<obj.stocks.length; i++) {
    let s = obj.stocks[i];
    let total_qty = 0;
    let total_expense = 0;
    let total_stock_cost = 0;
    let total_stock_gain = 0;
    let total_cash_dividend = 0;
    let total_fee = 0;
    let total_tax = 0;

    text += '<table>';
    text += String.format('<tr><th colspan=7>{0} {1}</th></tr>', s.code, s.name);
    text += '<tr><td>日期</td><td>事件</td><td>價格</td><td>張數</td><td>配股</td><td>配息</td><td>損益</td></tr>';
    for (var j=0; j<s.events.length; j++) {
      let e = s.events[j];
      let pz = parseFloat(e.pz);
      let qty = parseInt(e.qty);
      let cash_dividend = parseFloat(e.cash);
      let stock_dividend = parseFloat(e.stock);
      let vec = [];
      if (e.type == 'buy') {
        total_expense += pz * qty * 1000;
        total_stock_cost += pz * qty * 1000;
        total_fee += Math.round(pz * qty * 0.855); //電子下單，手續費6折
        total_qty += qty;
        vec.push(e.date, '<span class=red>買入</span>', pz.toFixed(2), e.qty, '-', '-', '-');
      }
      else if (e.type == 'sell') {
        let avg = total_stock_cost / (total_qty * 1000);
        let gain = (pz - avg) * qty * 1000;
        total_stock_gain += gain;
        total_stock_cost = total_stock_cost * (total_qty - qty) / total_qty;
        total_qty -= qty;
        total_fee += Math.round(pz * qty * 0.855); //電子下單，手續費6折
        total_tax += Math.round(pz * qty * 3);
        vec.push(e.date, '<span class=green>賣出</span>', pz.toFixed(2), e.qty, '-', '-', Math.round(gain).toLocaleString());
      }
      else if (e.type == 'dividend') {
        let gain = 0;
        if (stock_dividend > 0) {
          total_qty = total_qty * (10 + stock_dividend) / 10;
        }
        if (cash_dividend > 0) {
          gain = total_qty * 1000 * cash_dividend;
          total_cash_dividend += gain;
        }
        vec.push(e.date, '<span class=bg_gold>股利</span>', '-', '-', e.stock, e.cash, Math.round(gain).toLocaleString());
      }
      text += '<tr>';
      for (var v=0; v<vec.length; v++) {
        text += '<td>' + vec[v] + '</td>';
      }
      text += '</tr>'
    }
    s.total_qty = total_qty;
    text += '<tr><td colspan=6 class=note><hr>';
    text += String.format('成本支出：{0}<br>', total_expense.toLocaleString());
    text += String.format('證交稅：{0}<br>', total_tax);
    text += String.format('手續費：{0}<br>', total_fee);
    text += String.format('現金股利：{0}<br>', total_cash_dividend.toLocaleString());
    text += String.format('買賣損益：{0}<br>', total_stock_gain.toLocaleString());
    if (total_qty > 0) {
      s.avg_pz = total_stock_cost / (total_qty * 1000);
      text += String.format('目前張數：{0}<br>', total_qty);
      text += String.format('目前均價：{0}<br>', s.avg_pz.toLocaleString());
      stocks_with_qty.push(obj.stocks[i].code);
    }
    let total_gain = total_stock_gain + total_cash_dividend - total_fee - total_tax;
    let total_gain_ratio = total_gain / total_expense * 100;
    if (total_qty > 0) {
      text += String.format('目前損益：{0} ({1}%)<br>', total_gain.toLocaleString(), total_gain_ratio.toLocaleString());
    }
    else {
      text += String.format('損益合計：{0} ({1}%)<br>', total_gain.toLocaleString(), total_gain_ratio.toLocaleString());
    }
    text += '</td></tr>';
    text += '</table>';
    all_total_gain += total_gain;
    all_total_cost += total_stock_cost;
  }

  text += '<hr><div id="DividendForecast"></div>';

  text += '<hr>'
  text += String.format('<div class=total>總損益：{0}</div>', Math.round(all_total_gain).toLocaleString());
  text += String.format('<div class=total>總成本：{0}</div>', Math.round(all_total_cost).toLocaleString());

  $('#result').html(text);

   $.ajax({
    url: 'dividend.py?c=' + stocks_with_qty.join(','),
    dataType: 'json',
    error: onTimeout,
    success: function(data){ updateDividendForecast(data, obj.stocks); },
    timeout: 20000
  });

  return;
}

function parseJSON(obj) {
  console.log(obj);
  updateResult(obj);
}

function onTimeout () {
  console.log('timeout');
}

function updateAccount() {
  $.ajax({
    url: 'load.py?j=account.json',
    dataType: 'json',
    error: onTimeout,
    success: parseJSON,
    timeout: 2000
  });
}

function onDocumentReady() {
  updateAccount();
}

