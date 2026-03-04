# 🎬 YouTube Downloader Pro

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)

A polished Python desktop app for downloading videos from YouTube up to 4K and extracting high-quality MP3 audio.  
Standalone executable builds are supported — no Python install needed.

---

## ✨ Features

- 🖥️ Video downloads: 144p → 4K  
- 🎧 MP3 audio extraction  
- 📊 Progress tracking  
- 📁 Automatic file organization  
- 🚀 Modern GUI (CustomTkinter)  
- ⚙️ Standalone executable option

---

## 🖼️ Preview

> Add real screenshots inside `screenshots/` and update paths below:

![Main UI](screenshots/ui-main.png)
![Download Progress](screenshots/ui-progress.png)

---

## 🛠️ Install (Dev Mode)

```bash
git clone https://github.com/avraniel/youtube-downloader-pro.git
cd youtube-downloader-pro
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m app.main
