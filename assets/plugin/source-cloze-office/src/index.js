$(document).ready(() => {
    // action buttons
    $('#create-poll-button').click(createPoll);
    $('#edit-poll-button').click(editPoll);
    $('#start-poll-button').click(startPoll);
    $('#stop-poll-button').click(stopPoll);
    // edit tools
    $('#language-dropdown').change(setCode);
    $('#code-text').bind('input propertychange', setCode)
    $('#demo-toggle-3').change(setCode);
    $('#code-size-slider').change(setCodeSize);
    setCode();
    // Language dropdown
    var DropdownHTMLElements = document.querySelectorAll('.ms-Dropdown');
    for (var i = 0; i < DropdownHTMLElements.length; i++) {
        var Dropdown = new fabric['Dropdown'](DropdownHTMLElements[i]);
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
    // Create poll button
    $('#edit-poll').hide();
    $('#start-poll').hide();
    $('#stop-poll').hide();
});

// The initialize function must be run each time a new page is loaded
Office.initialize = (reason) => {

};

var ctId = ''
var ctCode = ''
var ctClozeCount = ''
var ctLanguage = 'python'

/**
 * Switch to edit state.
 */
function editPoll() {
    setCode(true);
    $('#create-body').show();
    $('#create-poll').show();
    $('#edit-poll').hide();
    $('#start-poll').hide();
}

/**
 * Switch to preview state.
 */
function createPoll() {
    setCode(false);
    $('#create-body').hide();
    $('#create-poll').hide();
    $('#sidebar').empty();
    $('#edit-poll').show();
    $('#start-poll').show();
}

/**
 * Switch to access state.
 */
function startPoll() {
    $('#edit-poll').attr("disabled", true);
    $('#start-poll').hide();
    $('#stop-poll').show();
    startPolltAjax();
}

/**
 * Switch to result state.
 */
function stopPoll() {
    $('#edit-poll').attr("disabled", false);
    $('#start-poll').show();
    $('#stop-poll').hide();
    stopPollAjax();
}

/**
 * Send ajax-call to the application for participation to start poll
 */
function startPolltAjax() {
    $.ajax({
        url: 'https://cloze.jglod.de/start-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_test': ctCode,
                              'cloze_count': ctClozeCount,
                              'language': ctLanguage}),
        contentType: 'application/json',
        success: function(data) {
            ctId = data.cloze_test_id;
            showClozeId();
        },
        error: function(e) {
            console.log(e.message);
        }
    });
}

/**
 * Send ajax-call to the application for participation to stop poll.
 */
function stopPollAjax() {
    $.ajax({
        url: 'https://cloze.jglod.de/stop-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_test_id': ctId}),
        contentType: 'application/json',
        dataType: 'json',
        success: function(data) {
            showAnswer(data);
        },
        error: function(e) {
            console.log(e.message);
        }
    });
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
 * Set language main code element.
 */
function setLanguage() {
    ctLanguage = $('#language-dropdown').val().toLowerCase();
    $('code[class^="language-"]').each(function(index) {
        $(this).attr("class", "language-" + ctLanguage);
    });
    highlightCode();
    $('#code-view').attr("class", "language-" + ctLanguage);
    Prism.highlightElement($('#code-view')[0]);
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
 * Take the code from the input field. Manipulate gaps from gap text.
 * Highligth syntax.
 * @param {boolean} edit If the cloze test in in edit mode
 */
function setCode(edit=true) {
    showSolution();
    setLanguage();
    var regex = /(CL\{)((?!(\}ZE)).)*(\}ZE)/gi;
    if (edit) {
        if (!$('#demo-toggle-3').prop('checked')) {
            var codeText = $('#code-text').val().replace(regex, function(){return "CL{ }ZE";});
        } else {
            var codeText = $('#code-text').val().replace(/(CL\{)|(\}ZE)/gi, "");
        }
    } else {
        var codeText = $('#code-text').val().replace(regex, function(){return "CL{ }ZE";});
    }
    $('#code-view').text(codeText);
    Prism.highlightElement($('#code-view')[0]);
    highlightCode();
    var count = 0;
    $('.token.cloze').each(function(index) {
        count += 1;
        $(this).text("    #" + (count) + "    ");
    });
    ctCode = $('#code-text').val();
    ctClozeCount = count.toString();
}

/**
 * Extract the answers from the clozes and place them in a solution field.
 */
function showSolution() {
    var matchRegex = /(CL\{)(.*?)(\}ZE)/gi;
    var replaceRegex = /(CL\{)|(\}ZE)/gi;
    var matches = $('#code-text').val().match(matchRegex);
    if (matches == null) {
        $('#sidebar').empty();
    } else {
        var ClozeElements = Array.from(matches);
        var answerText = '{\"language\":\"' + ctLanguage + '\",\"clozes\": [';
        for (var i = 0; i < ClozeElements.length; i++) {
            if (i > 0) {
                answerText += ',{\"nr\":\"#' + (i+1) + '\",\"code\":\"' + ClozeElements[i].replace(replaceRegex, "") + '\"}';
            } else {
                answerText += '{\"nr\":\"#' + (i+1) + '\",\"code\":\"' + ClozeElements[i].replace(replaceRegex, "") + '\"}';
            }
        }
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
    var idTemplate = $('#idTmpl').html();
    var idTemplateScript = Handlebars.compile(idTemplate);
    var idHtml = idTemplateScript({'cloze_test_id': ctId});
    $('#sidebar').empty();
    $('#sidebar').append(idHtml);
    var qrcodeSize = Math.floor($('#id-info-box').width() * 3 / 4);
    var qrcode = new QRCode(document.getElementById('qrcode'), {
    	text: 'https://cloze.jglod.de/id/' + ctId,
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
    var template = $('#contentTmpl').html();
    var templateScript = Handlebars.compile(template);
    var html = templateScript(answers);
    $('#sidebar').empty();
    $('#sidebar').append(html);
    $('.answer-field').each(function(index) {
        $(this).click(function(event) {
            event.preventDefault();
            var ClozeAnswers = $(this).find('code');
            fillClozes(ClozeAnswers);
        });
    });
    highlightCode();
}

/**
 * Helper function for fill in answers in cloze test on click action.
 */
function fillClozes(ClozeAnswers) {
    $('.token.cloze').each(function(index) {
        $(this).text(' ' + $(ClozeAnswers[index]).text() + ' ');
    });
}
