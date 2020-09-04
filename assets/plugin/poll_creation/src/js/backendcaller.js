
/**
 * Send ajax-call to the application for test the source code
 */
async function testCodeAjax() {
    // console.info("startPolltAjax");
    var result;
    await $.ajax({
        url: '/api/test-code/',
        type: 'POST',
        data: JSON.stringify({//'cloze_name': $('#code-name').val(),
                              'cloze_test': ctCode,
                              //'cloze_count': ctClozeCount,
                              'language': ctLanguage
                          }),
        contentType: 'application/json',
        error: function(e) {console.error(e);showError(e.responseText);},
        success: function(data) {
            result = data.result;
            return result;
        },
    });
    return result;
}

/**
 * Send ajax-call to the application to create and start poll
 */
function startPolltAjax() {
    // console.info("startPolltAjax");
    $.ajax({
        url: '/api/start-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_name': $('#code-name').val(),
                              'cloze_test': ctCode,
                              'cloze_count': ctClozeCount,
                              'language': ctLanguage}),
        contentType: 'application/json',
        error: function(e) {console.error(e);showError(e.responseText);},
        success: function(data) {
            ctId = data.cloze_test_id;
            showClozeId();
            ctClozeCountOrig = ctClozeCount;
            $('#spinner').hide();
        },
    });
}


/**
 * Send ajax-call to the application to update a poll
 */
function updatePolltAjax(){
    // console.info("updatePolltAjax");
    $.ajax({
        url: '/api/update-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_test_id': ctId,
                              'cloze_name': ctName,
                              'cloze_test': ctCode,
                              'cloze_count': ctClozeCount,
                              'active': true,
                              'language': ctLanguage}),
        contentType: 'application/json',
        error: function(e) {console.error(e);showError(e.responseText);},
        success: function(data) {
            showClozeId();
            $('#spinner').hide();
        },
    });
}


/**
 * Send ajax-call to the application to update the result of syntax check for specifix single answer
 */
function updatePollAnswerAjax(type, num, answer, result){
    $.ajax({
        url: '/api/update-answer-result/',
        type: 'POST',
        data: JSON.stringify({'cloze_test_id': ctId,
                              'cloze_answer': answer,
                              'answer_type': type,
                              'answer_num': num,
                              'syntaxresult': result}),
        contentType: 'application/json',
        error: function(e) {console.error(e);showError(e.responseText);},
        success: function(data) {
            $('#answerview-dropdown').val("byEach")
            setPollInfos(data.poll)
            statusPollAjax();
            showAnswer(data);
            showAnswerViewByType();
            $('#spinner').hide();
        },
    });
}


/**
 * Send ajax-call to the application for (re-)activation of poll
 */
function activatePolltAjax() {
    // console.info("activatePolltAjax");
    $.ajax({
        url: '/api/activate-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_test_id': ctId}),
        contentType: 'application/json',
        error: function(e) { console.error(e);showError(e.responseText); },
        success: function(data) { setPollInfos(data); showClozeId(); 
            $('#spinner').hide();},
    });
}


/**
 * Send ajax-call to the application to receive the current number of answers for a poll
 */
async function statusPollAjax() {
    // console.info("statusPollAjax");
    var count;
    await $.ajax({
        url: '/api/status-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_test_id': ctId}),
        contentType: 'application/json',
        dataType: 'json',
        error: function(e) {console.error(e);showError(e.responseText);},
        success: function(data) {
            $('#cloze-id-count-running').html(data.cloze_answer_count)
            $('#cloze-id-count-stopped').html(data.cloze_answer_count)
            // console.debug("current answers: "+data.cloze_answer_count)
            count = data.cloze_answer_count;
            $('#spinner').hide();
            return count;
        },
    });
    return count;
}


/**
 * Send ajax-call to the application for participation to stop poll and calculate the answers.
 */
function stopPollAjax() {
    // console.info("stopPollAjax");
    $.ajax({
        url: '/api/stop-poll/',
        type: 'POST',
        data: JSON.stringify({'cloze_test_id': ctId}),
        contentType: 'application/json',
        dataType: 'json',
        error: function(e) {console.log(e.message);showError(e.responseText);},
        success: function(data) {
            $('#answerview-dropdown').val("byBundle")
            setPollInfos(data.poll)
            statusPollAjax();
            showAnswer(data);
            showAnswerViewByType();
            $('#spinner').hide();
        },
    });
}
