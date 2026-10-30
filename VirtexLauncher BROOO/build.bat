@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/4] Проверка Python...
python --version || (echo Python не установлен! Скачай с python.org & pause & exit /b 1)

echo [2/4] Установка зависимостей...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo [3/4] Сборка .exe...
pyinstaller --noconfirm --clean build.spec

echo [4/4] Копирование файлов рядом с exe...
if exist VirtexVisuals.exe copy /Y VirtexVisuals.exe dist\ >nul
if exist VirtexVisuals.dll copy /Y VirtexVisuals.dll dist\ >nul
if exist injector.exe copy /Y injector.exe dist\ >nul

echo.
echo ========================================
echo  ГОТОВО! Твой exe здесь:
echo  dist\VirtexLauncher.exe
echo ========================================
pause