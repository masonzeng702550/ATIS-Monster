"""
Gemini 圖像生成模組
使用 Gemini 2.5-flash-image (Nano Banana) 生成天氣簡圖
"""

import os
import logging
from datetime import datetime
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def generate_weather_image(atis_text, airport_code, api_key, static_dir='./app/static/images'):
    """
    使用 Gemini Nano Banana 生成天氣簡圖

    Args:
        atis_text (str): ATIS 文字內容
        airport_code (str): 機場代碼
        api_key (str): Gemini API Key
        static_dir (str): 靜態檔案目錄

    Returns:
        str: 圖片檔案名稱

    Raises:
        Exception: 如果生成失敗
    """
    try:
        logger.info(f"開始使用 Gemini Nano Banana 生成 {airport_code} 天氣簡圖...")

        # 確保輸出目錄存在
        os.makedirs(static_dir, exist_ok=True)

        # 初始化 Gemini Client
        client = genai.Client(api_key=api_key)

        # 建立圖像生成 Prompt
        prompt = f"""Create a clear and professional airport weather diagram for ATIS information.

ATIS Content:
{atis_text}

Requirements for the weather diagram:
1. **Title**: Display airport code "{airport_code}" and "ATIS Weather Diagram" at the top
2. **Runway Indicator**: Show the active runway with direction arrow
3. **Wind Information**: Display wind direction (arrow) and speed in knots
4. **Visibility**: Show visibility range with appropriate icon
5. **Cloud Coverage**: Illustrate cloud layers with height in feet (FEW/SCT/BKN/OVC)
6. **Temperature & Dew Point**: Display with thermometer icons
7. **QNH/Pressure**: Show barometric pressure with icon
8. **Visual Style**:
   - Clean, professional aviation-style diagram
   - Use aviation standard colors and symbols
   - Clear labels and units
   - Easy to read at a glance
   - Include small plane icons for context
9. **Layout**: Organize information in a logical, easy-to-scan layout

Make it look like a professional aviation weather briefing chart that pilots would use."""

        logger.info("正在呼叫 Gemini 2.5-flash-image API...")

        # 呼叫 Gemini Image Generation API
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        # 處理回應
        image_saved = False
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'weather_{airport_code}_{timestamp}.png'
        filepath = os.path.join(static_dir, filename)

        for part in response.parts:
            if part.text is not None:
                logger.info(f"Gemini 回應文字: {part.text}")

            elif part.inline_data is not None:
                # 儲存生成的圖片
                image = part.as_image()
                image.save(filepath)
                image_saved = True

                file_size = os.path.getsize(filepath)
                logger.info(f"天氣簡圖生成成功！檔案: {filename}, 大小: {file_size / 1024:.2f} KB")

        if not image_saved:
            raise Exception("Gemini 沒有回傳圖片資料")

        return filename

    except Exception as e:
        logger.error(f"Gemini 圖像生成失敗: {str(e)}")
        raise Exception(f"天氣簡圖生成失敗: {str(e)}")


def generate_simple_weather_image(atis_data, airport_code, api_key, static_dir='./app/static/images'):
    """
    使用結構化資料生成天氣簡圖（可選的替代方案）

    Args:
        atis_data (dict): 結構化的 ATIS 資料
        airport_code (str): 機場代碼
        api_key (str): Gemini API Key
        static_dir (str): 靜態檔案目錄

    Returns:
        str: 圖片檔案名稱
    """
    try:
        logger.info("使用結構化資料生成天氣簡圖...")

        # 初始化 Gemini Client
        client = genai.Client(api_key=api_key)

        # 從結構化資料建立 Prompt
        prompt = f"""Create a professional airport weather diagram with the following information:

Airport: {atis_data.get('airport', airport_code)}
Information Code: {atis_data.get('info_code', 'N/A')}
Runway in Use: {atis_data.get('runway', 'N/A')}
Wind: {atis_data.get('wind', 'N/A')}
Visibility: {atis_data.get('visibility', 'N/A')}
Clouds: {atis_data.get('clouds', 'N/A')}
Temperature: {atis_data.get('temperature', 'N/A')}
Dew Point: {atis_data.get('dewpoint', 'N/A')}
QNH: {atis_data.get('qnh', 'N/A')}

Create a clear, professional aviation weather diagram showing:
- Runway direction indicator with arrows
- Wind direction and speed visualization
- Cloud layers with height markers
- Temperature and dew point displays with icons
- QNH pressure reading
- Use standard aviation symbols and colors
- Make it easy to read and understand at a glance"""

        # 呼叫 API
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        # 儲存圖片
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'weather_{airport_code}_{timestamp}.png'
        filepath = os.path.join(static_dir, filename)

        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(filepath)
                logger.info(f"簡化版天氣簡圖生成成功: {filename}")
                return filename

        raise Exception("未收到圖片資料")

    except Exception as e:
        logger.error(f"簡化版圖像生成失敗: {str(e)}")
        raise
