
/**
 * Shows the edit poll view
 */
function editPoll() {
    // console.info("editPoll");
    // $('#spinner').show();
    openPollEdit();
    clearTimeout(ctStatusCallTimerId)
    setLanguageToDropdown(ctLanguage);
    setCode(true);
    if (ctId) $('#update-poll').show();
}

/**
 * Shows the access view and activate poll.
 */
function activatePoll(force=true) {
    // console.info("activatePoll");
    $('#spinner').show();
    setCode(false);
    openPollAccess();
    clearInterval(window.intervalSetted);
    if (force) activatePolltAjax();
    ctStatusCallTimerId = setInterval(statusPollAjax, 1000);
}


/**
 * Action to create a poll 
 * (checks if gaps exists and the code is compiling otherwise return to the creation view)
 */
async function createPoll() {
    // console.info("createPoll");
    $('#spinner').show();
    if (!isGapInCloze()) {
        alert("Please use CL{...}ZE to add a gap");
        $('#spinner').hide();
        return;
    }
    var testResult = await testCodeAjax();
    if (testResult != "True")
        if (confirm("Compiling the source code failed or takes too long.\n"
            + "This affects the syntax check of answers!\n"
            + "Continue editing?")) {
            // txt = "You pressed OK!";
            $('#spinner').hide();
            return;
        }
    ctName = $('#code-name').val();
    openPollAccess();
    setCode(false);
    startPolltAjax();
    ctStatusCallTimerId = setInterval(statusPollAjax, 1000);
}
/**
 * Action to update an existing poll 
 * (checks if gaps exists, the count of gaps changed 
 *  and the code is compiling otherwise return to the creation view)
 */
async function updatePoll(){
    // console.info("updatePoll");
    $('#spinner').show();
    if (!isGapInCloze()) {
        alert("Please use CL{...}ZE to add a gap");
        $('#spinner').hide();
        return;
    }
    // console.debug("ctClozeCountOrig vs clozeCount: "+ ctClozeCountOrig+ " vs" + getClozeCount())
    if (ctClozeCountOrig != getClozeCount()){
        var cloze_answer_count = await statusPollAjax();
        if (cloze_answer_count > 0){
            alert("You cannot update gaps of the poll, if the poll is already answered.")
            return;
        }
    }
    var testResult = await testCodeAjax();
    if (testResult != "True")
        if (confirm("Compiling the source code failed or takes too long.\n"
            + "This affects the syntax check of answers!\n"
            + "Continue editing?")) {
            // txt = "You pressed OK!";
            $('#spinner').hide();
            return;
        }
    ctName = $('#code-name').val();
    openPollAccess();
    setCodeLanguage();
    updatePolltAjax();
    setCode(false);
    ctStatusCallTimerId = setInterval(statusPollAjax, 1000);
}
/**
 * Stops the poll and show the resolution view.
 */
function stopPoll() {
    // console.info("stopPoll");
    $('#spinner').show();
    clearTimeout(ctStatusCallTimerId);
    stopPollAjax();
    openPollResolution();
}

/**
 * Creates an intervall to stop the poll in giben time (minutes)
 */
function timestopPoll(durationMin){
    // console.info("timestopPoll");
    $('#timestop-dropdown').removeClass('active');
    // ctStopPollTimer = setInterval()
    if (durationMin == 0){
        stopPoll();
        return;
    }
    // durationMin = $('#timestop-dropdown').val();
    $('#time-till-stop').html(durationMin)
    createProgressbar('progressbarTimer', parseInt(durationMin)*60, function() {
        // alert(durationMin+' min progressbar is finished!');
        stopPoll();
    });
}


/**
 * Creates a pdf slide of the access view
 */
async function pdfPollCreation(){
    // console.info("pdfPollCreation");
    $('#spinner').show();
    // more in PDFcreation.js
    const filename  = 'SCloze_'+ctId+'_'+ctName+'_Creation.pdf';
    var pdf = generatePDFLayout(); // https://html2canvas.hertzen.com/
    // https://itnext.io/javascript-convert-html-css-to-pdf-print-supported-very-sharp-and-not-blurry-c5ffe441eb5e
    await buildLeftSite(pdf);
    await buildRightSiteQrCode(pdf);
    await pdf.save(filename);
    alert("Please check the builded pdf. The quality depends on browser zoom state.");
    $('#spinner').hide();
    // console.info("pdfPollCreation");
}

/**
 * Creates a pdf slide of the resolution view
 */
async function pdfPollResult(){
    // console.info("pdfPollResult");
    // more in PDFcreation.js
    $('#spinner').show();
    var cloze_answer_count = await statusPollAjax();
    $('#spinner').show();
    if (cloze_answer_count <= 0){
        alert("Please wait to have at least one answer to create a PDF file.");
        $('#spinner').hide();
        return;
    }
    $('#spinner').show();
    const filename  = 'SCloze_'+ctId+'_'+ctName+'_Result.pdf';
    var pdf = generatePDFLayout();
    await buildResultPages(pdf, "#answerview");
    await pdf.save(filename);
    alert("Please check the builded pdf. The quality depends on browser zoom state.");
    $('#spinner').hide();
}