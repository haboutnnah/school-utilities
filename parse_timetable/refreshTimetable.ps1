[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
If (Test-Path config.txt){
    $Url = Get-Content config.txt | Select-Object -First 1
    $SleepTime = Get-Content config.txt | Select-Object -First 1 -Skip 1
    $SleepTime = $SleepTime -as [int]
    $IFTTTBaseURI = Get-Content config.txt | Select-Object -First 1 -Skip 2
    $IFTTTAPIKey = Get-Content config.txt | Select-Object -First 1 -Skip 3
}
Else {
    $Url = Read-Host -Prompt "Input your timetable url (Preferably the cyclical one.)"
    $SleepTime = Read-Host -Prompt "How long between refreshes?"
    $IFTTTBaseURI = Read-Host -Prompt "IFTTT Base URI"
    $IFTTTAPIKey = Read-Host -Prompt "IFTTT API key"
    Write-Output $Url | Out-File -FilePath config.txt
    Write-Output$SleepTime | Out-File -FilePath config.txt -Append
    Write-Output$IFTTTBaseURI | Out-File -FilePath config.txt -Append
    Write-Output $IFTTTAPIKey | Out-File -FilePath config.txt -Append
}


$IconExists = Test-Path icon.ico
If (-Not $IconExists){
    Invoke-WebRequest -Uri "http://paulferrett.com/fontawesome-favicon/generate.php?icon=refresh&fg=00bcd4" -OutFile icon.ico
}



While($true){
    $WebsiteContent = Invoke-WebRequest -Uri $Url -UserAgent "Script to refresh timetable page until change is found [https://gist.github.com/tf2manu994/57ddb19d6c7549f7d3881b76aea6a3b0] <contact@hannahi.com>"
    $WebsiteContent.ParsedHtml.body | Select-Object -ExpandProperty innerHTML | Out-File -FilePath current-site.html
    $WebsiteHash = Get-FileHash current-site.html -Algorithm MD5
    $WebsiteHash = $WebsiteHash.Hash
    Write-Host "Debug: Current website hash is " -NoNewline -ForegroundColor Cyan
    Write-Host $WebsiteHash -ForegroundColor Yellow
    Rename-Item current-site.html "${WebsiteHash}.html" -ErrorAction SilentlyContinue -ErrorVariable RenameError
    If ($RenameError) {
        Write-Host "This hash has been previously found, it is certain that the timtables have not been updated." -ForegroundColor Cyan
    }
    Else {
        Write-Host "Change detected." -ForegroundColor Green
        Write-Host "Sending SMS" -ForegroundColor Cyan 
        Invoke-WebRequest -Uri "${IFTTTBaseURI}/${IFTTTAPIKey}?value1=${Url}&value2=${SleepTime}" | Out-File -FilePath "smsConfig"
        Write-Host "Firing notification." -ForegroundColor Cyan
        $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon 
        $workingdir = (Get-Item -Path ".\" -Verbose).FullName
        $objNotifyIcon.Icon =  "$workingdir\icon.ico"
        $objNotifyIcon.BalloonTipIcon = "Info" 
        $objNotifyIcon.BalloonTipText = "The timetable has updated." 
        $objNotifyIcon.BalloonTipTitle = "Timetable Update" 
        $objNotifyIcon.Visible = $True 
        $objNotifyIcon.ShowBalloonTip(10000)
        exit
    }
    Write-Host "Checking again in ${SleepTime} seconds." -ForegroundColor Cyan
    Remove-Item current-site.html -ErrorAction SilentlyContinue
    Start-Sleep $SleepTime
    }
