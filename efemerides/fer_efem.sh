#!/bin/sh

PATHVENV=/data/project/jorobot/periodics/efemerides/pyvenv_pel_batch

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#0	15	*	*	3 /usr/bin/jsub -N fer_efem -once -quiet /data/project/jorobot/periodics/efemerides/fer_efem.sh
# O sigui, el dia 3 de la setmana (dimecres) a les 3 de la tarda

# Un cop migrat a Kubernetes, s'engega un cop amb
# toolforge-jobs run fer-efem --command "periodics/efemerides/fer_efem.sh" --image tf-python39 --schedule "0 15 * * 3"

# i es treu del crontab

HOMEBOT=~/periodics/efemerides
#HOMEBOT=~/programes/periodics/efemerides
# Aquesta variable té els dies d'antelació amb què creem les plantilles
ANTELACIO=14

# Posem la data d'inici del treball, d'aquí $ANTELACIO dies
dia=`date +'%d' -d "+$ANTELACIO days"`
mes=`date +'%m' -d "+$ANTELACIO days"`
any=`date +'%Y' -d "+$ANTELACIO days"`

cd $HOMEBOT
# Creem 7 dies seguits i ho gravem
./pyvenv_pel_batch/bin/python3 $HOMEBOT/dates_rodones.py $any $mes $dia 7 1
