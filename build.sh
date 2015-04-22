#!/bin/bash -e

source venv/bin/activate
make test
make zipfile
scp bot.zip 192.168.56.1:~/Downloads/
rm bot.zip
