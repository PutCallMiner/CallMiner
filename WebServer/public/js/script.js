let audioPlayer = document.getElementById("recording-audio");

function skipToTime(timeInSeconds) {
  audioPlayer.currentTime = timeInSeconds;
  audioPlayer.play()
}

let transcriptEntries = Array.from(
  document.getElementsByClassName("transcript-entry")
);

const entries = transcriptEntries.map((div) => {
  const id = div.id;
  const startTimeMs = parseInt(id.replace('entry-', ''));
  return { div, startTimeMs };
});

entries.sort((a, b) => a.startTimeMs - b.startTimeMs);

let previousIndex = -1;

function updateHighlight() {
  const currentTimeMs = audioPlayer.currentTime * 1000;
  let newIndex = findCurrentIndex(currentTimeMs);
  if (newIndex !== previousIndex) {
    if (previousIndex >= 0) {
      entries[previousIndex].div.classList.remove('highlighted-entry');
    }

    if (newIndex >= 0) {
      entries[newIndex].div.classList.add('highlighted-entry');
      entries[newIndex].div.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    previousIndex = newIndex;
  }
}

function findCurrentIndex(currentTimeMs) {
  let index = -1;
  for (let i = 0; i < entries.length; i++) {
    if (entries[i].startTimeMs <= currentTimeMs) {
      index = i;
    } else {
      break;
    }
  }
  return index;
}

audioPlayer.addEventListener('timeupdate', updateHighlight);
audioPlayer.addEventListener('seeked', updateHighlight);