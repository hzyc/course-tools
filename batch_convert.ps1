# PPT批量转换脚本
# 使用前请确保：
# 1. 已安装Python和所需依赖
# 2. 已安装FFmpeg
# 3. config.json已正确配置

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  PPT批量转视频工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 设置文件夹路径
$inputFolder = "d:\Code\PPTtovideo\input"
$outputFolder = "d:\Code\PPTtovideo\output"

# 获取所有PPT文件
$pptFiles = Get-ChildItem -Path $inputFolder -Filter "*.pptx" | Sort-Object Name

Write-Host "找到 $($pptFiles.Count) 个PPT文件：" -ForegroundColor Green
foreach ($file in $pptFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor White
}
Write-Host ""

# 逐个转换
$successCount = 0
$failedCount = 0

foreach ($pptFile in $pptFiles) {
    Write-Host "--------------------------------------" -ForegroundColor Yellow
    Write-Host "正在处理：$($pptFile.Name)" -ForegroundColor Yellow
    Write-Host "--------------------------------------" -ForegroundColor Yellow
    
    $outputFileName = $pptFile.BaseName + ".mp4"
    $outputPath = Join-Path $outputFolder $outputFileName
    
    try {
        # 调用Python脚本进行转换
        python "d:\Code\PPTtovideo\main.py" $pptFile.FullName "-o" $outputPath
        
        Write-Host ""
        Write-Host "✅ $($pptFile.Name) 转换完成！" -ForegroundColor Green
        Write-Host "   输出：$outputPath" -ForegroundColor Gray
        $successCount++
    }
    catch {
        Write-Host ""
        Write-Host "❌ $($pptFile.Name) 转换失败！" -ForegroundColor Red
        Write-Host "   错误：$($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
    
    Write-Host ""
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  批量转换完成！" -ForegroundColor Cyan
Write-Host "  成功：$successCount" -ForegroundColor Green
Write-Host "  失败：$failedCount" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Cyan
