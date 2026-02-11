import cv2
import os
import torch
import pyttsx3
import threading
from queue import Queue
from PIL import Image
from gtts import gTTS
from playsound import playsound
import uuid
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from deep_translator import GoogleTranslator
# ---------- CURRENCY IDENTIFICATION PROMPT ----------
CURRENCY_PROMPT = (
    "Identify the Indian currency note in the image. "
    "If it is an Indian rupee note, say ONLY the denomination like "
    "'It is a 10 rupee note', 'It is a 20 rupee note', "
    "'It is a 50 rupee note', 'It is a 100 rupee note', "
    "'It is a 200 rupee note', or 'It is a 500 rupee note'. "
    "If no Indian currency note is visible, say 'No currency note detected'."
)
# ---------- INDIAN CURRENCY COLOR MAP ----------
CURRENCY_COLOR_MAP = {
    "10": "brown",
    "20": "greenish yellow",
    "50": "fluorescent blue",
    "100": "lavender",
    "200": "bright yellow",
    "500": "stone grey"
}
# ---------- COLOR DETECTION ----------
def detect_dominant_color(frame):
    resized = cv2.resize(frame, (200, 200))
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)

    mask = (s > 40) & (v > 40)

    if mask.sum() == 0:
        return "dark"

    mean_hue = int(h[mask].mean())

    if mean_hue < 10 or mean_hue >= 170:
        return "reddish"
    elif mean_hue < 25:
        return "yellowish"
    elif mean_hue < 85:
        return "greenish"
    elif mean_hue < 130:
        return "bluish"
    else:
        return "multicolored"
# ---------- TEXT TO SPEECH (STABLE VERSION) ----------
def speak(text):
    if not text:
        return
    try:
        # Detect Hindi characters
        is_hindi = any('\u0900' <= c <= '\u097F' for c in text)

        # Detect Kannada characters
        is_kannada = any('\u0C80' <= c <= '\u0CFF' for c in text)

        if is_hindi:
            filename = f"voice_{uuid.uuid4().hex}.mp3"
            tts = gTTS(text=text, lang='hi')
            tts.save(filename)
            playsound(filename)
            os.remove(filename)

        elif is_kannada:
            filename = f"voice_{uuid.uuid4().hex}.mp3"
            tts = gTTS(text=text, lang='kn')
            tts.save(filename)
            playsound(filename)
            os.remove(filename)

        else:
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.say(text)
            engine.runAndWait()

    except Exception as e:
        print("TTS Error:", e)
# ---------- TRANSLATION FUNCTION ----------
def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except:
        try:
            return GoogleTranslator(source='en', target=target_lang).translate(text)
        except Exception as e:
            print("Translation error:", e)
            return text
class Moondream:
    def __init__(self, model_id="vikhyatk/moondream2", revision="2024-08-26"):
        print("Loading Moondream model...")
        self.evidence_folder = "captured_evidence"
        if not os.path.exists(self.evidence_folder):
            os.makedirs(self.evidence_folder)   
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                trust_remote_code=True, 
                revision=revision
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
            self.model.eval()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
    def _background_log(self, frame, prompt, response, timestamp):
        """Saves image, audio, and logs data in a background thread."""
        try:
            time_str = timestamp.strftime('%Y%m%d_%H%M%S_%f')
            # Save frame as JPEG
            img_filename = f"capture_{time_str}.jpg"
            img_filepath = os.path.join(self.evidence_folder, img_filename)
            cv2.imwrite(img_filepath, frame)
            # Note: local_engine doesn't strictly need stop() here as it's a local object, 
            # but we ensure it finishes runAndWait().
            # Log to session_log.txt
            log_entry = (
                f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Prompt: {prompt}\n"
                f"Response: {response}\n"
                f"Image Path: {img_filepath}\n"
                f"{'-'*40}\n"
            )
            with open("session_log.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error in background logging: {e}")
    def process_image(self, frame, prompt):
        """Processes the image with AI and triggers background logging."""
        try:
            timestamp = datetime.now()
            # Convert BGR to RGB for PIL
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # AI Inference
            with torch.no_grad():
                enc_image = self.model.encode_image(image)
                response = self.model.answer_question(enc_image, prompt, self.tokenizer)
            # Start background logging thread
            log_thread = threading.Thread(
                target=self._background_log, 
                args=(frame.copy(), prompt, response, timestamp),
                daemon=True
            )
            log_thread.start()
            return response
        except Exception as e:
            print(f"Error during image processing: {e}")
            return f"Error: {e}"
def main():
    try:
        ai = Moondream()
    except Exception:
        return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    print("--------------------------------------------------")
    print("Moondream Webcam Test with Voice & Logging")
    print("--------------------------------------------------")
    print("Press 'SPACE' to capture and describe the frame.")
    print("Press 'a' to describe the scene in English, Hindi, and Kannada.")
    print("Press 't' to read text from the image aloud.")
    print("Press 'c' to identify Indian currency note.")
    print("Press 'q' to quit.")
    print("--------------------------------------------------")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        cv2.imshow('Moondream Webcam Test', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord(' '):
            print("\nCapturing frame and analyzing...")
            description_en = ai.process_image(
                frame,
                "Briefly describe the image in one short sentence in English."
                )
            if description_en.strip() and not description_en.startswith("Error"):
                # Translate to Hindi & Kannada
                description_hi = translate_text(description_en, 'hi')
                description_kn = translate_text(description_en, 'kn')
                print(f"English: {description_en}")
                print(f"Hindi: {description_hi}")
                print(f"Kannada: {description_kn}\n")
                # Speak all three
                speak("English description")
                speak(description_en)
                speak("Hindi description")
                speak(description_hi)
                speak("Kannada description")
                speak(description_kn)
        elif key == ord('a'):
            print("\nCapturing frame and describing in 3 languages...")
            description_en = ai.process_image(
                frame,
                "Briefly describe the image in one short sentence in English."
            )
            if description_en.strip() and not description_en.startswith("Error"):
                description_hi = translate_text(description_en, 'hi')
                description_kn = translate_text(description_en, 'kn')
                print(f"English: {description_en}")
                print(f"Hindi: {description_hi}")
                print(f"Kannada: {description_kn}\n")
                speak("English description")
                speak(description_en)
                speak("Hindi description")
                speak(description_hi)
                speak("Kannada description")
                speak(description_kn)
        elif key == ord('t'):
            print("\nCapturing frame and extracting text...")
            text = ai.process_image(
                frame,
                "Read ONLY the visible text exactly as written. "
                "If the text is Hindi, return it ONLY in Devanagari script (हिंदी अक्षरों में). "
                "Do NOT use English letters for Hindi. Do not repeat words."
                )
            print(f"Text: {text}\n")
            if text.strip() and not text.startswith("Error:"):
                speak(text)
            else:
                speak("No text detected.")
        elif key == ord('c'):
            print("\nCapturing frame and identifying currency note...")
            currency = ai.process_image(frame, CURRENCY_PROMPT)
            color = "unknown"
            words = currency.split()   # split sentence into words
            for word in words:
                if word.isdigit() and word in CURRENCY_COLOR_MAP:
                    color = CURRENCY_COLOR_MAP[word]
                    break

            # ---- GET COLOR FROM DENOMINATION ----
            print(f"Currency: {currency}")
            print(f"Color: {color}\n")
            if currency.strip() and "rupee" in currency.lower():
                final_output = f"{currency}. The color is {color}"
                speak(final_output)
            else:
                speak(f"This is {color} color.")
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()