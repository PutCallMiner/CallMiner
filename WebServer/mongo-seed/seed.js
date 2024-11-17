blobs = [
  "SCCNext_2024_04_17__15_39_40.wav",
  "SCCNext_2024_04_17__15_40_33.wav",
  "SCCNext_2024_04_17__15_40_48.wav",
  "SCCNext_2024_04_17__15_41_02.wav",
  "SCCNext_2024_04_17__15_41_17.wav",
  "SCCNext_2024_04_17__15_41_32.wav",
  "SCCNext_2024_04_17__15_41_52.wav",
  "SCCNext_2024_04_17__15_42_11.wav",
  "SCCNext_2024_04_17__15_42_32.wav",
  "SCCNext_2024_04_17__15_42_52.wav",
];

recordings = blobs.map((name) => ({
  blob_name: name,
  transcript: null,
  summary: null,
  speaker_mapping: null,
  duration: null,
  ner: null,
  conformity: null,
}));

db = db.getSiblingDB("callminer");
db.recordings.insertMany(recordings);
