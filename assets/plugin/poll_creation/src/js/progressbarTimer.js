/*
 *  Creates a progressbar.
 *  @param id the id of the div we want to transform in a progressbar
 *  @param duration the duration of the timer example: '10s'
 *  @param callback, optional function which is called when the progressbar reaches 0.
 */
function createProgressbar(id, duration, callback) {
  clearInterval(window.intervalSetted);
  
  var progressbar = document.getElementById(id);
  progressbar.className = 'progressbar';
  // We create the div that changes width to show progress
  $('#timeanimation').remove();
  var progressbarinner = document.createElement('div');
  progressbarinner.id = "timeanimation"
  progressbarinner.className = 'inner';
  
  // Now we set the animation parameters
  progressbarinner.style.animationDuration = duration + "s";

  // Append the progressbar to the main progressbardiv
  progressbar.appendChild(progressbarinner);
  
  // Start running time counter
  var start = Date.now();
  $('#time-till-stop').show();
  
  function timer() {
    var diff = duration - (((Date.now() - start) / 1000) | 0);
    var minutes = (diff / 60) | 0;
    var seconds = (diff % 60) | 0;
    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;
    $('#time-till-stop').html(minutes + ":" + seconds);
    if (diff <= 0) {
      $('#time-till-stop').html("00:00");
      clearInterval(window.intervalSetted);
      // Eventually couple a callback
      if (typeof(callback) === 'function') {
        callback();
      }
    }
  }
  timer();
  window.intervalSetted = setInterval(timer, 1000);
  // When everything is set up we start the animation
  progressbarinner.style.animationPlayState = 'running';
}