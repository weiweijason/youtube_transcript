# YouTube 逐字稿分析器 Docker 管理腳本
# 使用方式: ./docker-manager.ps1 [command]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "start", "stop", "restart", "logs", "clean", "status", "help")]
    [string]$Command = "help"
)

# 顏色輸出函數
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    
    switch ($Color) {
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Blue" { Write-Host $Message -ForegroundColor Blue }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

# 檢查 Docker 是否已安裝
function Test-DockerInstalled {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        return $true
    }
    catch {
        Write-ColorOutput "❌ Docker 或 Docker Compose 未安裝或未啟動" "Red"
        Write-ColorOutput "請先安裝 Docker Desktop: https://www.docker.com/products/docker-desktop" "Yellow"
        return $false
    }
}

# 顯示幫助信息
function Show-Help {
    Write-ColorOutput "🎬 YouTube 逐字稿分析器 Docker 管理工具" "Cyan"
    Write-ColorOutput "=" * 50 "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "使用方式: ./docker-manager.ps1 [command]" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "可用命令:" "Yellow"
    Write-ColorOutput "  build    - 建構 Docker 映像" "White"
    Write-ColorOutput "  start    - 啟動容器" "White"
    Write-ColorOutput "  stop     - 停止容器" "White"
    Write-ColorOutput "  restart  - 重新啟動容器" "White"
    Write-ColorOutput "  logs     - 查看容器日誌" "White"
    Write-ColorOutput "  status   - 查看容器狀態" "White"
    Write-ColorOutput "  clean    - 清理容器和映像" "White"
    Write-ColorOutput "  help     - 顯示此幫助信息" "White"
    Write-ColorOutput ""
    Write-ColorOutput "範例:" "Yellow"
    Write-ColorOutput "  ./docker-manager.ps1 build" "Green"
    Write-ColorOutput "  ./docker-manager.ps1 start" "Green"
    Write-ColorOutput "  ./docker-manager.ps1 logs" "Green"
}

# 建構映像
function Build-Container {
    Write-ColorOutput "🔨 建構 YouTube 逐字稿分析器映像..." "Blue"
    
    # 詢問使用哪個版本
    Write-ColorOutput "選擇要建構的版本:" "Yellow"
    Write-ColorOutput "1. 輕量版 (推薦，資源需求較低)" "Green"
    Write-ColorOutput "2. 完整版 (功能完整，資源需求較高)" "Green"
    
    do {
        $choice = Read-Host "請選擇 (1 或 2)"
    } while ($choice -notin @("1", "2"))
    
    if ($choice -eq "1") {
        Write-ColorOutput "建構輕量版映像..." "Blue"
        docker build -f Dockerfile.light -t youtube-analyzer-light .
    } else {
        Write-ColorOutput "建構完整版映像..." "Blue"
        docker build -t youtube-analyzer .
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 映像建構完成！" "Green"
    } else {
        Write-ColorOutput "❌ 映像建構失敗！" "Red"
    }
}

# 啟動容器
function Start-Container {
    Write-ColorOutput "🚀 啟動 YouTube 逐字稿分析器..." "Blue"
    
    # 檢查是否已有運行中的容器
    $running = docker ps --filter "name=youtube_transcript_analyzer" --format "table {{.Names}}" | Select-String "youtube_transcript_analyzer"
    
    if ($running) {
        Write-ColorOutput "⚠️  容器已在運行中" "Yellow"
        Write-ColorOutput "使用 'restart' 命令重新啟動容器" "Yellow"
        return
    }
    
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 容器啟動成功！" "Green"
        Write-ColorOutput "💡 使用 'logs' 命令查看啟動進度" "Yellow"
        Write-ColorOutput "💡 使用 'docker exec -it youtube_transcript_analyzer bash' 進入容器" "Yellow"
    } else {
        Write-ColorOutput "❌ 容器啟動失敗！" "Red"
    }
}

# 停止容器
function Stop-Container {
    Write-ColorOutput "🛑 停止容器..." "Blue"
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 容器已停止" "Green"
    } else {
        Write-ColorOutput "❌ 停止容器失敗！" "Red"
    }
}

# 重新啟動容器
function Restart-Container {
    Write-ColorOutput "🔄 重新啟動容器..." "Blue"
    docker-compose restart
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 容器重新啟動完成！" "Green"
    } else {
        Write-ColorOutput "❌ 重新啟動失敗！" "Red"
    }
}

# 查看日誌
function Show-Logs {
    Write-ColorOutput "📋 顯示容器日誌..." "Blue"
    Write-ColorOutput "按 Ctrl+C 退出日誌查看" "Yellow"
    docker-compose logs -f
}

# 查看狀態
function Show-Status {
    Write-ColorOutput "📊 容器狀態:" "Blue"
    Write-ColorOutput "=" * 30 "Blue"
    
    # 檢查容器狀態
    $containers = docker ps -a --filter "name=youtube_transcript_analyzer" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    if ($containers -match "youtube_transcript_analyzer") {
        Write-ColorOutput $containers "Green"
    } else {
        Write-ColorOutput "❌ 未找到相關容器" "Red"
    }
    
    Write-ColorOutput ""
    Write-ColorOutput "💾 映像列表:" "Blue"
    Write-ColorOutput "=" * 20 "Blue"
    docker images | Select-String "youtube-analyzer"
    
    Write-ColorOutput ""
    Write-ColorOutput "🖥️  系統資源使用:" "Blue"
    Write-ColorOutput "=" * 30 "Blue"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | Select-String "youtube"
}

# 清理資源
function Clean-Resources {
    Write-ColorOutput "🧹 清理 Docker 資源..." "Yellow"
    
    Write-ColorOutput "⚠️  這將移除所有相關的容器和映像" "Red"
    $confirm = Read-Host "確定要繼續嗎? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-ColorOutput "停止並移除容器..." "Blue"
        docker-compose down
        
        Write-ColorOutput "移除映像..." "Blue"
        docker rmi youtube-analyzer 2>$null
        docker rmi youtube-analyzer-light 2>$null
        
        Write-ColorOutput "清理未使用的資源..." "Blue"
        docker system prune -f
        
        Write-ColorOutput "✅ 清理完成！" "Green"
    } else {
        Write-ColorOutput "❌ 取消清理操作" "Yellow"
    }
}

# 主程式邏輯
if (-not (Test-DockerInstalled)) {
    exit 1
}

switch ($Command) {
    "build" { Build-Container }
    "start" { Start-Container }
    "stop" { Stop-Container }
    "restart" { Restart-Container }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "clean" { Clean-Resources }
    "help" { Show-Help }
    default { Show-Help }
}
