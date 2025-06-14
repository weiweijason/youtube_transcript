#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 逐字稿分析器 - 更新版
功能：
1. 接收 YouTube URL
2. 提取影片逐字稿
3. 使用 LLM 進行翻譯/標點符號處理
4. 生成摘要
"""

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
        # 載入 Whisper 模型
        self.whisper_model = whisper.load_model("base")
        
        print("正在連接 LLM...")
        # 連接 Ollama LLM
        try:
            self.llm = Ollama(model="gemma:7b")
            # 測試連接
            test_response = self.llm.invoke("Hello")
            print("LLM 連接成功！")
        except Exception as e:
            print(f"LLM 連接失敗: {e}")
            print("請確保 Ollama 已安裝並運行 gemma:7b 模型")

    def get_youtube_url(self):
        """詢問使用者輸入 YouTube URL"""
        while True:
            url = input("請輸入 YouTube 影片 URL: ").strip()
            if self.validate_youtube_url(url):
                return url
            else:
                print("無效的 YouTube URL，請重新輸入")
    
    def validate_youtube_url(self, url):
        """驗證 YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
    
    def run(self):
        """主執行方法"""
        print("=== YouTube 逐字稿分析器 ===")
        print("此工具可以:")
        print("1. 下載 YouTube 影片音訊")
        print("2. 使用 Whisper 生成逐字稿")
        print("3. 使用 LLM 翻譯/加標點")
        print("4. 生成摘要")
        print("=" * 40)
        
        try:
            # 獲取 YouTube URL
            url = self.get_youtube_url()
            
            # 下載音訊
            audio_file = self.download_audio(url)
            if not audio_file:
                print("音訊下載失敗，程式結束")
                return
            
            # 提取逐字稿
            transcript = self.extract_transcript(audio_file)
            if not transcript:
                print("逐字稿提取失敗，程式結束")
                return
            
            print("\n=== 原始逐字稿 ===")
            print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
            
            # 語言檢測
            is_english = self.detect_language(transcript)
            
            # 處理逐字稿
            processed_transcript = self.process_transcript_with_llm(transcript, is_english)
            
            print("\n=== 處理後的逐字稿 ===")
            print(processed_transcript[:500] + "..." if len(processed_transcript) > 500 else processed_transcript)
            
            # 生成摘要
            summary = self.generate_summary(processed_transcript)
            
            print("\n=== 摘要 ===")
            print(summary)
            
            # 清理暫存檔案
            self.cleanup_temp_files(audio_file)
            
            print("\n分析完成！")
            
        except KeyboardInterrupt:
            print("\n\n程式被使用者中斷")
        except Exception as e:
            print(f"執行過程中發生錯誤: {e}")
        finally:
            print("清理資源...")
    
    def extract_transcript(self, audio_file):
        """使用 Whisper 提取逐字稿"""
        print("正在使用 Whisper 提取逐字稿...")
        
        try:
            # 檢查檔案是否存在
            if not os.path.exists(audio_file):
                print(f"音訊檔案不存在: {audio_file}")
                return None
            
            # 使用 Whisper 轉錄
            result = self.whisper_model.transcribe(
                audio_file,
                language=None,  # 自動檢測語言
                task="transcribe",
                verbose=False
            )
            
            transcript = result["text"].strip()
            detected_language = result.get("language", "unknown")
            
            print(f"逐字稿提取完成！檢測到的語言: {detected_language}")
            print(f"逐字稿長度: {len(transcript)} 個字符")
            
            return transcript
            
        except Exception as e:
            print(f"逐字稿提取失敗: {e}")
            return None
    
    def detect_language(self, text):
        """簡單的語言檢測"""
        # 檢查是否包含中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        english_chars = re.findall(r'[a-zA-Z]', text)
        
        chinese_ratio = len(chinese_chars) / len(text) if text else 0
        english_ratio = len(english_chars) / len(text) if text else 0
        
        print(f"語言檢測 - 中文比例: {chinese_ratio:.2%}, 英文比例: {english_ratio:.2%}")
        # 如果英文字符比例較高，認為是英文
        return english_ratio > chinese_ratio and english_ratio > 0.3

    def process_transcript_with_llm(self, transcript, is_english):
        """使用 LLM 處理逐字稿"""
        if not self.llm:
            print("LLM 未連接，跳過處理")
            return transcript
        
        try:
            if is_english:
                print("正在將英文逐字稿翻譯成中文...")
                prompt = f"""
請將以下英文逐字稿翻譯成繁體中文，保持原意和語調：

{transcript}

請只回傳翻譯結果，不要其他說明：
"""
            else:
                print("正在為中文逐字稿添加標點符號...")
                prompt = f"""
請為以下中文逐字稿添加適當的標點符號和段落分隔，讓文本更容易閱讀：

{transcript}

請只回傳處理後的文本，不要其他說明：
"""
            
            # 調用 LLM
            response = self.llm.invoke(prompt)
            processed_text = response.strip()
            
            print("LLM 處理完成！")
            return processed_text
            
        except Exception as e:
            print(f"LLM 處理失敗: {e}")
            return transcript
    
    def generate_summary(self, transcript):
        """生成摘要"""
        if not self.llm:
            print("LLM 未連接，無法生成摘要")
            return "無法生成摘要：LLM 未連接"
        
        try:
            print("正在生成摘要...")
            prompt = f"""
請為以下文本生成條列式摘要，用繁體中文回應：

{transcript}

請以條列式格式回應，每個要點以「•」開頭：
"""
            
            response = self.llm.invoke(prompt)
            summary = response.strip()
            
            print("摘要生成完成！")
            return summary
            
        except Exception as e:
            print(f"摘要生成失敗: {e}")
            return "摘要生成失敗"
    
    def cleanup_temp_files(self, audio_file):
        """清理暫存檔案"""
        try:
            if audio_file and os.path.exists(audio_file):
                # 清理音訊檔案及其目錄
                temp_dir = os.path.dirname(audio_file)
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                print("暫存檔案已清理")
        except Exception as e:
            print(f"清理暫存檔案時出現錯誤: {e}")

    def get_available_formats(self, url):
        """獲取可用的音訊格式"""
        print("正在檢查可用的音訊格式...")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # 篩選出音訊格式，特別關注 m3u8 格式的純音訊
                audio_formats = []
                for f in formats:
                    # 檢查是否為音訊格式
                    format_note = f.get('format_note', '').lower()
                    acodec = f.get('acodec', 'none')
                    vcodec = f.get('vcodec', 'none')
                    format_id = f.get('format_id', '')
                    
                    # 根據您的輸出，233 和 234 是 audio only 格式
                    if ('audio only' in format_note or 
                        format_id in ['233', '234'] or
                        (acodec != 'none' and vcodec == 'none')):
                        
                        format_info = {
                            'format_id': format_id,
                            'ext': f.get('ext', 'mp4'),
                            'acodec': acodec,
                            'quality': f.get('quality', 0),
                            'format_note': format_note,
                            'protocol': f.get('protocol', ''),
                            'is_audio_only': True
                        }
                        audio_formats.append(format_info)
                
                # 優先選擇格式 234 (高品質)，然後是 233 (低品質)
                audio_formats.sort(key=lambda x: (
                    x['format_id'] == '234',  # 優先高品質音訊
                    x['format_id'] == '233',  # 然後是低品質音訊
                    x.get('quality', 0)
                ), reverse=True)
                
                if audio_formats:
                    print(f"找到 {len(audio_formats)} 個音訊格式:")
                    for fmt in audio_formats[:3]:
                        print(f"  ID: {fmt['format_id']}, 格式: {fmt['ext']}, 說明: {fmt['format_note']}")
                
                return audio_formats, info
                
        except Exception as e:
            print(f"獲取格式列表失敗: {e}")
            return [], {}

    def download_audio_by_format(self, url, format_id):
        """根據指定格式 ID 下載音訊"""
        print(f"使用格式 ID {format_id} 下載音訊...")
        
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "audio.%(ext)s")
        
        # 針對 m3u8 格式的特殊配置
        ydl_opts = {
            'format': format_id,
            'outtmpl': output_path,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            },
            'no_warnings': True,
            'ignoreerrors': False,
        }
        
        # 如果不是 m3u8 格式，添加音訊提取後處理器
        if format_id not in ['233', '234']:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 尋找下載的檔案
            for ext in ['wav', 'mp4', 'm4a', 'webm', 'mp3']:
                audio_file = os.path.join(temp_dir, f"audio.{ext}")
                if os.path.exists(audio_file):
                    print(f"音訊下載成功！檔案: {audio_file}")
                    return audio_file
            
            # 尋找其他可能的檔案名
            for file in os.listdir(temp_dir):
                if file.startswith('audio') and not file.endswith('.part'):
                    audio_file = os.path.join(temp_dir, file)
                    print(f"找到音訊檔案: {audio_file}")
                    return audio_file
            
            raise FileNotFoundError("找不到下載的音訊檔案")
            
        except Exception as e:
            print(f"格式 {format_id} 下載失敗: {e}")
            return None

    def download_audio(self, url):
        """改進的音訊下載方法"""
        print("正在下載影片音訊...")
        
        # 1. 獲取可用格式
        audio_formats, info = self.get_available_formats(url)
        
        if info:
            print(f"影片標題: {info.get('title', '未知')}")
            print(f"影片長度: {info.get('duration', 0)} 秒")
        
        if not audio_formats:
            print("未找到可用的音訊格式，嘗試備用方法...")
            return self.download_audio_fallback(url)
        
        # 2. 按優先順序嘗試下載音訊格式
        for fmt in audio_formats:
            print(f"嘗試下載格式 {fmt['format_id']} ({fmt['format_note']})")
            result = self.download_audio_by_format(url, fmt['format_id'])
            if result:
                return result
        
        # 3. 如果音訊格式都失敗，嘗試備用方法
        print("音訊格式下載失敗，嘗試備用方法...")
        return self.download_audio_fallback(url)

    def download_audio_fallback(self, url):
        """備用下載方法"""
        print("使用備用下載策略...")
        
        temp_dir = tempfile.mkdtemp()
        
        # 嘗試多種備用策略
        fallback_strategies = [
            {
                'format': 'worstaudio',
                'description': '最低品質音訊'
            },
            {
                'format': 'worst[height<=360]',
                'description': '低解析度影片（含音訊）'
            },
            {
                'format': 'worst',
                'description': '最低品質影片'
            }
        ]
        
        for i, strategy in enumerate(fallback_strategies):
            print(f"備用策略 {i+1}: {strategy['description']}")
            
            ydl_opts = {
                'format': strategy['format'],
                'outtmpl': os.path.join(temp_dir, f"backup_{i}.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '128',
                }],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                },
                'no_warnings': True,
                'ignoreerrors': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 檢查下載結果
                for ext in ['wav', 'mp4', 'm4a', 'webm', 'mp3']:
                    audio_file = os.path.join(temp_dir, f"backup_{i}.{ext}")
                    if os.path.exists(audio_file):
                        print(f"備用方法成功！檔案: {audio_file}")
                        return audio_file
                
                # 檢查所有檔案
                for file in os.listdir(temp_dir):
                    if file.startswith(f'backup_{i}') and not file.endswith('.part'):
                        audio_file = os.path.join(temp_dir, file)
                        print(f"備用方法找到檔案: {audio_file}")
                        return audio_file
                        
            except Exception as e:
                print(f"備用策略 {i+1} 失敗: {e}")
                continue
        
        print("所有下載方法都失敗了")
        return None


def main():
    """主函數"""
    analyzer = YouTubeTranscriptAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    main()
