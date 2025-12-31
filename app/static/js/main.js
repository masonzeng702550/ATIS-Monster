/**
 * ATIS Monster - 前端 JavaScript
 * 處理使用者互動和 API 呼叫
 */

// 全域變數
let currentProcessing = null;

// ATIS 串流 URL 對應
const ATIS_STREAMS = {
    'RCSS': 'https://stream.twatc.net/RCSS_ATIS',
    'RCTP': 'https://stream.twatc.net/RCTP_ATIS',
    'RCKH': 'https://stream.twatc.net/RCKH_ATIS'
};

// 機場名稱對應
const AIRPORT_NAMES = {
    'RCSS': '松山機場 Songshan Airport',
    'RCTP': '桃園機場 Taoyuan Airport',
    'RCKH': '高雄機場 Kaohsiung Airport'
};

/**
 * 處理 ATIS 請求
 * @param {string} airportCode - 機場代碼 (RCSS, RCTP, RCKH)
 */
async function processATIS(airportCode) {
    // 防止重複點擊
    if (currentProcessing) {
        alert('處理中，請稍候...');
        return;
    }

    currentProcessing = airportCode;

    try {
        // 重置 UI
        resetUI();

        // 播放 ATIS 音訊
        playATISAudio(airportCode);

        // 顯示 loading
        showLoading(true);

        // 更新按鈕狀態
        updateButtonState(airportCode, 'processing');

        // 更新 loading 狀態文字
        updateLoadingStatus('正在錄製 ATIS 音訊 (90秒)...');

        // 呼叫後端 API
        const response = await fetch('/api/process_atis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                airport_code: airportCode
            })
        });

        const data = await response.json();

        // 隱藏 loading
        showLoading(false);

        if (response.ok && data.status === 'success') {
            // 顯示成功結果
            displayResults(data);

            // 更新按鈕狀態
            updateButtonState(airportCode, 'completed');

        } else {
            // 顯示錯誤訊息
            showError(data.message || '處理失敗，請稍後再試');

            // 重置按鈕
            updateButtonState(airportCode, 'idle');
        }

    } catch (error) {
        console.error('處理 ATIS 時發生錯誤:', error);

        showLoading(false);
        showError('網路錯誤或伺服器無回應，請檢查網路連線');

        if (currentProcessing) {
            updateButtonState(currentProcessing, 'idle');
        }

    } finally {
        currentProcessing = null;
    }
}

/**
 * 顯示結果
 * @param {Object} data - API 回傳資料
 */
