#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#10	1-6	*	*	* /usr/bin/jsub -N mesllegits -once -quiet /data/project/jorobot/periodics/mesllegits/mesllegits.sh
# O sigui, cada dia, a l'hora i 10, de 1 a 6 del matí (en realitat, de 2 a 7
# que el toolserver va a hora UTC)
HOMEBOT=/data/project/jorobot/periodics/mesllegits
#HOMEBOT=~/programes/periodics/mesllegits

PYTHONPATH=/data/project/shared/pywikipedia/core

cd $HOMEBOT

python3 $HOMEBOT/mesllegits.py
