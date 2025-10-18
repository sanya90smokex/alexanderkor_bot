#!/usr/bin/env bash
set -e
echo "Запуск start.sh"
echo "Текущая директория:"; pwd
echo "Файлы:"; ls -la

python -u server.py &
python -u bot.py
