#!/bin/sh
PATH=/bin:/usr/bin

# Això des de casa
#HOMEBOT=/home/bot/programes/subst
#export PYTHONPATH=:/home/bot/.pywikibot_master/core
# Això des de toolforge
HOMEBOT=/data/project/jorobot/periodics/thanks

# Aquest shell script està pensat per passar-lo en qualsevol moment del mes
# i possiblement unes quantes vegades. Només té efecte la primera vegada que
# es passa. Les subsegüents, no fa res.

# Llegim el fitxer que diu l'últim mes per al qual s'han creat estadístiques
# el format és aaaamm
ultimany=`cat $HOMEBOT/thanksbot.dat | cut -c1-4`
ultimmes=`cat $HOMEBOT/thanksbot.dat | cut -c5-7`

# Mirem en quin any i mes som
anyactual=`date +"%Y"`
mesactual=`date +"%m"`

# mirem quin tocaria fer segons el que hem llegit a thanksbot.dat
# tenim en compte que després del desembre canvia l'any
if [ X$ultimmes = "X12" ]
then noumes=01
     nouany=`echo "$ultimany" | awk '{out=$0+1;printf out}'`
else noumes=`echo "$ultimmes" | awk '{out=$0+1;printf "%02d",out}'`
     nouany=$ultimany
fi

# aquí mirem si el mes que estem ja està fet. En aquest cas, pleguem
if [ X$anyactual = "X$nouany" ]
then if [ X$mesactual = "X$noumes" ]
then return		# ja l'hem fet, no hi tornem
fi
fi

# si arribem aquí, és que s'ha d'executar
# thanks.py agafa com a paràmetres l'any i mes del que vols fer estadístiques
python $HOMEBOT/thanks.py $nouany $noumes
echo $nouany$noumes > $HOMEBOT/thanksbot.dat  # posem la data de l'últim mes fet
