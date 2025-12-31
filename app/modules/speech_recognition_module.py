"""
語音轉文字模組
使用 Gemini API 進行音訊轉文字
"""

import os
import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from google import genai

logger = logging.getLogger(__name__)


def transcribe_audio_with_gemini(audio_file, api_key):
    """
    使用 Gemini API 將音訊轉換為文字

    Args:
        audio_file (str): 音訊檔案路徑（支援 MP3, WAV 等格式）
        api_key (str): Gemini API Key

    Returns:
        str: 辨識出的文字內容

    Raises:
        Exception: 如果辨識失敗
    """
    try:
        logger.info(f"使用 Gemini API 進行語音轉文字: {audio_file}")

        # 初始化 Gemini 客戶端
        client = genai.Client(api_key=api_key)

        # 上傳音訊檔案
        logger.info("正在上傳音訊檔案到 Gemini...")
        myfile = client.files.upload(file=audio_file)
        logger.info(f"音訊檔案上傳成功: {myfile.name}")

        # 使用 Gemini 進行音訊轉文字
        logger.info("開始使用 Gemini 辨識音訊...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "Please transcribe this ATIS (Automatic Terminal Information Service) audio recording. "
                "Output only the transcribed text without any additional explanation or formatting. "
                "The audio is an aviation ATIS broadcast in English.",
                myfile
            ]
        )

        # 取得辨識結果
        transcribed_text = response.text.strip()

        logger.info(f"Gemini 語音辨識成功！辨識文字長度: {len(transcribed_text)} 字元")
        logger.debug(f"辨識結果預覽: {transcribed_text[:100]}...")

        # 刪除已上傳的檔案（清理）
        try:
            client.files.delete(name=myfile.name)
            logger.info("已清理上傳的音訊檔案")
        except Exception as e:
            logger.warning(f"清理上傳檔案時發生錯誤: {str(e)}")

        # 檢查結果
        if not transcribed_text or len(transcribed_text) == 0:
            raise Exception("Gemini 辨識結果為空")

        return transcribed_text

    except Exception as e:
        logger.error(f"Gemini 語音轉文字失敗: {str(e)}")
        raise Exception(f"音訊轉文字失敗: {str(e)}")


def convert_mp3_to_wav(mp3_file, temp_dir='./temp'):
    """
    將 MP3 檔案轉換為 WAV 格式
    （SpeechRecognition 需要 WAV 格式）

    Args:
        mp3_file (str): MP3 檔案路徑
        temp_dir (str): 臨時檔案目錄

    Returns:
        str: WAV 檔案路徑

    Raises:
        Exception: 如果轉換失敗
    """
    try:
        logger.info(f"開始將 MP3 轉換為 WAV: {mp3_file}")

        # 載入 MP3
        audio = AudioSegment.from_mp3(mp3_file)

        # 設定 WAV 參數（單聲道，16000 Hz）
        audio = audio.set_channels(1)  # 單聲道
        audio = audio.set_frame_rate(16000)  # 16kHz 採樣率

        # 生成 WAV 檔案路徑
        wav_file = mp3_file.replace('.mp3', '.wav')

        # 匯出為 WAV
        audio.export(wav_file, format='wav')

        file_size = os.path.getsize(wav_file)
        logger.info(f"WAV 轉換成功！檔案大小: {file_size / 1024:.2f} KB")

        return wav_file

    except Exception as e:
        logger.error(f"MP3 轉 WAV 失敗: {str(e)}")
        raise Exception(f"音訊格式轉換失敗: {str(e)}")


