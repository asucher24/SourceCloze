$(document).ready(() => {
    fetchCloze();
    $('.sortable').click(function(){
        var table = $(this).parents('table').eq(0)
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
        this.asc = !this.asc
        if (!this.asc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
    });
    if ($(document).width() > 479)
        $('.details-vote').attr('open', "")
});
function fetchCloze(){
    var count = 1;
    $('#code-view > .token.cloze').each(function(index) {
        $(this).text("    #" + (count++) + "    ");
    });
    
    $('#code-oview > .token.cloze').each(function(index) {
        var txt = $(this).html().replace(/(CL\{)|(\}ZE)/gi, "");
        $(this).text(' ' + txt + ' ');
    });
}

function comparer(index) {
    return function(a, b) {
        var valA = getCellValue(a, index), valB = getCellValue(b, index)
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB.toString())
    }
}
function getCellValue(row, index){ return $(row).children('td').eq(index).attr('data-value') }

