#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#10	0	*	*	* /usr/bin/jsub -N redir -once -quiet /data/project/jorobot/periodics/mesllegits/redir_mesllegits.sh
# O sigui, cada dia, a les 00:10, (en realitat, 01:10, que el toolserver va
# a hora UTC)

HOMEBOT=/data/project/jorobot/periodics/mesllegits
#HOMEBOT=~/programes/periodics/mesllegits

PYTHONPATH=/data/project/shared/pywikipedia/core

cd $HOMEBOT

python3 $HOMEBOT/redir_mesllegits.py
