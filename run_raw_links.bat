@echo off
echo GitHub Raw Links Generator Calistiriliyor...
python github_raw_links.py tuguss11-source prototype0 --branch main --exclude-py-cache > raw_links.txt
echo Islem tamamlandı! Sonuclar raw_links.txt dosyasina kaydedildi.
pause