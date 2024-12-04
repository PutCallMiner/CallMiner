const audioPlayer = document.getElementById("recording-audio");
let entries = [];
let previousIndex = -1;

function skipToTime(time) {
  audioPlayer.currentTime = time / 1000;
  highlight(undefined, time);
}

function togglePlayback() {
  if (audioPlayer.paused) {
    audioPlayer.play();
  } else {
    audioPlayer.pause();
  }
}

function setupEntries() {
  console.log("Setting up");
  let transcriptEntries = Array.from(
    document.getElementsByClassName("transcript-entry"),
  );

  entries = transcriptEntries.map((div) => {
    const id = div.id;
    const startTimeMs = parseInt(id.replace("entry-", ""));
    return { div, startTimeMs };
  });

  entries.sort((a, b) => a.startTimeMs - b.startTimeMs);
  previousIndex = -1;
}

function highlight(_, entryTime) {
  if (entries.length === 0) {
    setupEntries();
  }

  function findCurrentIndex() {
    const currentTimeMs = audioPlayer.currentTime * 1000;
    let low = 0;
    let high = entries.length - 1;
    let index = -1;

    while (low <= high) {
      let mid = Math.floor((low + high) / 2);
      if (entries[mid].startTimeMs <= currentTimeMs) {
        index = mid;
        low = mid + 1;
      } else {
        high = mid - 1;
      }
    }

    return index;
  }

  const newIndex =
    entryTime !== undefined
      ? entries.findIndex((e) => e.startTimeMs === entryTime)
      : findCurrentIndex();

  if (newIndex === previousIndex) return;

  if (previousIndex >= 0) {
    entries[previousIndex].div.classList.remove("highlighted");
  }

  if (newIndex >= 0) {
    entries[newIndex].div.classList.add("highlighted");
    entries[newIndex].div.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }

  previousIndex = newIndex;
}

function pulse(id) {
  const entry = document.getElementById(id);
  const container = entry.parentElement;

  function pulseEntry() {
    entry.classList.add("pulse");
    setTimeout(() => {
      entry.classList.remove("pulse");
    }, 1000);
  }

  if (entry.classList.contains("pulse")) {
    return;
  }

  if (
    entry.offsetTop > container.scrollTop + container.clientHeight ||
    entry.offsetTop < container.scrollTop
  ) {
    entry.scrollIntoView({ behavior: "smooth", block: "center" });

    container.addEventListener("scrollend", pulseEntry, { once: true });
  } else {
    pulseEntry();
  }
}

setupEntries();
audioPlayer.addEventListener("timeupdate", highlight);
audioPlayer.addEventListener("seeked", highlight);
document.addEventListener("keydown", function (event) {
  if (event.code === "Space" || event.key === " ") {
    event.preventDefault();
    togglePlayback();
  } else if (event.code === "ArrowLeft") {
    event.preventDefault();
    audioPlayer.currentTime = audioPlayer.currentTime - 5;
  } else if (event.code === "ArrowRight") {
    event.preventDefault();
    audioPlayer.currentTime = audioPlayer.currentTime + 5;
  }
});
