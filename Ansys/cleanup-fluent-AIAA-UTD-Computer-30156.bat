echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\v252\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\v252\fluent\ntbin\win64\tell.exe" AIAA-UTD-Computer 64080 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\v252\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="AIAA-UTD-Computer" (%KILL_CMD% 33408) 
if /i "%LOCALHOST%"=="AIAA-UTD-Computer" (%KILL_CMD% 40388) 
if /i "%LOCALHOST%"=="AIAA-UTD-Computer" (%KILL_CMD% 30156) 
if /i "%LOCALHOST%"=="AIAA-UTD-Computer" (%KILL_CMD% 41716)
del "C:\Users\AIAA UT Dallas\Documents\Comet Rocketry Sims\CometRocketryRocketpySims\cleanup-fluent-AIAA-UTD-Computer-30156.bat"
