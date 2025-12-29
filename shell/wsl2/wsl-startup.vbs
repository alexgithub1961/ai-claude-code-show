' wsl-startup.vbs - Silent launcher for WSL2 services at Windows startup
'
' IMPORTANT: This script is only needed if NOT using Tailscale.
' With Tailscale, services start automatically.
'
' This VBScript runs PowerShell scripts silently (no window popup).
' Use with Windows Task Scheduler to run at login.
'
' Task Scheduler Setup:
'   1. Open Task Scheduler (taskschd.msc)
'   2. Create Basic Task > "WSL2 Startup"
'   3. Trigger: "When I log on"
'   4. Action: "Start a program"
'   5. Program: wscript.exe
'   6. Arguments: "C:\path\to\wsl-startup.vbs"
'   7. Check "Run with highest privileges"
'

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script lives
scriptPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

' Wait for WSL2 to be ready
WScript.Sleep 5000

' Start WSL2 and run the start-services script
' This ensures SSH and Tailscale are running
WshShell.Run "wsl.exe -e bash -c 'cd " & Replace(scriptPath, "\", "/") & " && ./start-services.sh --quiet'", 0, True

' Run port forwarding (requires elevation, so we use PowerShell)
' Note: This will prompt for admin if not already elevated
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & scriptPath & "port-forward.ps1""", 0, True

Set WshShell = Nothing
