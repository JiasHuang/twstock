
function updateResult(obj) {

  var text = '';

  for (const [k, v] of Object.entries(obj)) {
    text += `<h4 align="center"><a href="report.html?c=${k}" target="_blank">${k} ${v}</a></h4>`;
    text += `<img src="loadpng.py?c=${k}">`;
  }

  $('#result').html(text);
}

function updateStockInfo() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const q = urlParams.get('q');

  $.ajax({
    url: 'load.py?n=code&q='+q,
    dataType: 'json',
    success: updateResult,
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
}

