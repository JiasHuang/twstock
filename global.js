
function updateResult(obj) {

  var text = '';

  for (const [k, v] of Object.entries(obj)) {
    text += `<h4 align="center">${k} ${v}</h4>`;
    text += `<img src="loadpng.py?c=${k}">`;
  }

  $('#result').html(text);
}

function updateStockInfo() {
  console.log('updateStockInfo');
  $.ajax({
    url: 'load.py?n=global',
    dataType: 'json',
    success: updateResult,
  });
}

function onDocumentReady() {
  loadTopMenu();
  updateStockInfo();
}

