@echo off
cd /d "d:\youtube\auto_video"
if not exist "output\logs" mkdir "output\logs"
echo Starting 9 AM Video Pipeline... >> "output\logs\auto_9am.log"
date /t >> "output\logs\auto_9am.log"
time /t >> "output\logs\auto_9am.log"
"C:\Users\manav\anaconda3\python.exe" main.py full >> "output\logs\auto_9am.log" 2>&1
echo Finished 9 AM Video Pipeline. >> "output\logs\auto_9am.log"
