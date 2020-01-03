#!/bin/sh
PATH=/bin:/usr/bin

# Des de toolforge
# S'engega per crontab amb una línia com aquesta (però sense el comentari)
#1	23	*	*	* /usr/bin/jsub -N gensub -once -quiet /data/project/jorobot/periodics/efemerides/canvi_dia.sh
# O sigui, cada dia de cada mes, a les 23:01 del vespre. Cal tenir en compte
# que això és hora de toolforge, que va una hora abans, o sigui que en realita
# s'executa a mitjanit més un minut, per evitar el pic de la mitjanit.

HOMEBOT=/data/project/jorobot/periodics/efemerides
PWBDIR=/shared/pywikipedia/core/scripts

python3 $PWBDIR/pwb.py touch -page:Plantilla:Portada600k/efemèrides
python3 $PWBDIR/pwb.py touch -page:Plantilla:Portada600k
