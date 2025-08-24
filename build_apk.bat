@echo off
chcp 65001 >nul
echo ================================================
echo    Генератор телефонной книги - Сборка APK
echo ================================================
echo.

echo Проверка наличия WSL...
wsl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WSL не установлен.
    echo.
    echo Для установки WSL выполните следующие команды в PowerShell от имени администратора:
    echo.
    echo   wsl --install
    echo   wsl --install -d Ubuntu
    echo.
    echo После установки перезагрузите компьютер и запустите этот скрипт снова.
    pause
    exit /b 1
)

echo WSL найден!
echo.

echo Проверка наличия Ubuntu в WSL...
wsl -l | findstr Ubuntu >nul
if %errorlevel% neq 0 (
    echo Ubuntu не найден в WSL.
    echo Установка Ubuntu...
    wsl --install -d Ubuntu
    echo.
    echo После завершения установки Ubuntu запустите этот скрипт снова.
    pause
    exit /b 1
)

echo Ubuntu найден!
echo.

echo Создание рабочей директории в WSL...
wsl mkdir -p ~/phonebook_generator

echo Копирование файлов в WSL...
wsl cp "/mnt/f/Блог/Проекты HTML/Python/Генератор номеров/main.py" ~/phonebook_generator/
wsl cp "/mnt/f/Блог/Проекты HTML/Python/Генератор номеров/buildozer.spec" ~/phonebook_generator/

echo Установка зависимостей в WSL...
wsl bash -c "cd ~/phonebook_generator && sudo apt update && sudo apt install -y python3 python3-pip python3-venv git zip unzip openjdk-8-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev"

echo Установка Python пакетов...
wsl bash -c "cd ~/phonebook_generator && pip3 install buildozer kivy python-for-android cython faker"

echo.
echo ================================================
echo Начинаем сборку APK файла...
echo Это может занять 30-60 минут при первой сборке.
echo ================================================
echo.

wsl bash -c "cd ~/phonebook_generator && buildozer android debug"

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo Сборка завершена успешно!
    echo ================================================
    echo.
    echo APK файл создан в WSL. Копирование на Windows...
    
    if not exist "bin" mkdir bin
    wsl cp ~/phonebook_generator/bin/*.apk "/mnt/f/Блог/Проекты HTML/Python/Генератор номеров/bin/"
    
    echo.
    echo APK файл скопирован в папку 'bin'
    echo Вы можете найти его по пути:
    echo %cd%\bin\
    echo.
    echo Для установки на Android:
    echo 1. Скопируйте APK файл на устройство
    echo 2. Разрешите установку из неизвестных источников
    echo 3. Установите приложение
    echo.
) else (
    echo.
    echo ================================================
    echo Ошибка при сборке APK!
    echo ================================================
    echo.
    echo Проверьте вывод выше для получения подробностей об ошибке.
    echo.
    echo Для получения помощи обратитесь к файлу README_APK_Build.md
    echo.
)

pause