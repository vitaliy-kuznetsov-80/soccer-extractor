pyinstaller main.py --onefile
pyinstaller main_results.py --onefile
rmdir /s /q build
xcopy "assets" "dist\assets" /s /e /i
mkdir "dist\config"
copy "config\appsettings.json" "dist\config"