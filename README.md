# Face Greeter 🎭👋

A real-time face recognition app that greets people by name through text-to-speech and automatically learns new faces.


## Features

- 📷 Detects faces in real time from a webcam
- 👤 Recognizes previously seen faces by name
- 🎙️ Speaks a personalized greeting using offline text-to-speech (`pyttsx3`)
- 🆕 Unknown faces: greets generically, asks for a name, and remembers it for next time
- 🔁 Greets each person once per visit — re-greets only after they leave the frame for 2 seconds
- 💾 Saves face encodings + names locally in SQLite
- 📸 Optional offline enrollment from a photo (`enroll.py`)

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Face detection & encoding | `face_recognition` (built on `dlib`) | Simple high-level API, pre-trained 128-D encodings |
| Camera & video | `opencv-python` | Fast frame capture and drawing overlays |
| Text-to-speech | `pyttsx3` | Offline, no API key, cross-platform |
| Database | `sqlite3` + `pickle` | Zero-setup, file-based, ideal for a local prototype |
| Language | Python 3.10 | Required for `face_recognition` compatibility |

## How It Works

1. Webcam frames are captured with OpenCV.
2. Every 3rd frame is resized to 50% and converted to RGB for speed.
3. `face_recognition` detects faces (HOG detector) and produces a **128-D encoding** for each face.
4. The encoding is compared against known encodings in SQLite using **Euclidean distance** with `tolerance=0.5`.
5. Match found → greets by name using TTS.
6. No match → greets generically, prompts in the terminal for a name, saves the new encoding to `faces.db`, and greets again by the new name.
7. A presence tracker (`ABSENT_TIMEOUT = 2.0`) makes sure each person is greeted **once per visit**, not every frame.

## Setup

```bash
git clone https://github.com/ankit12p/face-greeter.git
cd face-greeter
py -3.10 -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python main.py