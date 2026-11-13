import sys
import face_recognition
from db import save_face

if len(sys.argv) != 3:
    print('Usage: python enroll.py <photo.jpg> "<Name>"')
    sys.exit(1)

photo_path, person_name = sys.argv[1], sys.argv[2]
image = face_recognition.load_image_file(photo_path)
encodings = face_recognition.face_encodings(image)

if not encodings:
    print("ERROR: No face detected in the photo.")
    sys.exit(1)

save_face(person_name, encodings[0])
print(f"Done. '{person_name}' is now registered.")