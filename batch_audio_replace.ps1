# 批量替换视频音频的PowerShell脚本
# 使用方法: .\batch_audio_replace.ps1 -InputDir "input_videos" -OutputDir "output_videos"

param(
    [string]$InputDir = "output",
    [string]$OutputDir = "output_replaced",
    [string]$ConfigFile = "config.json",
    [string]$Voice = "",
    [switch]$UseManualText,
    [string]$TextFile = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  批量视频音频替换工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 获取所有视频文件
$videoExtensions = @("*.mp4", "*.mkv", "*.avi", "*.mov", "*.wmv")
$videoFiles = @()

foreach ($ext in $videoExtensions) {
    $videoFiles += Get-ChildItem -Path $InputDir -Filter $ext -File
}

if ($videoFiles.Count -eq 0) {
    Write-Host "未找到视频文件在 $InputDir" -ForegroundColor Red
    exit 1
}

Write-Host "找到 $($videoFiles.Count) 个视频文件" -ForegroundColor Green
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($video in $videoFiles) {
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "处理: $($video.Name)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    
    $outputFile = Join-Path $OutputDir $video.Name
    
    # 构建命令
    $cmdArgs = @(
        "audio_replacer.py",
        "`"$($video.FullName)`"",
        "`"$outputFile`"",
        "--config", "`"$ConfigFile`""
    )
    
    if ($Voice) {
        $cmdArgs += "--voice", "`"$Voice`""
    }
    
    if ($UseManualText -and $TextFile -and (Test-Path $TextFile)) {
        $cmdArgs += "--text-file", "`"$TextFile`""
    }
    
    $cmd = "python " + ($cmdArgs -join " ")
    
    Write-Host "执行: $cmd" -ForegroundColor Gray
    Write-Host ""
    
    try {
        & python $($cmdArgs)
        
        if (Test-Path $outputFile) {
            Write-Host "✅ 成功: $($video.Name)" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "❌ 失败: $($video.Name) - 输出文件不存在" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "❌ 失败: $($video.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  批量处理完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "成功: $successCount" -ForegroundColor Green
Write-Host "失败: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Gray" })
Write-Host "输出目录: $OutputDir" -ForegroundColor Cyan