function displayResults(data) {
    // 顯示結果區塊
    const resultSection = document.getElementById('result-section');
    resultSection.style.display = 'block';

    // 顯示翻譯內容
    displayTranslation(data.translation, data.original_text);

    // 顯示天氣簡圖
    displayWeatherImage(data.image_url, data.airport_code);

    // 滑動到結果區
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * 顯示翻譯內容
 * @param {Object} translation - 翻譯資料
 * @param {string} originalText - 原始 ATIS 文字
 */
function displayTranslation(translation, originalText) {
    const container = document.getElementById('translation-content');

    let html = '<div class="translation-content">';

    // 標題
    html += `<h3 style="color: #2563eb; margin-bottom: 20px;">✈️ ${translation.airport || '機場資訊'}</h3>`;

    // 資訊代碼和時間
    if (translation.info_code || translation.time) {
        html += '<div style="background: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">';
        if (translation.info_code) {
            html += `<p><strong>🔤 資訊代碼：</strong>${translation.info_code}</p>`;
        }
        if (translation.time) {
            html += `<p><strong>⏰ 時間：</strong>${translation.time}</p>`;
        }
        html += '</div>';
    }

    // 跑道與進場
    html += '<h4 style="color: #1e293b; margin: 20px 0 10px 0;">✈️ 跑道與進場</h4>';
    html += '<ul style="list-style: none; padding: 0;">';
    if (translation.runway) {
        html += `<li style="padding: 8px 0;"><strong>使用跑道：</strong>${translation.runway}</li>`;
    }
    if (translation.approach) {
        html += `<li style="padding: 8px 0;"><strong>進場程序：</strong>${translation.approach}</li>`;
    }
    html += '</ul>';

    // 天氣狀況
    html += '<h4 style="color: #1e293b; margin: 20px 0 10px 0;">🌤️ 天氣狀況</h4>';
    html += '<ul style="list-style: none; padding: 0;">';
    if (translation.wind) {
        html += `<li style="padding: 8px 0;"><strong>風向風速：</strong>${translation.wind}</li>`;
    }
    if (translation.visibility) {
        html += `<li style="padding: 8px 0;"><strong>能見度：</strong>${translation.visibility}</li>`;
    }
    if (translation.clouds) {
        html += `<li style="padding: 8px 0;"><strong>雲況：</strong>${translation.clouds}</li>`;
    }
    if (translation.temperature) {
        html += `<li style="padding: 8px 0;"><strong>溫度：</strong>${translation.temperature}</li>`;
    }
    if (translation.dewpoint) {
        html += `<li style="padding: 8px 0;"><strong>露點：</strong>${translation.dewpoint}</li>`;
    }
    if (translation.qnh) {
        html += `<li style="padding: 8px 0;"><strong>氣壓 (QNH)：</strong>${translation.qnh}</li>`;
    }
    html += '</ul>';

    // 備註
    if (translation.remarks && translation.remarks !== '未提供') {
        html += '<h4 style="color: #1e293b; margin: 20px 0 10px 0;">📝 備註</h4>';
        html += `<p style="background: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">${translation.remarks}</p>`;
    }

    // 摘要
    if (translation.summary) {
        html += '<h4 style="color: #1e293b; margin: 20px 0 10px 0;">💬 摘要</h4>';
        html += `<p style="background: #dbeafe; padding: 15px; border-radius: 8px; font-size: 1.05rem; line-height: 1.7;">${translation.summary}</p>`;
    }

    // 原始文字（可摺疊）
    if (originalText) {
        html += '<details style="margin-top: 30px;">';
        html += '<summary style="cursor: pointer; font-weight: 600; color: #64748b; padding: 10px 0;">📄 查看原始 ATIS 文字</summary>';
        html += `<pre style="background: #f8fafc; padding: 15px; border-radius: 8px; overflow-x: auto; margin-top: 10px; font-size: 0.9rem;">${originalText}</pre>`;
        html += '</details>';
    }

    html += '</div>';

    container.innerHTML = html;
}

/**
 * 顯示天氣簡圖
 * @param {string} imageUrl - 圖片 URL
 * @param {string} airportCode - 機場代碼
 */
function displayWeatherImage(imageUrl, airportCode) {
    const container = document.getElementById('image-content');

    const html = `
        <div class="weather-image">
            <img src="${imageUrl}" alt="${airportCode} Weather Diagram"
                 style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
                 onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'400\\' height=\\'300\\'%3E%3Crect width=\\'400\\' height=\\'300\\' fill=\\'%23f1f5f9\\'/%3E%3Ctext x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' fill=\\'%2364748b\\' font-size=\\'20\\'%3E圖片載入失敗%3C/text%3E%3C/svg%3E';">
            <p style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
                由 Gemini Nano Banana 自動生成
            </p>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * 顯示/隱藏 Loading
 * @param {boolean} show - 是否顯示
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

/**
 * 更新 Loading 狀態文字
 * @param {string} status - 狀態文字
 */
function updateLoadingStatus(status) {
    const statusElement = document.getElementById('loading-status');
    if (statusElement) {
        statusElement.textContent = status;
    }
}

/**
 * 顯示錯誤訊息
 * @param {string} message - 錯誤訊息
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    errorText.textContent = message;
    errorDiv.style.display = 'flex';

    // 3 秒後自動關閉（如果使用者沒有手動關閉）
    setTimeout(() => {
        if (errorDiv.style.display === 'flex') {
            closeError();
        }
    }, 5000);
}

/**
 * 關閉錯誤訊息
 */
function closeError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.style.display = 'none';
}

/**
 * 更新按鈕狀態
 * @param {string} airportCode - 機場代碼
 * @param {string} state - 狀態 (idle, processing, completed)
 */
function updateButtonState(airportCode, state) {
    const buttons = document.querySelectorAll('.airport-btn');

    buttons.forEach(btn => {
        const code = btn.getAttribute('data-airport');

        // 重置所有按鈕
        btn.classList.remove('processing', 'completed');

        // 設定目標按鈕狀態
        if (code === airportCode) {
            if (state === 'processing') {
                btn.classList.add('processing');
            } else if (state === 'completed') {
                btn.classList.add('completed');

                // 3 秒後移除完成狀態
                setTimeout(() => {
                    btn.classList.remove('completed');
                }, 3000);
            }
        }
    });
}

/**
 * 重置 UI
 */
function resetUI() {
    // 隱藏錯誤訊息
    closeError();

    // 可選：清空之前的結果（如果想保留則註解掉）
    // const resultSection = document.getElementById('result-section');
    // resultSection.style.display = 'none';
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('ATIS Monster 已載入');

    // 可以在這裡加入健康檢查
    checkHealth();
});

/**
 * 健康檢查
 */
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            console.log('✅ 系統狀態正常');
            console.log('Gemini API:', data.gemini_api_configured ? '已設定' : '未設定');
        }
    } catch (error) {
        console.error('健康檢查失敗:', error);
    }
}

/**
 * 播放 ATIS 音訊
 * @param {string} airportCode - 機場代碼
 */
function playATISAudio(airportCode) {
    const streamUrl = ATIS_STREAMS[airportCode];
    const airportName = AIRPORT_NAMES[airportCode];

    if (!streamUrl) {
        console.error('找不到機場的 ATIS 串流:', airportCode);
        return;
    }

    // 顯示音訊播放器區塊
    const audioSection = document.getElementById('audio-player-section');
    const audioPlayer = document.getElementById('atis-audio-player');
    const airportNameElement = document.getElementById('audio-airport-name');

    // 更新機場名稱
    airportNameElement.textContent = airportName;

    // 設定音訊來源並播放
    audioPlayer.src = streamUrl;
    audioPlayer.load();
    audioPlayer.play();

    // 顯示播放器
    audioSection.style.display = 'block';

    console.log('開始播放 ATIS:', airportCode, streamUrl);
}

/**
 * 停止 ATIS 音訊播放
 */
function stopATISAudio() {
    const audioSection = document.getElementById('audio-player-section');
    const audioPlayer = document.getElementById('atis-audio-player');

    // 停止播放
    audioPlayer.pause();
    audioPlayer.src = '';

    // 隱藏播放器
    audioSection.style.display = 'none';

    console.log('已停止 ATIS 播放');
}
