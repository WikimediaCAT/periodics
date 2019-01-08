#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#0	20	20	*	* /usr/bin/jsub -N gensub -once -quiet /data/project/jorobot/periodics/efemerides/gensub.sh
# O sigui, el dia 20 de cada mes, a les 8 del vespre
# Tots els mesos, i qualsevol dia de la setmana.
HOMEBOT=/data/project/jorobot/periodics/efemerides

# si no existeix el directori, el creem, però això només hauria de ser la
# primera vegada de totes
cd $HOMEBOT
if [ ! -d bd ]
   then mkdir bd
fi

# si s'executa el 20, i li sumem 20 dies més, segur que caiem al mes
# següent. date -d "+20 days" et dóna la data d'avui més 20 dies
# el +'%m' és perquè només t'ensenyi el mes, en 2 dígits
mesqueve=`date +'%m' -d "+20 days"`

python ./efemerides.py $mesqueve
