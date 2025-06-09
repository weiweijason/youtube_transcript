# YouTube 逐字稿分析器 - Google Colab 版本
# 請在 Google Colab 中執行此程式

# === 安裝必要套件 ===
!pip install yt-dlp
!pip install openai-whisper
!pip install langchain-community
!pip install langchain

# 安裝 Ollama（在 Colab 中）
!curl -fsSL https://ollama.com/install.sh | sh

# 啟動 Ollama 服務並下載 Gemma 7B 模型
!ollama serve > ollama.log 2>&1 &
import time
time.sleep(10)  # 等待服務啟動
!ollama pull gemma:7b

import os
import re
import yt_dlp
import whisper
import torch
from langchain_community.llms import Ollama
import tempfile
import warnings
warnings.filterwarnings("ignore")

class YouTubeTranscriptAnalyzer:
    def __init__(self):
        """初始化分析器"""
        self.whisper_model = None
        self.llm = None
        self.setup_models()
    
    def setup_models(self):
        """設置模型"""
        print("正在載入 Whisper 模型...")
        # 載入 Whisper 模型（在 Colab 中使用較小的模型以節省記憶體）
        self.whisper_model = whisper.load_model("base")
        
        print("正在連接 LLM...")
        # 連接 Ollama LLM
        try:
            self.llm = Ollama(model="gemma:7b", base_url="http://localhost:11434")
            # 測試連接
            test_response = self.llm.invoke("測試")
            print("LLM 連接成功！")
        except Exception as e:
            print(f"LLM 連接失敗: {e}")
            print("請確保 Ollama 服務正在運行")
    
    def get_youtube_url(self):
        """詢問使用者輸入 YouTube URL"""
        url = input("請輸入 YouTube 影片 URL: ").strip()
        if self.validate_youtube_url(url):
            return url
        else:
            print("URL 格式可能不正確，但仍嘗試處理...")
            return url
    
    def validate_youtube_url(self, url):
        """驗證 YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
    
    def download_audio(self, url):
        """下載 YouTube 影片音訊"""
        print("正在下載影片音訊...")
        
        # 在 Colab 中使用 /tmp 目錄
        output_path = "/tmp/audio.%(ext)s"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 找到下載的音訊檔案
            audio_file = "/tmp/audio.wav"
            if os.path.exists(audio_file):
                print("音訊下載完成！")
                return audio_file
            else:
                raise FileNotFoundError("音訊檔案未找到")
                
        except Exception as e:
            print(f"下載失敗: {e}")
            return None
    
    def extract_transcript(self, audio_file):
        """使用 Whisper 提取逐字稿"""
        print("正在提取逐字稿...")
        
        try:
            result = self.whisper_model.transcribe(audio_file)
            transcript = result["text"]
            detected_language = result["language"]
            
            print(f"檢測到的語言: {detected_language}")
            print("逐字稿提取完成！")
            
            return transcript, detected_language
            
        except Exception as e:
            print(f"逐字稿提取失敗: {e}")
            return None, None
    
    def detect_language(self, text):
        """檢測文本語言"""
        # 簡單的中英文檢測
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return "zh"
        else:
            return "en"
    
    def process_transcript_with_llm(self, transcript, language):
        """使用 LLM 處理逐字稿"""
        print(f"正在使用 LLM 處理逐字稿（語言: {language}）...")
        
        if language == "en":
            # 英文逐字稿翻譯成中文
            prompt = f"""請將以下英文逐字稿翻譯成繁體中文，保持原意並使用自然的中文表達：

{transcript}

請直接提供翻譯結果，不需要額外說明："""
        else:
            # 中文逐字稿加標點符號
            prompt = f"""請為以下中文逐字稿加上適當的標點符號，使其更容易閱讀：

{transcript}

請直接提供加上標點符號後的結果，不需要額外說明："""
        
        try:
            processed_text = self.llm.invoke(prompt)
            return processed_text.strip()
        except Exception as e:
            print(f"LLM 處理失敗: {e}")
            return transcript
    
    def generate_summary(self, text):
        """生成摘要"""
        print("正在生成摘要...")
        
        prompt = f"""請將以下文本整理成條列式摘要，用繁體中文回答：

{text}

請用以下格式整理成重點摘要：
• 重點一
• 重點二
• 重點三
（依內容長度調整重點數量）

請直接提供摘要，不需要額外說明："""
        
        try:
            summary = self.llm.invoke(prompt)
            return summary.strip()
        except Exception as e:
            print(f"摘要生成失敗: {e}")
            return "摘要生成失敗"
    
    def cleanup_temp_files(self, audio_file):
        """清理臨時檔案"""
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
                print("臨時檔案已清理")
        except Exception as e:
            print(f"清理臨時檔案時發生錯誤: {e}")
    
    def run(self):
        """主要執行流程"""
        print("=== YouTube 逐字稿分析器 ===")
        print()
        
        # 1. 獲取 YouTube URL
        url = self.get_youtube_url()
        print(f"您輸入的 URL: {url}")
        print()
        
        # 2. 下載音訊
        audio_file = self.download_audio(url)
        if not audio_file:
            print("音訊下載失敗，程式結束")
            return
        
        try:
            # 3. 提取逐字稿
            transcript, detected_language = self.extract_transcript(audio_file)
            if not transcript:
                print("逐字稿提取失敗，程式結束")
                return
            
            # 4. 顯示原始逐字稿
            print("\n" + "="*50)
            print("原始逐字稿:")
            print("="*50)
            print(transcript)
            print()
            
            # 5. 使用 LLM 處理逐字稿
            language = detected_language if detected_language else self.detect_language(transcript)
            processed_transcript = self.process_transcript_with_llm(transcript, language)
            
            print("\n" + "="*50)
            if language == "en":
                print("翻譯結果:")
            else:
                print("加標點符號後的結果:")
            print("="*50)
            print(processed_transcript)
            print()
            
            # 6. 生成摘要
            summary = self.generate_summary(processed_transcript)
            
            print("\n" + "="*50)
            print("摘要:")
            print("="*50)
            print(summary)
            print()
            
        finally:
            # 7. 清理臨時檔案
            self.cleanup_temp_files(audio_file)
        
        print("程式執行完成！")

# 執行程式
analyzer = YouTubeTranscriptAnalyzer()
analyzer.run()
