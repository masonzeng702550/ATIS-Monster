"""
Gemini 文字翻譯模組
使用 Gemini 2.5-flash 將 ATIS 英文翻譯成繁體中文
"""

import os
import logging
import json
from google import genai

logger = logging.getLogger(__name__)


def translate_atis(atis_text, api_key):
    """
    使用 Gemini API 翻譯 ATIS 文字

    Args:
        atis_text (str): ATIS 英文原文
        api_key (str): Gemini API Key

    Returns:
        dict: 結構化的翻譯結果

    Raises:
        Exception: 如果翻譯失敗
    """
    try:
        logger.info("開始使用 Gemini 翻譯 ATIS 內容...")

        # 初始化 Gemini Client
        client = genai.Client(api_key=api_key)

        # 建立翻譯 Prompt
        prompt = f"""你是專業的航空翻譯員。請將以下 ATIS（機場自動終端情報服務）廣播內容翻譯成繁體中文，
並以 JSON 格式回傳結構化資訊。

ATIS 原文：
{atis_text}

請仔細分析內容，並以以下 JSON 格式回傳（只回傳 JSON，不要其他文字）：
{{
  "airport": "機場名稱（繁體中文）",
  "info_code": "資訊代碼（如 Alpha, Bravo 等）",
  "time": "時間（UTC/ZULU 時間）",
  "runway": "使用跑道",
  "approach": "進場程序",
  "wind": "風向風速（例如：050度 8節）",
  "visibility": "能見度",
  "clouds": "雲況（高度和類型）",
  "temperature": "溫度",
  "dewpoint": "露點溫度",
  "qnh": "氣壓設定值（QNH）",
  "remarks": "其他備註或重要資訊",
  "summary": "簡短摘要（1-2句話，用平易近人的語言說明目前天氣狀況）"
}}

注意事項：
1. 如果某些欄位在原文中未提及，請填入 "未提供"
2. 溫度和露點請轉換為攝氏度數
3. 風速請保留節（knots）單位
4. 能見度請轉換為公里或公尺
5. 雲況請說明雲層高度（英尺）和類型（FEW/SCT/BKN/OVC）
6. summary 要用簡單易懂的中文說明"""

        # 呼叫 Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # 解析回應
        response_text = response.text.strip()
        logger.debug(f"Gemini 回應: {response_text[:200]}...")

        # 嘗試解析 JSON
        try:
            # 移除可能的 markdown 程式碼區塊標記
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()

            translation_data = json.loads(response_text)
            logger.info("ATIS 翻譯成功")

            return translation_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {str(e)}")
            logger.error(f"原始回應: {response_text}")

            # 如果 JSON 解析失敗，回傳基本格式
            return {
                "airport": "解析失敗",
                "summary": response_text[:200],  # 至少回傳部分內容
                "raw_response": response_text
            }

    except Exception as e:
        logger.error(f"Gemini 翻譯失敗: {str(e)}")
        raise Exception(f"AI 翻譯服務暫時無法使用: {str(e)}")


def format_translation_for_display(translation_data):
    """
    將翻譯結果格式化為易讀的文字

    Args:
        translation_data (dict): 翻譯結果

    Returns:
        str: 格式化後的文字
    """
    try:
        formatted = f"""
機場資訊 ATIS Translation
{'=' * 50}

📍 機場：{translation_data.get('airport', '未知')}
🔤 資訊代碼：{translation_data.get('info_code', '未提供')}
⏰ 時間：{translation_data.get('time', '未提供')}

✈️ 跑道與進場
  • 使用跑道：{translation_data.get('runway', '未提供')}
  • 進場程序：{translation_data.get('approach', '未提供')}

🌤️ 天氣狀況
  • 風向風速：{translation_data.get('wind', '未提供')}
  • 能見度：{translation_data.get('visibility', '未提供')}
  • 雲況：{translation_data.get('clouds', '未提供')}
  • 溫度：{translation_data.get('temperature', '未提供')}
  • 露點：{translation_data.get('dewpoint', '未提供')}
  • 氣壓 (QNH)：{translation_data.get('qnh', '未提供')}

📝 備註
{translation_data.get('remarks', '無')}

💬 摘要
{translation_data.get('summary', '無法生成摘要')}
"""
        return formatted.strip()

    except Exception as e:
        logger.warning(f"格式化翻譯結果失敗: {str(e)}")
        return str(translation_data)
