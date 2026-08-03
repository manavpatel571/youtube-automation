@echo off
cd /d "d:\youtube\auto_video"
if not exist "output\logs" mkdir "output\logs"
echo Starting 6 PM Music Video Pipeline... >> "output\logs\auto_6pm.log"
date /t >> "output\logs\auto_6pm.log"
time /t >> "output\logs\auto_6pm.log"
"C:\Users\manav\anaconda3\python.exe" main.py music-full >> "output\logs\auto_6pm.log" 2>&1
echo Finished 6 PM Music Video Pipeline. >> "output\logs\auto_6pm.log"
