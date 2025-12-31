# ATIS Monster - 台灣機場自動情報服務翻譯系統

![image](https://github.com/masonzeng702550/ATIS-Monster/blob/main/screenshot.png)

## English Description

**ATIS Monster** is an intelligent web application that automatically processes, translates, and visualizes ATIS (Automatic Terminal Information Service) broadcasts from Taiwan's three major airports: Songshan (RCSS), Taoyuan (RCTP), and Kaohsiung (RCKH).

The application provides real-time streaming of ATIS broadcasts and leverages Google's Gemini AI to deliver comprehensive aviation weather information in an accessible format. It automatically records 90 seconds of ATIS audio, transcribes it using Gemini 2.5-flash, translates the aviation terminology into Chinese, and generates intuitive weather diagrams using Gemini's image generation capabilities.

**Key Features:**
- 🔊 **Live ATIS Streaming**: Listen to real-time ATIS broadcasts from any supported airport
- 🎙️ **Automatic Audio Recording**: Captures 90-second ATIS broadcasts using ffmpeg
- 🤖 **AI-Powered Transcription**: Utilizes Gemini 2.5-flash for accurate audio-to-text conversion
- 🌐 **Intelligent Translation**: Converts aviation English to Chinese with context-aware AI translation
- 🎨 **Visual Weather Diagrams**: Generates airport weather illustrations using Gemini 2.5-flash-image (Nano Banana)
- ✈️ **Multi-Airport Support**: Covers Taiwan's three major airports (RCSS, RCTP, RCKH)
- 📱 **Responsive Web Interface**: Clean, modern UI built with HTML5, CSS3, and vanilla JavaScript

**Technology Stack:**
- Backend: Python Flask framework
- Audio Processing: ffmpeg, pydub
- AI Services: Google Gemini API (2.5-flash for transcription & translation, 2.5-flash-image for visualization)
- Frontend: Responsive HTML5/CSS3/JavaScript
- Audio Streaming: HTML5 Audio API

Perfect for pilots, aviation enthusiasts, flight students, and anyone interested in understanding airport weather conditions in Taiwan.

---

## 中文說明

自動錄製、辨識並翻譯台灣三大機場（松山、桃園、高雄）的 ATIS 廣播內容，並提供 AI 生成的天氣視覺化簡圖。

## 功能特色

- 🎙️ 自動錄製 ATIS 音訊（90秒）
- 🗣️ 語音轉文字（Google Speech Recognition）
- 🤖 AI 翻譯成中文（Gemini 2.5-flash）
- 🎨 AI 生成天氣簡圖（Gemini Nano Banana）
- ✈️ 支援三大機場：松山(RCSS)、桃園(RCTP)、高雄(RCKH)

## 技術

- **後端**: Flask (Python 3.9+)
- **音訊處理**: ffmpeg, pydub
- **語音辨識**: Google Gemini API (原使用 SpeechRecognition 但效果不佳)
- **AI 服務**: Google Gemini API (2.5-flash + 2.5-flash-image)
- **前端**: HTML5, CSS3, JavaScript

## 安裝步驟

### 1. 系統需求

- Python 3.9+
- ffmpeg

### 2. 安裝 ffmpeg (macOS)

```bash
brew install ffmpeg
```

### 3. 建立虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 4. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 5. 設定 Gemini API Key

**方法 1：使用 API.txt（推薦）**
```bash
# 編輯 API.txt 檔案，將你的 Gemini API Key 貼上
nano API.txt
```

**方法 2：使用環境變數**
```bash
cp .env.example .env
# 編輯 .env 檔案，填入你的 GEMINI_API_KEY
nano .env
```

**取得 Gemini API Key**：
1. 訪問 https://ai.google.dev/
2. 登入 Google 帳號
3. 建立 API Key
4. 將 API Key 貼到 `API.txt` 檔案中

### 6. 執行應用程式

```bash
python run.py
```

應用程式將在 http://localhost:5000 啟動。

## 使用方式

1. 開啟瀏覽器訪問 http://localhost:5000
2. 點擊想要查詢的機場按鈕（松山/桃園/高雄）
3. 等待系統錄製並處理 ATIS 音訊（約 2 分鐘）
4. 查看結果：
   - 左側：中文翻譯的 ATIS 資訊
   - 右側：AI 生成的天氣簡圖

## 專案結構

```
ATIS_monster/
├── app/
│   ├── modules/          # 功能模組
│   │   ├── audio_recorder.py
│   │   ├── speech_recognition_module.py
│   │   ├── gemini_translator.py
│   │   └── gemini_image_generator.py
│   ├── static/           # 靜態檔案
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/        # HTML 模板
│   └── __init__.py
├── temp/                 # 臨時音訊檔案
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

## API 端點

### POST /api/process_atis

處理 ATIS 音訊並回傳翻譯和圖片。

**Request Body:**
```json
{
  "airport_code": "RCTP"
}
```

**Response:**
```json
{
  "status": "success",
  "airport_code": "RCTP",
  "original_text": "...",
  "translation": {...},
  "image_url": "/static/images/weather_RCTP_xxx.png"
}
```

## 授權

MIT License

## 致謝

- ATIS 串流來源：https://stream.twatc.net/
