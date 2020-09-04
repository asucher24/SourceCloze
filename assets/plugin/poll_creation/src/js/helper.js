
/**
 * Fill an integer with leading zeros till number of chars is euqal to given size
 */
Number.prototype.pad = function(size) {
    var s = String(this);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
};

/**
 * Helper Function to use in html to check if strings are equal
 */
Handlebars.registerHelper('if_eq', function(a, b, opts) {
    if (a == b) {
        return opts.fn(this);
    } else {
        return opts.inverse(this);
    }
});

/**
 * decodes quotes in string
 */
function replaceQuotes(str){
    // https://gist.github.com/getify/3667624
    return str.replace(/\\([\s\S])|(")/g,"\\$1$2"); // thanks @slevithan!
}

/**
 * Checks whenever there is a gap in the source code cloze test
 */
function isGapInCloze(){
    var regex = /(CL\{)(.*?)(\}ZE)/gi;
    var matches = $('#code-text').val().match(regex);
    if (matches == null) 
        return false
    return true
}

/**
 * Set code size.
 */
function setCodeSize() {
    var codeSize = $('#code-size-slider').val();
    $('#body').css("font-size", codeSize.toString() + "pt");
    setCode();
}

/**
 * Returns count of gaps in cloze test
 */
function getClozeCount(){
    var count = 0;
    $('.token.cloze').each(function(index) {
        count += 1;
    });
    return count.toString();
}

/**
 * Returns count of gaps in cloze test, 
 * but also resplace it to "   #x   " where x is the number of the cloze
 */
function getClozeCountAndTransform(){
    var count = 0;
    $('.token.cloze').each(function(index) {
        count += 1;
        $(this).text("    #" + (count) + "    ");
    });
    return count.toString();
}

/**
 * Helper function for fill in single gap answer in cloze test on click action.
 */
function fillCloze(clozeNum, clozeCode ) {
    var domElementCloze = $('.token.cloze').get(parseInt(clozeNum.replace("#",""))-1);
    domElementCloze.textContent = ' ' + clozeCode + ' ';
}

/**
 * Helper function for fill in answers in cloze test on click action.
 */
function fillClozes(ClozeAnswers) {
    $('.token.cloze').each(function(index) {
        $(this).text(' ' + $(ClozeAnswers[index]).text() + ' ');
    });
}

/**
 * Resets the content of gaps
 */
function resetCloze() {
    $('.token.cloze').each(function(index) {
        $(this).text('    #' + (index+1) + '    ');
    });
}

/**
 * Returns the element outside the {SOURCE} and {SOURCEEND} tags
 */
function elementsOutsideSource(){
    return $(".token.source-tag1,.token.source-tag2");
}
/**
 * Change the visibility of the element outside the {SOURCE} and {SOURCEEND} tags
 */
function changeSourceVisibility(){
    elementsOutsideSource().each(function(index) {
        $(this).toggle();
        Prism.highlightElement($(this)[0]);
    });
}

/**
 * Sets the local data to the given poll information 
 */
function setPollInfos(data){
    ctCode = data.cloze_test;
    ctName = data.cloze_name;
    ctClozeCount = data.cloze_count;
    ctClozeCountOrig = data.cloze_count;
    ctLanguage = data.language;
    $('#code-text').val(ctCode);
    $('#sidebar').empty();
    setLanguageToDropdown(ctLanguage);
    setCode(false);
}
/**
 * Highlight code for all prism elements.
 */
function highlightCode() {
    $('code[class^="language-"]').each(function(index) {
        Prism.highlightElement($(this)[0]);
    });
}

/**
 * Highligts also in/visible {SOURCE}/{SOURCEEND} elements
 */
function highlightMainCode(){
    Prism.highlightElement($('#code-view')[0]);
    highlightCode();
    sourceVisible = $('#source-toggle-lbl').hasClass('is-selected')
    if (sourceVisible){
        elementsOutsideSource().each(function(index) {
            Prism.highlightElement($(this)[0]);
            $(this).show();
        });
    }else{
        elementsOutsideSource().each(function(index) {$(this).hide();});
    }
}
