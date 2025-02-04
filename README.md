# Руководство по установке

## Шаг 1: Создание и активация Virtual Environment
Перед установкой зависимостей создайте и активируйте Virtual Environment:

```bash
python -m venv venv
source venv/bin/activate
```

## Шаг 2: Установка зависимостей
Установите необходимые пакеты Python с помощью:

```bash
pip install -r requirements.txt
```

## Шаг 3: Настройка sudoers для скриптов
Чтобы `monitor.sh` и `wifi.sh` запускались без запроса пароля, отредактируйте файл sudoers:

```bash
sudo visudo
```

Добавьте в конец файла следующие строки, заменив `username` на ваше имя пользователя:

```bash
username ALL=(ALL) NOPASSWD: /path/to/monitor.sh
username ALL=(ALL) NOPASSWD: /path/to/wifi.sh
```

## Шаг 4: Запуск сервера
Запустите сервер с помощью:

```bash
python server.py
```

Теперь все готово!