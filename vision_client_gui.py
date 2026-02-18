#!/usr/bin/env python3
import socket
import json
import os
import sys
import cv2
import threading
import tkinter as tk
from tkinter import Label, Button, Text
from PIL import Image, ImageTk


# ===================== Vision Client =====================
class VisionClient:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.request_id = 0

    def _connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.socket_path)
        return sock

    def _send_request(self, request):
        sock = self._connect()
        try:
            sock.sendall(json.dumps(request).encode("utf-8"))
            response = sock.recv(65536).decode("utf-8")
            return json.loads(response)
        finally:
            sock.close()

    def next_id(self):
        self.request_id += 1
        return self.request_id

    def initialize(self):
        return self._send_request({
            "id": self.next_id(),
            "init": {"model_path": "dummy"}
        })

    def clear_kv_cache(self):
        return self._send_request({
            "id": self.next_id(),
            "clear_kv_cache": {}
        })

    def infer(self, image_path, prompt=None, n_predict=64):
        if prompt is None:
            prompt = (
                "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
                "<|im_start|>user\n<img_placement>\n"
                "Describe the image in one short sentence.<|im_end|>\n"
                "<|im_start|>assistant\n"
            )

        return self._send_request({
            "id": self.next_id(),
            "infer": {
                "image_path": image_path,
                "prompt": prompt,
                "n_predict": n_predict
            }
        })


# ===================== Config =====================
SOCKET_PATH = "/tmp/vision.sock"
IMAGE_PATH = ".image.png"

if not os.path.exists(SOCKET_PATH):
    print("❌ Vision socket not found. Start SmolVLM server first.")
    sys.exit(1)

# ===================== Initialize Client =====================
client = VisionClient(SOCKET_PATH)
print("Initializing model...")
resp = client.initialize()
if not resp.get("success", False):
    print("❌ Model init failed:", resp.get("error"))
    sys.exit(1)
print("✅ Model initialized")

# ===================== Camera =====================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    sys.exit(1)

# ===================== GUI =====================
root = tk.Tk()
root.title("SmolVLM Vision Client (Raspberry Pi)")
root.geometry("900x700")

image_label = Label(root)
image_label.pack(pady=10)

output_box = Text(root, height=8, wrap="word", font=("Arial", 12))
output_box.pack(padx=10, pady=10)


# ===================== Actions =====================
def capture_and_infer():
    def run():
        ret, frame = cap.read()
        if not ret:
            output_box.insert("end", "Camera capture failed\n")
            return

        cv2.imwrite(IMAGE_PATH, frame)

        # Show image
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = img.resize((500, 350))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk

        client.clear_kv_cache()
        response = client.infer(os.path.abspath(IMAGE_PATH))

        output_box.delete("1.0", "end")
        if response.get("success", False):
            output_box.insert("end", response["result"]["text"])
        else:
            output_box.insert("end", response.get("error", "Inference error"))

    threading.Thread(target=run, daemon=True).start()


def quit_app():
    cap.release()
    if os.path.exists(IMAGE_PATH):
        os.remove(IMAGE_PATH)
    root.destroy()


# ===================== Buttons =====================
Button(root, text="📸 Capture & Describe", height=2, command=capture_and_infer).pack(pady=5)
Button(root, text="❌ Quit", height=2, command=quit_app).pack(pady=5)

root.mainloop()
