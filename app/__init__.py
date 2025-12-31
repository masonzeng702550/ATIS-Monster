"""
ATIS Monster Flask Application
台灣機場自動情報服務翻譯系統
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_api_key():
    """
    載入 Gemini API Key
    優先順序：API.txt > 環境變數
    """
    # 方法 1: 從 API.txt 讀取
    api_file = 'API.txt'
    if os.path.exists(api_file):
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳過空行和註解
                    if line and not line.startswith('#'):
                        logger.info("已從 API.txt 載入 Gemini API Key")
                        return line
        except Exception as e:
            logger.warning(f"無法讀取 API.txt: {str(e)}")

    # 方法 2: 從環境變數讀取
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        logger.info("已從環境變數載入 Gemini API Key")
        return api_key

    # 都沒有找到
    logger.warning("警告：未設定 Gemini API Key！")
    logger.warning("請在 API.txt 或 .env 檔案中設定 GEMINI_API_KEY")
    return None


def create_app():
    """建立並設定 Flask 應用程式"""
    app = Flask(__name__)

    # 讀取 Gemini API Key（優先從 API.txt，其次從環境變數）
    gemini_api_key = load_api_key()

    # 應用程式設定
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    app.config['GEMINI_API_KEY'] = gemini_api_key
    app.config['MAX_AUDIO_DURATION'] = int(os.getenv('MAX_AUDIO_DURATION', 90))
    app.config['TEMP_DIR'] = os.getenv('TEMP_DIR', './temp')
    app.config['STATIC_DIR'] = os.getenv('STATIC_DIR', './app/static/images')

    # ATIS 串流 URLs
    app.config['ATIS_URLS'] = {
        'RCSS': os.getenv('RCSS_ATIS_URL', 'https://stream.twatc.net/RCSS_ATIS'),
        'RCTP': os.getenv('RCTP_ATIS_URL', 'https://stream.twatc.net/RCTP_ATIS'),
        'RCKH': os.getenv('RCKH_ATIS_URL', 'https://stream.twatc.net/RCKH_ATIS'),
    }

    # 啟用 CORS
    CORS(app)

    # 確保必要目錄存在
    os.makedirs(app.config['TEMP_DIR'], exist_ok=True)
    os.makedirs(app.config['STATIC_DIR'], exist_ok=True)

    # 註冊路由
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    logger.info("ATIS Monster 應用程式初始化完成")

    return app
