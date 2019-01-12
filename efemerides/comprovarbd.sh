#!/bin/sh
# comprovarbd.sh - comprova que a la base de dades d'un mes concret hi hagi
#                  esdeveniments, naixements i defuncions a tots els dies
#
PATH=/bin:/usr/bin
#HOME=/data/project/jorobot/periodics/efemerides
HOME=~/programes/periodics/efemerides
BD=$HOME/bd

# Llegim un paràmetre del mes que s'ha de processar. Si no ens el passen,
# agafem el mes que ve.
if [ $# -eq 1 ]
then mes=`printf "%02d" $1`		# posa zero a l'esquerra si cal
else mes=`date +'%m' -d "+1 month"`
fi

# Fem un bucle mirant tots els dies. Per saber si el mes té 28, 29, 30 o 31
# dies, utilitzem "date" per anar sumant un dia.
# Quan detectem que hem canviat de mes, parem
#
any_mirem=2020		# perquè és de traspàs, i així té 29 de febrer
#
# l'any, en realitat, no el fem servir per buscar res. Serviria qualsevol any
# de traspàs
# inicialitzem al primer del mes
# el format %F fa 2020-01-01
ind_data=`date +'%F' -d "$any_mirem/$mes/01"`
while /bin/true			# només sortirem per un break
do
  # El dia el traiem a partir de la data
  dia=`date +'%d' -d $ind_data`
  # Passem a buscar als fitxers
  naix=`grep -c -E "^[0-9]+,$mes,$dia,N" $BD/efemerides_$mes.txt`
  if [ $naix -eq 0 ]
  then echo "No hi ha naixements el dia $dia del mes $mes"
  fi
  esde=`grep -c -E "^[0-9]+,$mes,$dia,E" $BD/efemerides_$mes.txt`
  if [ $esde -eq 0 ]
  then echo "No hi ha esdeveniments el dia $dia del mes $mes"
  fi
  defu=`grep -c -E "^[0-9]+,$mes,$dia,D" $BD/efemerides_$mes.txt`
  if [ $defu -eq 0 ]
  then echo "No hi ha defuncions el dia $dia del mes $mes"
  fi
  # sumem un dia
  ind_data=`date +'%F' -d "$ind_data+1 day"`
  # mirem de quin mes és l'endemà
  mes_nou=`date +'%m' -d $ind_data`
  # si hem canviat de mes, pleguem
  if [ $mes_nou != $mes ]
  then break
  fi
done
