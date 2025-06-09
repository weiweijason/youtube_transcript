# Docker 部署指南

這個目錄包含了將 YouTube 逐字稿分析器容器化的所有必要文件。

## 📁 Docker 相關檔案

- `Dockerfile` - 完整版 Docker 映像
- `Dockerfile.light` - 輕量版 Docker 映像（推薦）
- `docker-compose.yml` - Docker Compose 配置
- `.dockerignore` - Docker 建構忽略文件

## 🚀 快速開始

### 方法 1: 使用 Docker Compose（推薦）

```powershell
# 建構並啟動容器
docker-compose up --build

# 在背景執行
docker-compose up -d --build

# 查看日誌
docker-compose logs -f

# 停止容器
docker-compose down
```

### 方法 2: 使用 Docker 命令

```powershell
# 建構映像（完整版）
docker build -t youtube-analyzer .

# 建構映像（輕量版）
docker build -f Dockerfile.light -t youtube-analyzer-light .

# 執行容器
docker run -it --rm -p 11434:11434 youtube-analyzer-light
```

## 🔧 使用方式

1. **啟動容器**：
   ```powershell
   docker-compose up --build
   ```

2. **等待初始化**：
   - 容器會自動下載和設定 Ollama
   - 下載 Gemma 7B 模型（首次需要較長時間）

3. **開始使用**：
   - 在終端中輸入 YouTube URL
   - 等待程式處理並顯示結果

## 💡 版本選擇

### 完整版 (`Dockerfile`)
- **優點**: 功能完整，錯誤處理較好
- **缺點**: 資源需求較高
- **適用**: 正式環境，資源充足

### 輕量版 (`Dockerfile.light`)
- **優點**: 資源占用少，啟動快
- **缺點**: 功能相對精簡
- **適用**: 測試環境，資源有限

## 🔧 環境要求

### 最低要求
- **CPU**: 2 核心
- **記憶體**: 4GB RAM
- **磁碟**: 10GB 可用空間
- **網路**: 穩定的網路連線（用於下載模型）

### 建議配置
- **CPU**: 4 核心或以上
- **記憶體**: 8GB RAM 或以上
- **磁碟**: 20GB 可用空間

## 🐛 疑難排解

### 常見問題

1. **容器啟動失敗**
   ```powershell
   # 檢查日誌
   docker-compose logs
   
   # 重新建構
   docker-compose down
   docker-compose up --build
   ```

2. **記憶體不足**
   ```powershell
   # 修改 docker-compose.yml 中的記憶體限制
   # 或使用輕量版 Dockerfile
   docker build -f Dockerfile.light -t youtube-analyzer-light .
   ```

3. **模型下載失敗**
   ```powershell
   # 進入容器手動下載
   docker exec -it youtube_transcript_analyzer bash
   ollama pull gemma:7b
   ```

4. **端口衝突**
   ```powershell
   # 修改 docker-compose.yml 中的端口映射
   ports:
     - "11435:11434"  # 改為其他端口
   ```

### 檢查容器狀態

```powershell
# 查看運行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器日誌
docker logs youtube_transcript_analyzer

# 進入容器
docker exec -it youtube_transcript_analyzer bash
```

### 清理資源

```powershell
# 停止並移除容器
docker-compose down

# 移除映像
docker rmi youtube-analyzer

# 清理未使用的資源
docker system prune -a
```

## 📝 使用範例

1. **啟動容器**：
   ```powershell
   PS C:\path\to\project> docker-compose up --build
   ```

2. **等待初始化完成**（看到以下訊息）：
   ```
   ✅ 環境準備完成！
   🎬 啟動 YouTube 逐字稿分析器...
   請輸入 YouTube 影片 URL:
   ```

3. **輸入 YouTube URL**：
   ```
   請輸入 YouTube 影片 URL: https://www.youtube.com/watch?v=example
   ```

4. **查看結果**：
   - 原始逐字稿
   - 翻譯/標點符號處理結果
   - 條列式摘要

## 🔄 更新和維護

### 更新程式碼
```powershell
# 重新建構映像
docker-compose down
docker-compose up --build
```

### 更新模型
```powershell
# 進入容器更新模型
docker exec -it youtube_transcript_analyzer bash
ollama pull gemma:7b
```

## 📋 注意事項

1. **首次執行**會需要較長時間下載模型
2. **影片長度**建議控制在 5 分鐘以內
3. **網路連線**必須穩定，用於下載影片和模型
4. **磁碟空間**確保有足夠空間存放模型（約 5-8GB）
5. **資源監控**可使用 `docker stats` 監控資源使用情況

## 🆘 支援

如果遇到問題，請檢查：
1. Docker 和 Docker Compose 版本
2. 系統資源是否充足
3. 網路連線是否正常
4. 防火牆設定是否正確
