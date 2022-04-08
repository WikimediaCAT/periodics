#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#10	0	*	*	* /usr/bin/jsub -N redir -once -quiet /data/project/jorobot/periodics/mesllegits/redir_mesllegits.sh
# O sigui, cada dia, a les 00:10, (en realitat, 01:10, que el toolserver va
# a hora UTC)

# Amb Kubernetes, s'engega un cop amb
# toolforge-jobs run redir --command "periodics/mesllegits/redir_mesllegits.sh" --image tf-python39 --schedule "10 0 * * *"

HOMEBOT=~/periodics/mesllegits
#HOMEBOT=~/programes/periodics/mesllegits
PYVENV=~/periodics/efemerides/pyvenv_pel_batch

cd $HOMEBOT

$PYVENV/bin/python3 $HOMEBOT/redir_mesllegits.py
