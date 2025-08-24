# Инструкция по компиляции APK файла для Android

## Проблема с buildozer на Windows

К сожалению, buildozer имеет ограничения при работе на Windows. Для успешной компиляции APK файла рекомендуется использовать один из следующих методов:

## Метод 1: Использование WSL (Windows Subsystem for Linux) - Рекомендуется

### Шаг 1: Установка WSL
```bash
# В PowerShell от имени администратора
wsl --install
```

### Шаг 2: Установка Ubuntu в WSL
```bash
wsl --install -d Ubuntu
```

### Шаг 3: Настройка среды в WSL
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Установка зависимостей для buildozer
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Установка buildozer и kivy
pip3 install buildozer kivy python-for-android cython faker

# Установка Android SDK
sudo apt install android-sdk
```

### Шаг 4: Копирование файлов в WSL
```bash
# Скопируйте main.py и buildozer.spec в WSL
# Например, создайте папку в WSL и скопируйте файлы
mkdir ~/phonebook_generator
cd ~/phonebook_generator

# Скопируйте файлы из Windows в WSL
cp /mnt/f/Блог/Проекты\ HTML/Python/Генератор\ номеров/main.py .
cp /mnt/f/Блог/Проекты\ HTML/Python/Генератор\ номеров/buildozer.spec .
```

### Шаг 5: Сборка APK в WSL
```bash
# В папке с проектом
buildozer android debug
```

## Метод 2: Использование Docker

### Создание Dockerfile
```dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip git zip unzip openjdk-8-jdk \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

RUN pip3 install buildozer kivy python-for-android cython faker

WORKDIR /app
COPY . .

RUN buildozer android debug
```

### Сборка в Docker
```bash
# Создание образа
docker build -t phonebook-generator .

# Извлечение APK файла
docker run --rm -v $(pwd):/output phonebook-generator cp bin/*.apk /output/
```

## Метод 3: Использование онлайн-сервисов

1. **GitHub Actions** - Создание CI/CD пайплайна для автоматической сборки
2. **Colab** - Использование Google Colab для сборки
3. **Replit** - Онлайн IDE с поддержкой buildozer

## Метод 4: Альтернативные инструменты

### BeeWare (Briefcase)
```bash
pip install briefcase
briefcase new
briefcase dev
briefcase build android
briefcase package android
```

### Kivy Garden (только для тестирования)
```bash
pip install kivy-garden
garden install graph
```

## Готовые файлы в проекте

1. **main.py** - Приложение, переписанное с tkinter на Kivy
2. **buildozer.spec** - Конфигурация для сборки APK
3. **Generator.py** - Оригинальное приложение на tkinter

## Альтернативное решение: Веб-приложение

Если сборка APK окажется слишком сложной, можно создать веб-версию приложения:

```python
# Создание веб-приложения с Flask
pip install flask
```

## Заключение

Для Windows пользователей наиболее простым решением будет:
1. Использование WSL с Ubuntu
2. Или загрузка готового APK с GitHub Actions

APK файл будет создан в папке `bin/` после успешной сборки.

## Размер итогового APK
Ожидаемый размер: 15-25 МБ

## Совместимость
- Android 5.0+ (API 21+)
- Поддержка ARM и x86 архитектур