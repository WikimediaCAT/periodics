** Com es gestiona la portada **

*genbd.sh* - shell script que crida efemerides.py. Sense paràmetres, fa el
mes següent al que estem. La intenció és cridar-lo des del crontab perquè
cada mes es posi a l'última versió, incorporant el que hagin posat els
viquipedistes en el darrer any. Se li pot donar un paràmetre que és quants
mesos ha de saltar per crear la base de dades.

*comprovarbd.sh* - shell script que comprova si tots els dies del mes tenen
algun naixement, esdeveniment i defunció. Si no, és que alguna cosa ha anat
malament.

*efemerides.py* - crea, al directori bd, uns fitxers plans que
són la base de dades per buscar efemèrides. Es crea un fitxer per cada mes,
i el format és senzill, de fitxer pla, que diu la data, un codi (N,D,E) per
indicar si és naixement, defunció o esdeveniment, i una explicació de què és.

*fer_efem.sh* - shell script que crida dates_rodones.py. Està pensat per
llançar-se des del crontab i executar-se un cop per setmana (de moment,
dimecres). Llavors, el que fa és saltar 15 dies i generar les plantilles d'una
setmana seguida. Això dóna marge perquè algun humà les adapti i formategi

*dates_rodones.py* - script Python que llegeix les bases de dades creades per
efemerides.py, i genera una plantilla que, convenientment modificada, pot
utilitzar la portada per mostrar efemerides.
