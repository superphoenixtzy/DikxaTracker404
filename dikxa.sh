#!/data/data/com.termux/files/usr/bin/bash
BASE="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE"

mkdir -p "DikxaTracker" html

clear
echo "======================================"
echo "       DIKXA CYBER TRACKER UPLOAD"
echo "======================================"
echo
echo "[01] Jalankan server"
echo "[02] Lihat folder foto"
echo "[00] Keluar"
echo
read -p "CYBER@TERMUX > " choice

case "$choice" in
  01|1)
    python server.py
    ;;
  02|2)
    ls -lah "DikxaTracker"
    echo
    read -p "Enter untuk kembali..."
    exec "$0"
    ;;
  00|0)
    exit 0
    ;;
  *)
    echo "Menu tidak tersedia."
    sleep 1
    exec "$0"
    ;;
esac
