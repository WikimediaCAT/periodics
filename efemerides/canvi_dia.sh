#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#1	23	*	*	* /usr/bin/jsub -N canvi_dia -once -quiet /data/project/jorobot/periodics/efemerides/canvi_dia.sh
# O sigui, cada dia de cada mes, a les 23:01 del vespre. Cal tenir en compte
# que això és hora de toolforge, que va una hora o dues abans, o sigui que
# en realitat s'executa a mitjanit més un minut, o la una i 1, per evitar el
# pic de la mitjanit.

# Un cop migrat a Kubernetes, s'engega un cop amb
# toolforge-jobs run canvi-dia --command "periodics/efemerides/canvi_dia.sh" --image tf-python39 --schedule "1 23 * * *"
# requereix instal·lar el mòdul "setup" al pyvenv


HOMEBOT=~/periodics/efemerides
#PWBDIR=/data/project/shared/pywikipedia/core
PYVENV=$HOMEBOT/pyvenv_pel_batch
PWBDIR=$PYVENV/lib/python3\.9/site-packages/pywikibot/scripts

#echo $PWBDIR

$PYVENV/bin/python3 $PWBDIR/pwb.py touch -page:Plantilla:Portada600k/efemèrides
#python3 $PWBDIR/pwb.py touch -page:Plantilla:Portada600k
#$PYVENV/bin/python3 $PWBDIR/pwb.py touch -page:Plantilla:Portada600k
