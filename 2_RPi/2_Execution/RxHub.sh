#/bin/bash

cd ~/Desktop/RF24/examples_linux/
make clean &> /dev/null
make &> /dev/null

cd ~/Desktop
# ./RF24/examples_linux/receiver | python2 ./Hub/Prueba.py
./RF24/examples_linux/receiver | python2 ./Hub/Hub.py
