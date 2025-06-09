"""
YouTube 逐字稿分析器 - 簡化版
適用於資源有限的環境

作業要求：
1. 詢問使用者輸入 YouTube URL ✓
2. 提取並印出逐字稿 ✓
3. 使用 LLM 翻譯或加標點符號 ✓
4. 生成條列式摘要 ✓
"""

# 第一步：安裝必要套件
print("正在安裝必要套件...")
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import yt_dlp
    import whisper
    from langchain_community.llms import Ollama
except ImportError:
    print("安裝套件中...")
    install_package("yt-dlp")
    install_package("openai-whisper")
    install_package("langchain-community")
    
    import yt_dlp
    import whisper
    from langchain_community.llms import Ollama

import os
import re
import tempfile
import warnings
warnings.filterwarnings("ignore")

class SimpleYouTubeAnalyzer:
    def __init__(self):
        self.whisper_model = None
        self.llm = None
        print("初始化分析器...")
    
    def setup_whisper(self):
        """設置 Whisper 模型"""
        if self.whisper_model is None:
            print("載入 Whisper 模型...")
            self.whisper_model = whisper.load_model("tiny")  # 使用最小模型節省記憶體
            print("Whisper 模型載入完成")
    
    def setup_llm(self): 
        """設置 LLM"""
        if self.llm is None:
            print("連接 LLM...")
            try:
                self.llm = Ollama(model="gemma:7b")
                # 簡單測試
                self.llm.invoke("hi")
                print("LLM 連接成功")
            except Exception as e:
                print(f"LLM 連接失敗: {e}")
                print("請確保 Ollama 正在運行且已安裝 gemma:7b")
                return False
        return True
    
    def get_youtube_url(self):
        """步驟1: 詢問使用者輸入 YouTube URL"""
        print("\n=== 步驟1: 輸入 YouTube URL ===")
        url = input("請輸入 YouTube 影片 URL: ").strip()
        print(f"✓ 已接收 URL: {url}")
        return url
    
    def download_and_extract(self, url):
        """步驟2: 下載音訊並提取逐字稿"""
        print("\n=== 步驟2: 提取逐字稿 ===")
        
        # 下載音訊
        print("下載影片音訊...")
        temp_audio = "/tmp/temp_audio.wav"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_audio.replace('.wav', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(temp_audio):
                print("✓ 音訊下載完成")
            else:
                print("✗ 音訊下載失敗")
                return None, None
            
            # 提取逐字稿
            print("提取逐字稿...")
            self.setup_whisper()
            result = self.whisper_model.transcribe(temp_audio)
            
            transcript = result["text"].strip()
            language = result["language"]
            
            print(f"✓ 逐字稿提取完成 (語言: {language})")
            
            # 清理臨時檔案
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            
            return transcript, language
            
        except Exception as e:
            print(f"✗ 處理失敗: {e}")
            return None, None
    
    def process_with_llm(self, transcript, language):
        """步驟3: 使用 LLM 處理逐字稿"""
        print(f"\n=== 步驟3: LLM 處理 (語言: {language}) ===")
        
        if not self.setup_llm():
            return transcript
        
        if language == "en":
            print("翻譯英文逐字稿為中文...")
            prompt = f"請將以下英文翻譯成繁體中文：\n\n{transcript}\n\n翻譯："
        else:
            print("為中文逐字稿加上標點符號...")
            prompt = f"請為以下中文文本加上標點符號：\n\n{transcript}\n\n結果："
        
        try:
            processed = self.llm.invoke(prompt)
            print("✓ LLM 處理完成")
            return processed.strip()
        except Exception as e:
            print(f"✗ LLM 處理失敗: {e}")
            return transcript
    
    def generate_summary(self, text):
        """步驟4: 生成摘要"""
        print("\n=== 步驟4: 生成摘要 ===")
        
        if not self.llm:
            return "無法生成摘要（LLM 未連接）"
        
        prompt = f"""請將以下內容整理成條列式重點摘要，用繁體中文回答：

{text}

請用這個格式：
• 重點一
• 重點二  
• 重點三

摘要："""
        
        try:
            summary = self.llm.invoke(prompt)
            print("✓ 摘要生成完成")
            return summary.strip()
        except Exception as e:
            print(f"✗ 摘要生成失敗: {e}")
            return "摘要生成失敗"
    
    def run(self):
        """執行完整流程"""
        print("🎬 YouTube 逐字稿分析器")
        print("=" * 40)
        
        # 步驟1: 獲取 URL
        url = self.get_youtube_url()
        
        # 步驟2: 提取逐字稿
        transcript, language = self.download_and_extract(url)
        if not transcript:
            print("❌ 程式執行失敗")
            return
        
        # 顯示原始逐字稿
        print(f"\n📝 原始逐字稿 ({language}):")
        print("-" * 40)
        print(transcript)
        
        # 步驟3: LLM 處理
        processed_transcript = self.process_with_llm(transcript, language)
        
        # 顯示處理後的逐字稿
        title = "翻譯結果:" if language == "en" else "加標點符號後:"
        print(f"\n🔄 {title}")
        print("-" * 40)
        print(processed_transcript)
        
        # 步驟4: 生成摘要
        summary = self.generate_summary(processed_transcript)
        
        # 顯示摘要
        print(f"\n📋 摘要:")
        print("-" * 40)
        print(summary)
        
        print(f"\n✅ 程式執行完成！")

def main():
    """主程式"""
    analyzer = SimpleYouTubeAnalyzer()
    analyzer.run()

# 執行程式
if __name__ == "__main__":
    main()
