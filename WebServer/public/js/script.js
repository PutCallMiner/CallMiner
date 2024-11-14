function skipToTime(timeInSeconds) {
  let audio = document.getElementById("recording-audio");
  audio.currentTime = timeInSeconds;
  audio.play()
}