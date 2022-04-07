#!/bin/sh
PATH=/bin:/usr/bin

PATHVENV=/data/project/jorobot/periodics/efemerides/pyvenv_pel_batch

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#0	20	7	*	* /usr/bin/jsub -N gensub -once -quiet /data/project/jorobot/periodics/efemerides/gensub.sh
# O sigui, el dia 7 de cada mes, a les 8 del vespre, hora de toolforge
# Tots els mesos, i qualsevol dia de la setmana.

# Un cop migrat a Kubernetes, s'engega un cop amb
# toolforge-jobs run fer-efem --command "periodics/efemerides/gensub.sh" --image tf-python39 --schedule "0 20 7 * *"

HOMEBOT=~/periodics/efemerides

# si no existeix el directori, el creem, però això només hauria de ser la
# primera vegada de totes
cd $HOMEBOT
if [ ! -d bd ]
   then mkdir bd
fi

if [ $# -eq 1 ]
then antelacio=$1
else antelacio=1
fi

# per defecte, si s'executa un mes, volem que generi el mes següent.
# date -d "+1 month" et dóna la data d'avui més 1 mes
# el +'%m' és perquè només t'ensenyi el mes, en 2 dígits
# Podem passar-hi un paràmetre per fer altres mesos manualment
# per exemple: ./gensub.sh 2
mesqueve=`date +'%m' -d "+$antelacio month"`

./pyvenv_pel_batch/bin/python3 ./efemerides.py $mesqueve

./comprovarbd.sh $mesqueve
