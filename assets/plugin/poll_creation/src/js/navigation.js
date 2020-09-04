


/**
 * Show or hide elements for poll creation
 */
function openPollCreation(){
    // console.info("openPollCreation");
    $('#create-body').show();
    $('#create-poll').show();
    $('#edit-poll').hide();
    $('#start-poll').hide();
    // $('#stop-poll').hide();
    $('#timestop-poll').hide();
    $('#activate-poll').hide();
    $('#create-pdf-button').hide();
    $('#update-poll').hide();
    $('#pollIdLabel').hide();
    $('#pollId').hide();
    $('.cloze-id-count').hide();
    $('#source-toggle-lbl').removeClass('is-selected');
    $('#code-preview-settings').hide();
    $('#reset-clozes-button').hide();
    $('#ms-Dropdown-answerView').hide();
}

/**
 * Show or hide elements for poll editing
 */
function openPollEdit(){
    // console.info("openPollEdit");
    $('#code-name').val(ctName);
    $('#create-body').show();
    $('#create-poll').show();
    $('#activate-poll').show();
    $('#edit-poll').hide();
    $('#start-poll').hide();
    // $('#stop-poll').hide();
    $('#timestop-poll').hide();
    $('.cloze-id-count').hide();
    $('#create-pdf-button').hide();
    $('#update-poll').show();
    $('#pollIdLabel').show();
    $('#pollId').show();
    $('#pollId').html(ctId);
    $('#source-toggle-lbl').removeClass('is-selected');
    $('#code-preview-settings').hide();
    $('#reset-clozes-button').hide();
    $('#ms-Dropdown-answerView').hide();
}

/**
 * Show or hide elements for poll preview
 */
function openPollPreview(){
    // console.info("openPollPreview");
	$('#create-body').hide();
    $('#create-poll').hide();
    $('#update-poll').hide();
    $('#edit-poll').show();
    $('#start-poll').hide();
    $('#activate-poll').show();
    // $('#stop-poll').hide();
    $('#timestop-poll').hide();
    $('.cloze-id-count').each(function() { $(this).hide();});
    $('#create-pdf-button').hide();
    $('#source-toggle-lbl').removeClass('is-selected');
    $('#code-preview-settings').show();
    $('#reset-clozes-button').hide();
    $('#pollIdLabel').hide();
    $('#pollId').hide();
    $('#ms-Dropdown-answerView').hide();
}

/**
 * Show or hide elements for poll access
 */
function openPollAccess(){
    // console.info("openPollAccess");
    $('#update-poll').hide();
    $('#create-body').hide();
    $('#create-poll').hide();
    $('#start-poll').hide();
    $('#activate-poll').hide();
    $('#sidebar').empty();
    $('.cloze-id-count').each(function() { $(this).hide();});
    $('.cloze-id-count-running').show();
    // $('#stop-poll').show();
    $('#timestop-poll').show();
    $('#create-pdf-button').show();
    // $('#create-pdf-button').click(pdfPollCreation);
    $("#create-pdf-button").attr("onclick","pdfPollCreation()");
    $('#edit-poll').hide();
    $('#update-poll').hide();
    $('#source-toggle-lbl').removeClass('is-selected');
    $('#code-preview-settings').show();
    $('#reset-clozes-button').hide();
    $('#pollIdLabel').hide();
    $('#pollId').hide();
    $('#ms-Dropdown-answerView').hide();
}

/**
 * Show or hide elements for poll resolution
 */
function openPollResolution(){
    // console.info("openPollResolution");
    $('#create-body').hide();
    $('#spinner').show();
    $('#edit-poll').attr("disabled", false);
    $('#edit-poll').show();
    $('#start-poll').hide();
    $('#activate-poll').show();
    $('#create-poll').hide();
    // $('#stop-poll').hide();
    $('#timestop-poll').hide();
    $('#update-poll').hide();
    
    $('.cloze-id-count').each(function() { $(this).hide();});
    $('.cloze-id-count-stopped').show();
    $('#create-pdf-button').show();
    // $('#create-pdf-button').click(pdfPollResult);
    $("#create-pdf-button").attr("onclick","pdfPollResult()");
    $('#source-toggle-lbl').removeClass('is-selected');
    $('#code-preview-settings').show();
    $('#reset-clozes-button').show();
    $('#pollIdLabel').hide();
    $('#pollId').hide();
    $('#ms-Dropdown-answerView').show();
}


/**
 * Show an alert message
 */
function showError(message){
    alert(message);
}

/**
 * Switches between answer views depend on selected type in answerview-dropdown
 */
function showAnswerViewByType() {
    // console.info("showAnswerViewByType");
    caResultType = $('#answerview-dropdown').val().toLowerCase();
    if (caResultType=="bybundle") {
        $('#answerview-byBundle').show();
        $('#answerview-byEach').hide();
    }
    else if (caResultType=="byeach") {
        $('#answerview-byBundle').hide();
        $('#answerview-byEach').show();
    }
}