
var ctId = '';
var ctAnswers = {};
var ctCode = '';
var ctClozeCountOrig = '';
var ctClozeCount = '';
var ctLanguage = 'python';
var ctName = 'Print-Poll';
var caResultType = 'byBundle';
var ctStatusCallTimerId = null;
var ctStopPollTimer = null;
var intervalSetted = null;

/**
 * Init all elements
 */
function setupGui(){
    // console.info("SetupGui");
    highlightMainCode();
    initMSComponents();
    initComponentsEvents();
    // Set the correct ctLanguage as DropdownText
    setLanguageToDropdown(ctLanguage);
    setCodeLanguage();
    $('#spinner').hide();
}

/**
 * Set language to dropdown element
 */
function setLanguageToDropdown(language) {
    // console.info("setLanguageToDropdown");
    let ctLanguageTxt = $("#language-dropdown option[val='"+language+"']").val();
    $("#language-dropdown").val(ctLanguageTxt)
    // console.debug("Set language to dropdown: " + ctLanguageTxt)
}

/**
 * Set local language from dropdown element
 */
function setCodeLanguage() {
    // console.info("setCodeLanguage");
    ctLanguage = $('#language-dropdown').val().toLowerCase();
    $('code[class^="language-"]').each(function(index) {
        $(this).attr("class", "language-" + ctLanguage);
    });
    highlightCode();
    $('#code-view').attr("class", "language-" + ctLanguage);
    highlightMainCode();
}


/**
 * Take the code from the input field. Manipulate gaps from gap text.
 * Highligth syntax.
 * @param {boolean} edit If the cloze test in in edit mode
 */
function setCode(edit=true) {
    // console.info("setCode edit " +edit);
    showSolution();
    setCodeLanguage();
    var regex = /(CL\{)((?!(\}ZE)).)*(\}ZE)/gi;
    var codeText = $('#code-text').val().replace(regex, function(){return "CL{ }ZE";});
    if (edit && $('#cloze-toggle-lbl').hasClass('is-selected')) {
        codeText = $('#code-text').val().replace(/(CL\{)|(\}ZE)/gi, "");
    }
    $('#code-view').text(codeText);
    ctCode = $('#code-text').val();
    highlightMainCode();
    ctClozeCount = getClozeCountAndTransform();
}
/**
 * Extract the answers from the clozes and place them in a solution field.
 */
function showSolution() {
    // console.info("showSolution");
    var matchRegex = /(CL\{)(.*?)(\}ZE)/gi;
    var replaceRegex = /(CL\{)|(\}ZE)/gi;
    var matches = $('#code-text').val().match(matchRegex);
    if (matches == null) {
        $('#sidebar').empty();
    } else {
        var ClozeElements = Array.from(matches);
        var answerText = '{\"language\":\"' + ctLanguage + '\",\"clozes\": [';
        for (var i = 0; i < ClozeElements.length; i++) {
            answerText += '{\"nr\":\"#' + (i+1) + '\",\"code\":\"' + replaceQuotes(ClozeElements[i].replace(replaceRegex, "")) + '\"},';
        }
        answerText = answerText.substring(0, answerText.length - 1);
        answerText += ']}';

        var answerContext = JSON.parse(answerText);
        var answerTemplate = $('#answerTmpl').html();
        var answerTemplateScript = Handlebars.compile(answerTemplate);
        var answerHtml = answerTemplateScript(answerContext);
        $('#sidebar').empty();
        $('#sidebar').append(answerHtml);
    }
}
/**
 * Generate QR-code. Fill in template with cloze test id and url.
 */
function showClozeId() {
    // console.info("showClozeId");
    var idTemplate = $('#idTmpl').html();
    var idTemplateScript = Handlebars.compile(idTemplate);
    var idHtml = idTemplateScript({'cloze_test_id': ctId});
    $('#sidebar').empty();
    $('#sidebar').append(idHtml);
    var qrcodeSize = Math.floor($('#id-info-box').width() * 3 / 4);
    var qrcode = new QRCode(document.getElementById('qrcode'), {
    	text: url_id + ctId,
    	width: qrcodeSize,
    	height: qrcodeSize,
    	colorDark : '#444444',
    	colorLight : '#ffffff',
    	correctLevel : QRCode.CorrectLevel.H
    });
}

/**
 * Fill in template with answers for cloze test.
 */
function showAnswer(answers) {
    // console.info("showAnswer");
    ctAnswers = answers
    var template = $('#contentTmpl').html();
    var templateScript = Handlebars.compile(template);
    // console.debug("Answers:" + JSON.stringify(answers))
    showAnswerViewByType();
    var html = templateScript(answers);
    $('#sidebar').empty();
    $('#sidebar').append(html);
    $('.answer-field-bundle').each(function(index) {
        $(this).click(function(event) {
            event.preventDefault();
            var ClozeAnswers = $(this).find('code');
            fillClozes(ClozeAnswers);
        });
    });
    highlightCode();
}


/**
 * Init all MS Office Components (used also in non office application)
 */
function initMSComponents(){
    // console.info("initMSComponents");
    // Language dropdown
    var DropdownHTMLElementsLanguage = document.querySelectorAll('#ms-Dropdown-language');
    for (var i = 0; i < DropdownHTMLElementsLanguage.length; i++) {
        var DropdownLanguage = new fabric['Dropdown'](DropdownHTMLElementsLanguage[i]);
    }
    // AnswerView dropdown
    var DropdownHTMLElementsAnswerView = document.querySelectorAll('#ms-Dropdown-answerView');
    for (var i = 0; i < DropdownHTMLElementsAnswerView.length; i++) {
        var DropdownAnswerView = new fabric['Dropdown'](DropdownHTMLElementsAnswerView[i]);
    }
    // Source code input
    var TextFieldElements = document.querySelectorAll('.ms-TextField');
    for (var i = 0; i < TextFieldElements.length; i++) {
        new fabric['TextField'](TextFieldElements[i]);
    }
    // Cloze toggle
    var ToggleElements = document.querySelectorAll('.ms-Toggle');
    for (var i = 0; i < ToggleElements.length; i++) {
        new fabric['Toggle'](ToggleElements[i]);
    }
}

/**
 * Init events of elements
 */
function initComponentsEvents(){
    // poll action buttons
    $('#reset-clozes-button').click(resetCloze);
    $('#create-poll-button').click(createPoll);
    $('#update-poll-button').click(updatePoll);
    $('#edit-poll-button').click(editPoll);
    $('#activate-poll-button').click(activatePoll);
    $("#timestop-poll-button").click(function(){$('#timestop-dropdown').toggleClass('active');});
    // $('#stop-poll-button').click(stopPoll);
    // poll edit actions
    $('#language-dropdown').change(setCode);
    $('#answerview-dropdown').change(showAnswerViewByType);
    $('#code-text').bind('input propertychange', setCode)
    $('#cloze-toggle').change(setCode);
    $('#source-toggle').change(changeSourceVisibility);
    $('#code-size-slider').change(setCodeSize);
}