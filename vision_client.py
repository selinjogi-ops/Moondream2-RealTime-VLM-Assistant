import time
import json
import base64
import datetime
import subprocess
import requests
import os# REMOVED: from gpiozero import Button (Not needed anymore)
import cv2
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# --- CONFIGURATION ---
LLAMA_SERVER_URL = "http://localhost:8080/completion"
LOG_DIR = "history_logs"
VOICE_MODEL = "/home/neeraj/.config/piper-tts/en_US-lessac-medium.onnx"
VOICE_CONFIG = "/home/neeraj/.config/piper-tts/en_US-lessac-medium.onnx.json"
PIPER_BINARY = "/usr/local/bin/piper" # Ensure this path is correct

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def play_sound(text):
    """
    Generates TTS audio using Piper and plays it via aplay.
    """
    print(f"Speaking: {text}")
    try:
        # Note: Added '2>/dev/null' to hide generic audio logs
        cmd = f'echo "{text}" | piper --model {VOICE_MODEL} --output-raw | paplay --raw --rate=22050 --format=s16le --channels=1'
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"TTS Error: {e}")

def capture_image(filename="capture.jpg", cam_index=0):
    """
    Captures an image using OpenCV (works on laptop / USB camera / Pi).
    """
    print("Capturing image...")

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Camera not opened")
        return None
    # Warm up camera
    for _ in range(5):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to grab frame")
        return None

    cv2.imwrite(filename, frame)
    return filename


def get_description(image_path):
    """
    Sends the image to the local SmolVLM server.
    """
    print("Analyzing image...")
   
    if not os.path.exists(image_path):
        return "Error: Image capture failed."

    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")

    user_prompt = """
    You are an assistant for a blind person.
    1. If there is text in the image (English or Hindi), read it out exactly.
    2. If there is no text, describe the scene safely and clearly.
    Keep the answer concise.
    """

    payload = {
        "prompt": f"User: {user_prompt}\n<image_data>\nAssistant:",
        "image_data": [{"data": img_base64, "id": 10}],
        "n_predict": 256,
        "temperature": 0.2
    }
    try:
        response = requests.post(LLAMA_SERVER_URL, json=payload, timeout=60)
        result = response.json()

        ai_text = ""

        if isinstance(result, dict):
            ai_text = result.get("content") or result.get("response") or str(result)
        else:
            ai_text = str(result)

        ai_text = ai_text.strip()

        print("\nAI:", ai_text)
        play_sound(ai_text)
        return ai_text

    except Exception as e:
        print("AI: Error connecting to AI:", e)
        play_sound("Error connecting to AI")
        return "Error connecting to AI"


def log_interaction(description):
    """
    Logs the entry to a daily log file.
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.jsonl")
   
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "description": description
    }
   
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Logged to {log_file}")
def extract_text_ocr(image_path):
    if not TESSERACT_AVAILABLE:
        return None

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="eng+hin")
        return text.strip() if text.strip() else None
    except:
        return None
def main():
    print("------------------------------------------------")
    print(" SYSTEM READY ")
    print(" Press [ENTER] to capture an image.")
    print(" Press [Ctrl+C] to exit.")
    print("------------------------------------------------")
   
    # Initial Greeting
    play_sound("System Ready.")
   
    while True:
        try:
            # This line waits for you to hit Enter
            input("")
           
            play_sound("Scanning.")
           
            # 1. Capture
            img_file = capture_image()
            if img_file is None:
                play_sound("Camera error")
                continue
           
            # 2. Analyze
            ocr_text = extract_text_ocr(img_file)
            if ocr_text:
                print("\nOCR:", ocr_text)
                play_sound(ocr_text)
                log_interaction({"type": "ocr", "text": ocr_text})
            else:
                description = get_description(img_file)
                log_interaction({"type": "vlm", "text": description})      
           
            print("Ready for next capture (Press Enter)...")

        except KeyboardInterrupt:
            print("\nExiting program...")
            break

if __name__ == "__main__":
    main()