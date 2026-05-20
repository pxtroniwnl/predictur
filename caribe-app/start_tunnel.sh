#!/bin/bash
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1
/opt/homebrew/bin/cloudflared tunnel --url http://localhost:5173 --no-autoupdate 2>/Users/apple/Desktop/Universidad/Storytelling\ /caribe-app/cf_tunnel.log &
CF_PID=$!
echo $CF_PID > /Users/apple/Desktop/Universidad/Storytelling\ /caribe-app/cf_pid.txt

for i in $(seq 1 25); do
  sleep 1
  URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /Users/apple/Desktop/Universidad/Storytelling\ /caribe-app/cf_tunnel.log 2>/dev/null | head -1)
  if [ -n "$URL" ]; then
    echo "TUNNEL_URL=$URL"
    exit 0
  fi
done
echo "TIMEOUT"
cat /Users/apple/Desktop/Universidad/Storytelling\ /caribe-app/cf_tunnel.log
