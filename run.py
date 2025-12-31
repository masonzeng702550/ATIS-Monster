"""
ATIS Monster 主程式入口
執行此檔案來啟動 Flask 應用程式
"""

import os
from app import create_app

# 建立 Flask 應用程式實例
app = create_app()

if __name__ == '__main__':
    # 取得環境變數
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')

    print("=" * 60)
    print("🛫 ATIS Monster - 台灣機場自動情報服務翻譯系統")
    print("=" * 60)
    print(f"📡 伺服器位址: http://localhost:{port}")
    print(f"🔧 除錯模式: {'開啟' if debug_mode else '關閉'}")
    print(f"🔑 Gemini API: {'已設定' if app.config.get('GEMINI_API_KEY') else '未設定'}")
    print("=" * 60)
    print("支援機場：")
    print("  ✈️  RCSS - 松山機場")
    print("  ✈️  RCTP - 桃園機場")
    print("  ✈️  RCKH - 高雄機場")
    print("=" * 60)
    print("\n按 Ctrl+C 停止伺服器\n")

    # 啟動 Flask 開發伺服器
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )
