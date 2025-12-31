"""
ATIS Monster 路由處理
"""

import os
import logging
import traceback
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app

# 建立 Blueprint
main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# 機場資訊
AIRPORTS = {
    'RCSS': '松山機場 Songshan Airport',
    'RCTP': '桃園機場 Taoyuan Airport',
    'RCKH': '高雄機場 Kaohsiung Airport',
}


@main_bp.route('/')
def index():
    """首頁"""
    return render_template('index.html', airports=AIRPORTS)


@main_bp.route('/api/process_atis', methods=['POST'])
def process_atis():
    """
    處理 ATIS 音訊的主要 API 端點

    Request JSON:
        {
            "airport_code": "RCTP"
        }

    Response JSON:
        {
            "status": "success",
            "airport_code": "RCTP",
            "original_text": "...",
            "translation": {...},
            "image_url": "/static/images/weather_xxx.png",
            "timestamp": "2025-12-31T12:00:00"
        }
    """
    try:
        # 取得請求資料
        data = request.get_json()
        airport_code = data.get('airport_code')

        # 驗證機場代碼
        if not airport_code or airport_code not in AIRPORTS:
            return jsonify({
                'status': 'error',
                'message': f'無效的機場代碼: {airport_code}'
            }), 400

        logger.info(f"開始處理 {airport_code} ATIS 資訊")

        # 步驟 1: 錄製音訊
        from app.modules.audio_recorder import record_atis
        audio_file = record_atis(
            airport_code,
            current_app.config['ATIS_URLS'][airport_code],
            current_app.config['MAX_AUDIO_DURATION'],
            current_app.config['TEMP_DIR']
        )
        logger.info(f"音訊錄製完成: {audio_file}")

        # 步驟 2: 語音轉文字（使用 Gemini API）
        from app.modules.speech_recognition_module import transcribe_audio_with_gemini
        atis_text = transcribe_audio_with_gemini(
            audio_file,
            current_app.config['GEMINI_API_KEY']
        )
        logger.info(f"語音轉文字完成，長度: {len(atis_text)} 字元")

        # 儲存 ATIS 原文到 rec.txt（覆蓋模式）
        save_atis_to_file(atis_text, airport_code, audio_file)

        # 步驟 3: 並行處理 - 翻譯和圖像生成
        from app.modules.gemini_translator import translate_atis
        from app.modules.gemini_image_generator import generate_weather_image

        # 翻譯 ATIS 文字
        translation = translate_atis(
            atis_text,
            current_app.config['GEMINI_API_KEY']
        )
        logger.info("ATIS 翻譯完成")

        # 生成天氣簡圖
        image_filename = generate_weather_image(
            atis_text,
            airport_code,
            current_app.config['GEMINI_API_KEY'],
            current_app.config['STATIC_DIR']
        )
        logger.info(f"天氣簡圖生成完成: {image_filename}")

        # 清理臨時檔案
        cleanup_temp_files(audio_file, current_app.config['TEMP_DIR'])

        # 回傳結果
        return jsonify({
            'status': 'success',
            'airport_code': airport_code,
            'airport_name': AIRPORTS[airport_code],
            'original_text': atis_text,
            'translation': translation,
            'image_url': f'/static/images/{image_filename}',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"處理 ATIS 時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'處理失敗: {str(e)}'
        }), 500


def save_atis_to_file(atis_text, airport_code, audio_file=None):
    """
    儲存 ATIS 原文到 rec.txt

    Args:
        atis_text (str): ATIS 原文
        airport_code (str): 機場代碼
        audio_file (str): 音訊檔案路徑
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open('rec.txt', 'w', encoding='utf-8') as f:
            f.write(f"=" * 80 + "\n")
            f.write(f"ATIS 語音辨識記錄\n")
            f.write(f"=" * 80 + "\n")
            f.write(f"機場代碼: {airport_code}\n")
            f.write(f"機場名稱: {AIRPORTS.get(airport_code, '未知機場')}\n")
            f.write(f"辨識時間: {timestamp}\n")
            if audio_file:
                f.write(f"音訊檔案: {audio_file}\n")
            f.write(f"文字長度: {len(atis_text)} 字元\n")
            f.write(f"=" * 80 + "\n\n")

            if atis_text and len(atis_text.strip()) > 0:
                f.write("【辨識結果】\n\n")
                f.write(atis_text)
            else:
                f.write("【辨識結果】\n\n")
                f.write("⚠️ 警告：語音辨識未返回任何內容\n")
                f.write("可能原因：\n")
                f.write("1. 音訊品質不佳或無聲音\n")
                f.write("2. Google Speech API 連線問題\n")
                f.write("3. 音訊格式不支援\n")

            f.write(f"\n\n" + "=" * 80 + "\n")
            f.write(f"錄音檔案已保存為: temp/rec.mp3\n")
            f.write(f"可使用音訊播放器檢查錄音內容\n")
            f.write(f"=" * 80 + "\n")

        logger.info(f"ATIS 原文已儲存至 rec.txt (長度: {len(atis_text)} 字元)")

    except Exception as e:
        logger.warning(f"儲存 ATIS 到 rec.txt 時發生錯誤: {str(e)}")


def cleanup_temp_files(audio_file, temp_dir):
    """清理臨時檔案（保留 rec.mp3 用於除錯）"""
    try:
        # 只刪除 WAV 檔案，保留 rec.mp3 方便除錯
        wav_file = audio_file.replace('.mp3', '.wav')
        if os.path.exists(wav_file):
            os.remove(wav_file)
            logger.info(f"已刪除臨時 WAV 檔案: {wav_file}")

        # 不刪除 rec.mp3，以便檢查錄音內容
        logger.info(f"保留錄音檔案 {audio_file} 供除錯使用")

    except Exception as e:
        logger.warning(f"清理臨時檔案時發生錯誤: {str(e)}")


@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'gemini_api_configured': bool(current_app.config.get('GEMINI_API_KEY'))
    })
