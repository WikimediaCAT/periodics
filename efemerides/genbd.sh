#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#0	20	14	*	* /usr/bin/jsub -N gensub -once -quiet /data/project/jorobot/periodics/efemerides/gensub.sh
# O sigui, el dia 14 de cada mes, a les 8 del vespre
# Tots els mesos, i qualsevol dia de la setmana.
HOMEBOT=/data/project/jorobot/periodics/efemerides

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

python3 ./efemerides.py $mesqueve

./comprovarbd.sh $mesqueve
