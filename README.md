# 🌙 Moondream2 Real-Time Vision Language Assistant

An assistive real-time AI system powered by **Moondream-2 (Vision Language Model)** that interprets live visual input and generates natural language responses with multilingual voice output.

Designed as an educational and accessibility-focused initiative to support visually impaired individuals in understanding their surroundings independently.

---

## 🚀 Features

### 🎥 Real-Time Scene Understanding

* Live webcam integration
* Instant scene descriptions
* Object and environment awareness
* Continuous visual interpretation

### 📝 Text Reading (OCR + VLM)

* Detects and reads visible text
* Works on books, signboards, labels
* Supports translation into multiple languages

### 💰 Indian Currency Recognition

* Detects ₹10, ₹20, ₹50, ₹100, ₹200, ₹500 notes
* Announces denomination via voice output
* Designed for accessibility use cases

### 🌐 Multilingual Voice Output

Supports:

* English
* Hindi
* Kannada

Includes real-time translation and speech synthesis.

### 🧾 Evidence Logging

* Saves captured frames
* Stores AI-generated descriptions
* Useful for debugging and demonstrations

---

## ♿ Accessibility Impact

This system is built as an assistive AI tool that enables visually impaired users to:

* Understand surroundings through audio descriptions
* Read printed text independently
* Identify currency without assistance
* Interact in multiple languages

---

## 🏗️ System Architecture

Moondream-2 integrates:

* **Vision Encoder** → Converts image into visual embeddings
* **Language Model** → Generates contextual text responses

Core workflow:

1. Capture frame via OpenCV
2. Encode image using `encode_image()`
3. Generate response using `answer_question()`
4. Translate (optional)
5. Convert text → speech
6. Play audio output

---

## 🧠 Model Information

* **Model:** `vikhyatk/moondream2`
* **Type:** Vision-Language Model (VLM)
* **Parameters:** ~1.8B
* **Release Year:** 2024
* **Revision Used:** `2024-08-26`
* **Framework:** HuggingFace Transformers
* **Model Class:** `AutoModelForCausalLM`

### Why Moondream-2?

* Lightweight (~1.8B parameters)
* Runs locally (CPU compatible)
* Fast inference
* Suitable for edge AI deployment
* Open-source (Apache-2.0)

---

## 🛠️ Tech Stack

| Component         | Technology               |
| ----------------- | ------------------------ |
| Language          | Python                   |
| VLM               | Moondream-2              |
| Deep Learning     | PyTorch                  |
| Model Integration | HuggingFace Transformers |
| Computer Vision   | OpenCV                   |
| Speech Output     | gTTS / pyttsx3           |
| Translation       | Google Translator        |

---

## 💻 Hardware Requirements

Minimum:

* 4GB RAM
* CPU support

Recommended:

* 8GB RAM
* NVIDIA GPU (for faster inference)

---

## 🎯 Project Objectives

* Demonstrate real-time Vision-Language AI
* Build an accessibility-focused AI assistant
* Introduce students to applied AI systems
* Enable multilingual AI interaction
* Bridge computer vision and natural language processing

---

## 🏫 Educational Implementation

Implemented during a mentoring session at:

**Indus International School, Bangalore (IISB)**

Students gained hands-on exposure to:

* Real-time AI system development
* Vision Language Models
* Practical debugging
* Applied AI problem solving

---

## 📈 Future Improvements

* Mobile application integration
* Edge deployment optimization
* Expanded language support
* Enhanced object detection
* Wearable device integration
* Navigation assistance for visually impaired users

---

## 👨‍💻 Author

**Selin Jogi Chittilappilly**
B.Voc Mathematics & Artificial Intelligence
AI/ML Enthusiast | Computer Vision | Vision Language Models

---

## 🙏 Acknowledgment

* Niya C Anto – Mentor
* Neeraj PM – Head of Engineering



