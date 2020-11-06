#!/bin/bash
pip3 install -r requirements.txt
mkdir ~/.local/share/homeaccountant/
cp db.db ~/.local/share/homeaccountant/
cp main.py ~/.local/bin
cd ~/.local/bin
mv main.py homeaccountant
chmod +x homeaccountant

