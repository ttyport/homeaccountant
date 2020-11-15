#!/bin/bash
sudo pip3 uninstall pyqt5
pip3 install -r requirements.txt
mkdir $HOME/.homeaccountant/
cp db.db $HOME/.homeaccountant/
sudo cp main.py /usr/bin
cd /usr/bin
sudo mv main.py homeaccountant
sudo chmod +x homeaccountant

