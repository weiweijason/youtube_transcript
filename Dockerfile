# YouTube 逐字稿分析器 Dockerfile
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# 複製 requirements 文件並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式文件
COPY youtube_transcript_analyzer.py .
COPY simple_analyzer.py .
COPY README.md .

# 創建必要的目錄
RUN mkdir -p /tmp/youtube_analyzer

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# 暴露 Ollama 服務端口
EXPOSE 11434

# 創建啟動腳本
RUN echo '#!/bin/bash\n\
echo "啟動 Ollama 服務..."\n\
ollama serve &\n\
\n\
echo "等待 Ollama 服務啟動..."\n\
sleep 10\n\
\n\
echo "下載 Gemma 7B 模型..."\n\
ollama pull gemma:7b\n\
\n\
echo "模型準備完成，啟動應用程式..."\n\
python youtube_transcript_analyzer.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# 設定入口點
CMD ["/app/start.sh"]
