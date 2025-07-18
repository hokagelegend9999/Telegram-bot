#!/bin/bash
TRIAL_LOG_FILE="/etc/hokage-bot/trial_users.log"
CONFIG_FILE="/etc/xray/config.json"

if [ ! -f "$TRIAL_LOG_FILE" ]; then exit 0; fi
CURRENT_TIME=$(date +%s)
TMP_LOG_FILE="${TRIAL_LOG_FILE}.tmp"; > "$TMP_LOG_FILE"
config_changed=0

while IFS= read -r line; do
    EXP_TIME=$(echo "$line" | cut -d: -f1)
    USERNAME=$(echo "$line" | cut -d: -f2)
    ACC_TYPE=$(echo "$line" | cut -d: -f3)

    if [ "$CURRENT_TIME" -gt "$EXP_TIME" ]; then
        config_changed=1
        if [ "$ACC_TYPE" = "ssh" ]; then
            userdel -r "$USERNAME"
            sed -i "/^### $USERNAME /d" /etc/xray/ssh
        elif [ "$ACC_TYPE" = "vmess" ] || [ "$ACC_TYPE" = "vless" ] || [ "$ACC_TYPE" = "trojan" ]; then
            sed -i "/\"email\": \"$USERNAME\"/d" "$CONFIG_FILE"
            sed -i "/\#vm $USERNAME /d" "$CONFIG_FILE"
            sed -i "/\#vmg $USERNAME /d" "$CONFIG_FILE"
            sed -i "/\#vl $USERNAME /d" "$CONFIG_FILE"
            sed -i "/\#vlg $USERNAME /d" "$CONFIG_FILE"
            sed -i "/\#tr $USERNAME /d" "$CONFIG_FILE"
            sed -i "/\#trg $USERNAME /d" "$CONFIG_FILE"
        fi
    else
        echo "$line" >> "$TMP_LOG_FILE"
    fi
done < "$TRIAL_LOG_FILE"
mv "$TMP_LOG_FILE" "$TRIAL_LOG_FILE"
if [ "$config_changed" -eq 1 ]; then
    systemctl restart xray > /dev/null 2>&1
fi
