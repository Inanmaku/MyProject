import requests
import csv
import re
import io


API_KEY = "e2f631d110de2146392a6556169849304dde4f663d18f492c68bde28df470864"  
CSV_FILE = "scripts.csv"             
MODEL_ID = "eleven_multilingual_v2" 


def get_doc_text(doc_url):
    """Fetch plain text from a Google Doc."""
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", doc_url)
    if not match:
        print(f" Invalid Google Doc URL: {doc_url}")
        return ""
    doc_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    r = requests.get(export_url)
    if r.status_code != 200:
        print(f" Failed to fetch doc {doc_id}: HTTP {r.status_code}")
        return ""
    return r.text

def generate_speech(voice_id, text, filename):
    """Generate MP3 from ElevenLabs TTS API."""
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": MODEL_ID}
    )
    if r.status_code == 200:
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f" Saved {filename}")
    else:
        print(f" Error generating voice: {r.text}")

def safe_filename(name):
    """Convert text into a safe filename."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


def main():
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if row.get("voice_name") and row.get("doc_link")]

    print(f"Processing {len(rows)} rows...\n")

    
    voices_resp = requests.get("https://api.elevenlabs.io/v1/voices",
                               headers={"xi-api-key": API_KEY})
    voices_resp.raise_for_status()
    voices = voices_resp.json().get("voices", [])
    voice_map = {v["name"]: v["voice_id"] for v in voices}

    for idx, row in enumerate(rows, start=1):
        voice_name = row["voice_name"]
        doc_link = row["doc_link"]
        print(f"--- Row {idx} ---")

        voice_id = voice_map.get(voice_name)
        if not voice_id:
            print(f" Voice '{voice_name}' not found. Skipping.")
            continue

        text = get_doc_text(doc_link)
        if not text.strip():
            print(f" No text found in document: {doc_link}. Skipping.")
            continue

        filename = f"output_{safe_filename(voice_name)}_{safe_filename(doc_link[-10:])}.mp3"
        print(f" Generating voice '{voice_name}' for doc: {doc_link}...")
        generate_speech(voice_id, text, filename)

    print("\n All done! Check your folder for the generated MP3 files.")

if __name__ == "__main__":
    main()
