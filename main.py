import cv2
import face_recognition
import pyttsx3
import time

from db import load_faces, save_face

# ---------------- Text-to-speech ----------------
def speak(text):
    """Create a fresh engine each call to avoid the pyttsx3 stuck-after-one bug."""
    print(f"[SPEAK] {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        voices = engine.getProperty("voices")
        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"[TTS ERROR] {e}")


# ---------------- Load known faces ----------------
known_names, known_encodings = load_faces()
print(f"Loaded {len(known_names)} known face(s): {known_names}")

# ---------------- Camera ----------------
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    raise RuntimeError("Cannot open webcam. Check camera index or permissions.")

# ---------------- State ----------------
# present: name -> last time seen. A name is "present" while it keeps being
# detected. If it is not seen for ABSENT_TIMEOUT seconds, it is removed,
# and the next time it appears it will be greeted again.
present = {}
ABSENT_TIMEOUT = 2.0

# After skipping the name prompt, wait this long before asking again
skip_unknown_until = 0

frame_count = 0
PROCESS_EVERY = 3


def cleanup_absent(seen_this_frame):
    """Drop names not seen for ABSENT_TIMEOUT seconds."""
    now = time.time()
    for name in list(present.keys()):
        if name not in seen_this_frame and now - present[name] > ABSENT_TIMEOUT:
            del present[name]


def greet_known(name):
    """Greet only when the person transitions absent -> present."""
    if name in present:
        # Already greeted this visit; just refresh last-seen time.
        present[name] = time.time()
        return
    # New appearance -> greet once and mark present.
    present[name] = time.time()
    speak(f"Hello {name}, nice to see you again!")


def greet_and_enroll(encoding):
    """Unknown face: greet, ask name, save, greet by name."""
    global skip_unknown_until
    speak("Hello there! I don't think we have met before.")
    new_name = input(">>> Please enter your name (blank to skip): ").strip()

    if not new_name:
        speak("Alright, maybe next time.")
        skip_unknown_until = time.time() + 30
        return

    if new_name in known_names:
        speak(f"Okay, I will call you {new_name}.")
        present[new_name] = time.time()
        return

    save_face(new_name, encoding)
    known_names.append(new_name)
    known_encodings.append(encoding)
    present[new_name] = time.time()
    speak(f"Nice to meet you, {new_name}! I will remember you.")


# ---------------- Main loop ----------------
while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    frame_count += 1

    if frame_count % PROCESS_EVERY == 0:
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        # Scale back to original frame (factor 2)
        scaled = [(t * 2, r * 2, b * 2, l * 2) for (t, r, b, l) in face_locations]

        seen_this_frame = set()

        for (top, right, bottom, left), encoding in zip(scaled, face_encodings):
            name = "Unknown"
            color = (0, 0, 255)

            if known_encodings:
                matches = face_recognition.compare_faces(
                    known_encodings, encoding, tolerance=0.5
                )
                if True in matches:
                    idx = matches.index(True)
                    name = known_names[idx]
                    color = (0, 255, 0)
                    greet_known(name)
                    seen_this_frame.add(name)

            if name == "Unknown" and time.time() > skip_unknown_until:
                greet_and_enroll(encoding)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame, name, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2,
            )

        cleanup_absent(seen_this_frame)

    cv2.imshow("Face Greeter - press Q to quit", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()