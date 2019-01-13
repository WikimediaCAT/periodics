#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#10	3-7	*	*	* /usr/bin/jsub -N mesllegits -once -quiet /data/project/jorobot/periodics/mesllegits/mesllegits.sh
# O sigui, cada dia, a l'hora i 10, de 3 a 7 del matí
HOMEBOT=/data/project/jorobot/periodics/mesllegits
#HOMEBOT=~/programes/periodics/mesllegits

cd $HOMEBOT

python $HOMEBOT/mesllegits.py
