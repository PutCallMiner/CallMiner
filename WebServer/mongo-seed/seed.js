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

holandia = { name: "Holandia", color: "purple" };
rekomendacja = { name: "Rekomendacja", color: "green" };
rozliczenie = { name: "Rozliczenie", color: "blue" };
niemcy = { name: "Niemcy", color: "orange" };

tags = [
  [holandia, rekomendacja, rozliczenie],
  [niemcy, rozliczenie],
  [holandia],
  [],
  [niemcy],
  [],
  [],
  [],
  [],
  [],
];

recordings = blobs.map((name, index) => {
  const match = name.match(
    /SCCNext_(\d{4}_\d{2}_\d{2})__(\d{2}_\d{2}_\d{2})\.wav/,
  );
  const datePart = match[1].replace(/_/g, "-");
  const timePart = match[2].replace(/_/g, ":");
  const dateTimeISO = `${datePart}T${timePart}Z`;
  const createdAt = new Date(dateTimeISO);

  return {
    blob_name: name,
    transcript: null,
    summary: null,
    speaker_mapping: null,
    duration: null,
    ner: null,
    conformity: null,
    created: createdAt,
    agent: {
      id: 0,
      name: "Ewelina",
      email: "ewelina@eurotax.pl",
    },
    tags: tags[index],
  };
});

db = db.getSiblingDB("callminer");
db.recordings.insertMany(recordings);
