c:\Projects\soccer-extractor\.venv\Scripts\pyinstaller.exe run_america.py --onefile
c:\Projects\soccer-extractor\.venv\Scripts\pyinstaller.exe run_asia.py --onefile
c:\Projects\soccer-extractor\.venv\Scripts\pyinstaller.exe run_europe.py --onefile
c:\Projects\soccer-extractor\.venv\Scripts\pyinstaller.exe run_results.py --onefile
c:\Projects\soccer-extractor\.venv\Scripts\pyinstaller.exe run_scheduler.py --onefile
c:\Projects\soccer-extractor\.venv\Scripts\pyinstaller.exe run_scheduler_test.py --onefile

rmdir /s /q build
xcopy "assets" "dist\assets" /s /e /i
mkdir "dist\config"
copy "config\appsettings.json" "dist\config"
mkdir "dist\results"

set /p Version=<version
tar -a -c -f release_%Version%.zip dist

rmdir /s /q dist