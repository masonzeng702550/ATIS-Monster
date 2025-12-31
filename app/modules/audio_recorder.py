"""
音訊錄製模組
使用 ffmpeg 從 ATIS 串流錄製音訊
"""

import os
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def record_atis(airport_code, stream_url, duration=90, temp_dir='./temp'):
    """
    從 ATIS 串流錄製音訊

    Args:
        airport_code (str): 機場代碼 (RCSS, RCTP, RCKH)
        stream_url (str): ATIS 串流 URL
        duration (int): 錄製時長（秒），預設 90 秒
        temp_dir (str): 臨時檔案目錄

    Returns:
        str: 錄製的音訊檔案路徑

    Raises:
        Exception: 如果錄製失敗
    """
    try:
        # 確保臨時目錄存在
        os.makedirs(temp_dir, exist_ok=True)

        # 固定使用 rec.mp3 作為檔名（方便除錯）
        output_file = os.path.join(temp_dir, 'rec.mp3')

        logger.info(f"開始錄製 {airport_code} ATIS 音訊...")
        logger.info(f"串流 URL: {stream_url}")
        logger.info(f"錄製時長: {duration} 秒")
        logger.info(f"輸出檔案: {output_file}")

        # 建立 ffmpeg 命令
        ffmpeg_command = [
            'ffmpeg',
            '-i', stream_url,          # 輸入串流
            '-t', str(duration),        # 錄製時長
            '-acodec', 'libmp3lame',   # 音訊編碼器
            '-ab', '128k',              # 位元率
            '-y',                       # 覆蓋既有檔案
            output_file                 # 輸出檔案
        ]

        # 執行 ffmpeg 命令
        process = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=duration + 30  # 增加 30 秒緩衝時間
        )

        # 檢查是否成功
        if process.returncode != 0:
            error_message = process.stderr.decode('utf-8')
            logger.error(f"ffmpeg 錄製失敗: {error_message}")
            raise Exception(f"ffmpeg 錄製失敗: {error_message}")

        # 檢查檔案是否存在且大小正常
        if not os.path.exists(output_file):
            raise Exception(f"錄製的檔案不存在: {output_file}")

        file_size = os.path.getsize(output_file)
        if file_size < 1024:  # 小於 1KB 視為異常
            raise Exception(f"錄製的檔案過小: {file_size} bytes")

        logger.info(f"音訊錄製成功！檔案大小: {file_size / 1024:.2f} KB")
        return output_file

    except subprocess.TimeoutExpired:
        logger.error("ffmpeg 錄製超時")
        raise Exception("音訊錄製超時，請稍後再試")

    except FileNotFoundError:
        logger.error("找不到 ffmpeg，請確認是否已安裝")
        raise Exception("系統未安裝 ffmpeg，請聯繫管理員")

    except Exception as e:
        logger.error(f"錄製音訊時發生錯誤: {str(e)}")
        raise


def get_audio_info(audio_file):
    """
    取得音訊檔案資訊

    Args:
        audio_file (str): 音訊檔案路徑

    Returns:
        dict: 音訊資訊
    """
    try:
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            audio_file
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode == 0:
            import json
            info = json.loads(result.stdout.decode('utf-8'))
            return info
        else:
            logger.warning("無法取得音訊資訊")
            return None

    except Exception as e:
        logger.warning(f"取得音訊資訊時發生錯誤: {str(e)}")
        return None
