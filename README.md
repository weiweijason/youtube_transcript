# YouTube 逐字稿分析器

這是一個可以分析 YouTube 影片逐字稿並生成摘要的程式，完成以下功能：

## 功能特色

1. **URL 輸入**: 詢問使用者輸入 YouTube URL
2. **逐字稿提取**: 
   - 英文影片：提取英文逐字稿
   - 中文影片：提取沒有標點符號的逐字稿
3. **LLM 處理**:
   - 英文逐字稿：翻譯成中文
   - 中文逐字稿：加上標點符號
4. **摘要生成**: 將逐字稿整理成條列式摘要

## 檔案說明

### 1. `YouTube_Transcript_Analyzer.ipynb` (推薦)
- **適用於**: Google Colab
- **特點**: Jupyter Notebook 格式，分步驟執行
- **使用方式**: 直接在 Google Colab 中開啟並執行

### 2. `youtube_analyzer_colab.py`
- **適用於**: Google Colab
- **特點**: Python 腳本格式
- **使用方式**: 在 Colab 中執行整個腳本

### 3. `youtube_transcript_analyzer.py`
- **適用於**: 本地環境
- **特點**: 完整的 Python 類別實作
- **使用方式**: 需要先安裝依賴套件

## 使用方法

### 在 Google Colab 中使用（推薦）

1. 開啟 Google Colab
2. 上傳 `YouTube_Transcript_Analyzer.ipynb` 檔案
3. 依序執行每個 cell
4. 在提示時輸入 YouTube URL

### 在本地環境使用

1. 安裝依賴套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 安裝並設定 Ollama：
   ```bash
   # 安裝 Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   
   # 啟動服務
   ollama serve
   
   # 下載 Gemma 7B 模型
   ollama pull gemma:7b
   ```

3. 執行程式：
   ```bash
   python youtube_transcript_analyzer.py
   ```

## 依賴套件

- `yt-dlp`: YouTube 影片下載
- `openai-whisper`: 語音轉文字
- `langchain-community`: LLM 整合
- `torch`: PyTorch 深度學習框架
- `ffmpeg`: 音訊處理（需要系統安裝）

## 注意事項

1. **影片長度**: 建議測試影片長度控制在 4-5 分鐘以內，避免記憶體不足
2. **網路連線**: 需要穩定的網路連線下載影片和模型
3. **計算資源**: Whisper 和 LLM 模型需要一定的計算資源
4. **模型下載**: 首次使用時需要下載 Whisper 和 Gemma 模型，可能需要較長時間

## 程式流程

1. 使用者輸入 YouTube URL
2. 下載影片音訊檔案
3. 使用 Whisper 提取逐字稿並檢測語言
4. 根據語言使用 LLM 進行：
   - 英文 → 中文翻譯
   - 中文 → 加標點符號
5. 使用 LLM 生成條列式摘要
6. 清理臨時檔案

## 範例輸出

```
=== YouTube 逐字稿分析器 ===

請輸入 YouTube 影片 URL: https://www.youtube.com/watch?v=example

==================================================
原始逐字稿:
==================================================
Hello everyone, welcome to our channel...

==================================================
翻譯結果:
==================================================
大家好，歡迎來到我們的頻道...

==================================================
摘要:
==================================================
• 頻道介紹與歡迎詞
• 影片主要內容說明
• 重要觀點總結
```

## 疑難排解

### 常見問題

1. **LLM 連接失敗**
   - 確保 Ollama 服務正在運行
   - 檢查 Gemma 7B 模型是否已下載

2. **音訊下載失敗**
   - 檢查 YouTube URL 是否正確
   - 確認網路連線穩定
   - 檢查影片是否有地區限制

3. **記憶體不足**
   - 使用較短的測試影片
   - 在 Colab 中使用 GPU 運算環境

4. **FFmpeg 相關錯誤**
   - 在 Colab 中執行: `!apt install ffmpeg`
   - 在本地環境中安裝 FFmpeg

## 作業要求對照

✅ **能詢問使用者，讓他/她輸入一個 YouTube 的 URL（一分）**
- 實作在 `get_youtube_url()` 函數中

✅ **能印出逐字稿。如果影片是英文，則印出英文逐字稿。如果影片是中文，則印出沒有標點符號的逐字稿（兩分）**
- 使用 Whisper API 自動檢測語言並提取逐字稿

✅ **能連上一個大語言模型（LLM）。如果逐字稿是英文，則用 LLM 把逐字稿翻譯成中文印出。如果逐字稿是中文，則用 LLM 替它加上標點符號印出（兩分）**
- 使用 Ollama + Gemma 7B 模型進行處理

✅ **能要求大語言模型（LLM），將逐字稿摘要（Summarize）整理成條列（Bullet Points）的形式印出（兩分）**
- 實作在 `generate_summary()` 函數中

## 授權

此程式僅供學術用途使用。