def transcribe_audio(audio_file, temp_dir='./temp', language='en-US'):
    """
    將音訊轉換為文字

    Args:
        audio_file (str): 音訊檔案路徑（MP3 或 WAV）
        temp_dir (str): 臨時檔案目錄
        language (str): 語言設定，預設 'en-US' (ATIS 使用英文)

    Returns:
        str: 辨識出的文字內容

    Raises:
        Exception: 如果辨識失敗
    """
    try:
        # 步驟 1: 如果是 MP3，先轉換為 WAV
        if audio_file.endswith('.mp3'):
            wav_file = convert_mp3_to_wav(audio_file, temp_dir)
        else:
            wav_file = audio_file

        logger.info(f"開始語音轉文字: {wav_file}")

        # 步驟 2: 初始化辨識器
        recognizer = sr.Recognizer()

        # 調整辨識參數（提高準確度）
        recognizer.energy_threshold = 300  # 降低能量閾值
        recognizer.dynamic_energy_threshold = True

        # 步驟 3: 載入音訊檔案
        with sr.AudioFile(wav_file) as source:
            logger.info("正在載入音訊...")

            # 調整環境噪音
            recognizer.adjust_for_ambient_noise(source, duration=1)

            # 讀取整個音訊
            audio_data = recognizer.record(source)

            logger.info(f"音訊載入完成，開始辨識... (語言: {language})")

        # 步驟 4: 使用 Google Web Speech API 進行辨識
        try:
            # 辨識音訊
            text = recognizer.recognize_google(
                audio_data,
                language=language,
                show_all=False  # 只回傳最佳結果
            )

            logger.info(f"語音辨識成功！辨識文字長度: {len(text)} 字元")
            logger.debug(f"辨識結果: {text[:100]}...")  # 只記錄前 100 字元

            return text

        except sr.UnknownValueError:
            logger.error("Google Speech Recognition 無法理解音訊")
            raise Exception("無法辨識音訊內容，可能是音質不佳或沒有語音")

        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition 服務錯誤: {str(e)}")
            raise Exception(f"語音辨識服務暫時無法使用: {str(e)}")

    except Exception as e:
        logger.error(f"語音轉文字失敗: {str(e)}")
        raise


def transcribe_audio_in_chunks(audio_file, chunk_duration=60, temp_dir='./temp', language='en-US'):
    """
    使用靜音檢測將長音訊分段辨識（根據靜音自動分割）

    Args:
        audio_file (str): 音訊檔案路徑
        chunk_duration (int): 保留參數以維持向後相容（已不使用）
        temp_dir (str): 臨時檔案目錄
        language (str): 語言設定

    Returns:
        str: 完整的辨識文字

    Raises:
        Exception: 如果辨識失敗
    """
    try:
        # 轉換為 WAV
        if audio_file.endswith('.mp3'):
            wav_file = convert_mp3_to_wav(audio_file, temp_dir)
        else:
            wav_file = audio_file

        logger.info("開始使用靜音檢測分割音訊...")

        # 載入音訊
        sound = AudioSegment.from_file(wav_file)
        total_duration = len(sound) / 1000  # 總時長（秒）
        logger.info(f"音訊總時長: {total_duration:.1f} 秒")

        # 根據靜音分割音訊
        chunks = split_on_silence(
            sound,
            min_silence_len=500,        # 靜音至少 500 毫秒
            silence_thresh=sound.dBFS-14,  # 靜音閾值
            keep_silence=500,           # 保留 500 毫秒的靜音
        )

        logger.info(f"音訊已分割為 {len(chunks)} 個片段")

        # 建立臨時資料夾存放音訊片段
        chunks_folder = os.path.join(temp_dir, 'audio-chunks')
        os.makedirs(chunks_folder, exist_ok=True)

        # 初始化辨識器
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        whole_text = []

        # 處理每個音訊片段
        for i, audio_chunk in enumerate(chunks, start=1):
            # 匯出音訊片段
            chunk_filename = os.path.join(chunks_folder, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")

            logger.info(f"辨識第 {i}/{len(chunks)} 段...")

            # 辨識該片段
            try:
                with sr.AudioFile(chunk_filename) as source:
                    # 調整環境噪音
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)

                    try:
                        text = recognizer.recognize_google(audio_data, language=language)
                        if text and len(text.strip()) > 0:
                            whole_text.append(text)
                            logger.info(f"第 {i} 段辨識成功: {text[:50]}...")
                        else:
                            logger.warning(f"第 {i} 段辨識結果為空")
                    except sr.UnknownValueError:
                        logger.warning(f"第 {i} 段無法辨識（音訊內容無法理解）")
                    except sr.RequestError as e:
                        logger.error(f"第 {i} 段 API 請求失敗: {str(e)}")

            except Exception as e:
                logger.warning(f"第 {i} 段處理失敗: {str(e)}")

            finally:
                # 清理該片段檔案
                if os.path.exists(chunk_filename):
                    os.remove(chunk_filename)

        # 清理臨時資料夾
        try:
            if os.path.exists(chunks_folder):
                os.rmdir(chunks_folder)
        except:
            pass

        # 合併所有辨識文字
        result = ' '.join(whole_text)
        logger.info(f"靜音分段辨識完成，總長度: {len(result)} 字元")

        # 檢查是否有成功辨識的內容
        if not result or len(result.strip()) == 0:
            raise Exception("所有音訊片段皆無法辨識，可能是音質不佳或沒有語音內容")

        return result

    except Exception as e:
        logger.error(f"靜音分段辨識失敗: {str(e)}")
        raise
