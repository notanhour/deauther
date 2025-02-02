#!/usr/bin/bash

if [ "$(id -u)" -ne 0 ]; then
	echo "Этот скрипт требует прав суперпользователя (sudo)."
	exit 1
fi

if [ -z "$1" ]; then
	echo "Использование: $0 <start|stop> <interface>"
	exit 1
fi

INTERFACE=wlp2s0

if [ "$1" == "start" ]; then
	echo "Проверка на наличие процессов мешающих работе в monitor mode..."
	sudo airmon-ng check kill > /dev/null 2>&1
	echo "Переключение интерфейса $INTERFACE в monitor mode..."
	sudo airmon-ng start $INTERFACE > /dev/null 2>&1
	echo "Интерфейс ${INTERFACE}mon теперь работает в monitor mode."
elif [ "$1" == "stop" ]; then
	echo "Переключение интерфейса ${INTERFACE}mon в managed mode..."
	sudo airmon-ng stop ${INTERFACE}mon > /dev/null 2>&1
	echo "Интерфейс $INTERFACE теперь работает в managed mode."
	echo "Перезапуск NetworkManager..."
	sudo systemctl restart NetworkManager > /dev/null 2>&1
else
	echo "Неверный параметр. Использование: $0 <start|stop> <interface>"
	exit 1
fi
