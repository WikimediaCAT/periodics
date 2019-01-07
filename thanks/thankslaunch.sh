#!/bin/sh
PATH=/bin:/usr/bin
HOMEBOT=/home/bot/programes/subst
export PYTHONPATH=:/home/bot/.pywikibot_master/core

ultimany=`cat $HOMEBOT/thanksbot.dat | cut -c1-4`
ultimmes=`cat $HOMEBOT/thanksbot.dat | cut -c5-7`

anyactual=`date +"%Y"`
mesactual=`date +"%m"`

if [ X$ultimmes = "X12" ]
then noumes=01
     nouany=`echo "$ultimany" | awk '{out=$0+1;printf out}'`
else noumes=`echo "$ultimmes" | awk '{out=$0+1;printf "%02d",out}'`
     nouany=$ultimany
fi

if [ X$anyactual = "X$nouany" ]
then if [ X$mesactual = "X$noumes" ]
then return		# ja l'hem fet, no hi tornem
fi
fi

python $HOMEBOT/thanks.py $nouany $noumes
echo $nouany$noumes > $HOMEBOT/thanksbot.dat  # posem la data de l'últim mes fet
