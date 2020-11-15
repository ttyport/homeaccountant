#!/bin/bash
sudo pip3 uninstall pyqt5
pip3 install -r requirements.txt
mkdir /usr/share/homeaccountant/
cp db.db /usr/share/homeaccountant/
cp main.py /usr/bin
cd /usr/bin
mv main.py homeaccountant
chmod +x homeaccountant
