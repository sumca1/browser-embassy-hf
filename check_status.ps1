#!/usr/bin/env pwsh
<#
.SYNOPSIS
    בודק סטטוס Browser Embassy V5 ב-HuggingFace

.DESCRIPTION
    סקריפט מהיר לבדיקת זמינות ה-Space והשירותים שלו
#>

Write-Host "`n🔍 Browser Embassy V5 Status Check" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$spaceUrl = "https://kuperberg-browser-embassy.hf.space"

# 1. בדיקת API
Write-Host "`n1️⃣ בודק API..." -ForegroundColor Yellow
try {
    $api = Invoke-RestMethod -Uri "$spaceUrl/" -Method Get -TimeoutSec 10
    Write-Host "   ✅ API פעיל!" -ForegroundColor Green
    Write-Host "   📌 גרסה: $($api.service)" -ForegroundColor Cyan
    Write-Host "   📌 סטטוס: $($api.status)" -ForegroundColor Cyan
    if ($api.vnc_url) {
        Write-Host "   📌 VNC זמין: $($api.vnc_url)" -ForegroundColor Cyan
    }
} catch {
    if ($_.Exception.Message -match "503") {
        Write-Host "   ⏳ Space בונה או נרדם (503)" -ForegroundColor Yellow
    } elseif ($_.Exception.Message -match "502") {
        Write-Host "   ⏳ Space מתחיל (502)" -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ לא זמין: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2. בדיקת Status endpoint
Write-Host "`n2️⃣ בודק Browser Status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$spaceUrl/status" -Method Get -TimeoutSec 10
    Write-Host "   ✅ Browser: $($status.browser)" -ForegroundColor Green
    if ($status.current_url) {
        Write-Host "   📍 URL: $($status.current_url)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⏳ עדיין לא מוכן" -ForegroundColor Yellow
}

# 3. בדיקת VNC
Write-Host "`n3️⃣ בודק VNC Interface..." -ForegroundColor Yellow
try {
    $vnc = Invoke-WebRequest -Uri "$spaceUrl/vnc" -Method Get -TimeoutSec 10 -UseBasicParsing
    if ($vnc.StatusCode -eq 200) {
        Write-Host "   ✅ VNC Interface זמין!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⏳ עדיין לא זמין" -ForegroundColor Yellow
}

# סיכום
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 סיכום:" -ForegroundColor Cyan
Write-Host "   🌐 API: $spaceUrl" -ForegroundColor White
Write-Host "   🖥️ VNC: $spaceUrl/vnc" -ForegroundColor White
Write-Host "   📊 Admin: https://huggingface.co/spaces/kuperberg/browser-embassy" -ForegroundColor White

Write-Host "`n💡 להפעלה מחדש של הבדיקה:" -ForegroundColor Gray
Write-Host "   .\check_status.ps1" -ForegroundColor Gray
