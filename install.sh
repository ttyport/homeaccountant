#!/bin/bash
sudo pip3 uninstall pyqt5
pip3 install -r requirements.txt
mkdir $HOME/.homeaccountant/
cp db.db $HOME/.homeaccountant/
cp main.py /usr/bin
cd /usr/bin
mv main.py homeaccountant
chmod +x homeaccountant

