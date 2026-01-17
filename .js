const API_KEY = "yourapi_key_here"
const MODEL_ID = "eleven_multilingual_v2"; 
const OUTPUT_FOLDER_NAME = "ElevenLabs_MP3s"

-
function generateVoicesFromSheet() {
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (!sheet) {
    Logger.log("No sheet found.");
    return;
  }

  const data = sheet.getDataRange().getValues();
  if (data.length < 2) {
    Logger.log("Sheet has no data.");
    return;
  }

  
  let folderIter = DriveApp.getFoldersByName(OUTPUT_FOLDER_NAME);
  let folder = folderIter.hasNext() ? folderIter.next() : DriveApp.createFolder(OUTPUT_FOLDER_NAME);

  
  const voices = fetchElevenLabsVoices();
  const voiceMap = {};
  voices.forEach(v => voiceMap[v.name] = v.voice_id);

  
  for (let i = 1; i < data.length; i++) {
    const voiceName = data[i][0]; 
    const docUrl = data[i][1];    
    if (!voiceName || !docUrl) continue;

    const voiceId = voiceMap[voiceName];
    if (!voiceId) {
      sheet.getRange(i + 1, 3).setValue(`Voice '${voiceName}' not found`);
      continue;
    }

    const text = fetchGoogleDocText(docUrl);
    if (!text) {
      sheet.getRange(i + 1, 3).setValue("No text found in doc");
      continue;
    }

    try {
      const file = generateMP3(voiceId, text, folder, voiceName);
      sheet.getRange(i + 1, 3).setValue(file.getUrl()); // Column C
    } catch (e) {
      sheet.getRange(i + 1, 3).setValue("ElevenLabs API error: " + e);
    }
  }
}


function fetchElevenLabsVoices() {
  const response = UrlFetchApp.fetch("https://api.elevenlabs.io/v1/voices", {
    method: "get",
    headers: { "xi-api-key": API_KEY },
    muteHttpExceptions: true
  });
  const result = JSON.parse(response.getContentText());
  return result.voices || [];
}

function fetchGoogleDocText(docUrl) {
  const match = docUrl.match(/\/d\/([a-zA-Z0-9_-]+)/);
  if (!match) return "";
  const docId = match[1];
  try {
    const exportUrl = `https://docs.google.com/document/d/${docId}/export?format=txt`;
    const response = UrlFetchApp.fetch(exportUrl, { muteHttpExceptions: true });
    if (response.getResponseCode() !== 200) return "";
    return response.getContentText();
  } catch (e) {
    return "";
  }
}

function generateMP3(voiceId, text, folder, voiceName) {
  const payload = JSON.stringify({ text: text, model_id: MODEL_ID });
  const response = UrlFetchApp.fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
    method: "post",
    contentType: "application/json",
    headers: { "xi-api-key": API_KEY },
    payload: payload,
    muteHttpExceptions: true
  });

  if (response.getResponseCode() !== 200) {
    throw response.getContentText();
  }

  const blob = response.getBlob().setName(`${voiceName}_${new Date().getTime()}.mp3`);
  return folder.createFile(blob);
}