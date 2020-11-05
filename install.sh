#!/bin/bash
pip3 install -r requirements.txt
cp db.db ~/.local/bin
cp main.py ~/.local/bin
cd ~/.local/bin
mv main.py homeaccountant
chmod +x homeaccountant

