# -*- coding: utf-8 -*-

import pywikibot 
import re
import sys
# realment no calen aquests dos imports, eren proves
from pywikibot.version import getversion
from pywikibot.login import LoginManager
 
# aquesta funció tampoc no cal, perquè no s'executa interactivament
def preguntar():
  while 1:
   sys.stdout.write("Canviar? (s/n/t) ")
   a=sys.stdin.readline()
   a=a.rstrip()
   if a=='t':
       return 0
   if a=='s':
       return 1
   if a=='n':
       return -1

# I de fet tampoc no fem cerques, o sigui que també sobra
def get_search(searchstr):
    params = {
        'action'         :'query',
        'list'           :'search',
        'srsearch'       :searchstr,
        'srwhat'         :'text',
	'srlimit'        : 300
        }
    #sr=pywikibot.data.api.Request(**params).submit()
    print "Cerca "+searchstr
    sr=pywikibot.data.api.Request(**params).submit()
    return sr

# tres funcions auxiliars, prou evidents
# dóna el nom en català del mes
def mescatala(mes):
  nomsmesos = ['gener', 'febrer', u'març', 'abril', 'maig', 'juny', 'juliol', 'agost', 'setembre', 'octubre', 'novembre', 'desembre']
  return nomsmesos[mes-1]

# donada una tupla mes,any, retorna una altra tupla amb el mes anterior
def prevmes(mes,any):
    if mes > 1:
       return (mes-1,any)
    else:
       return (12,any-1)

# donada una tupla mes,any, retorna una altra tupla amb el mes posterior
def nextmes(mes,any):
    if mes < 12:
       return (mes+1,any)
    else:
       return (1,any+1)

def main():
  #print sys.version
  #print getversion()

  # Llegim paràmetres
  if len(sys.argv) != 3:
      print u"Ús: python thanks.py <any> <mes>".encode("utf-8")
      return
  mes = int(sys.argv[2])
  anyllegit = int(sys.argv[1])
  if mes < 1 or mes > 12:
     print u"Mes incorrecte ",mes
     return
  if any < 2015:
     print u"Any incorrecte ",any
     return

  messtr= sys.argv[2].strip()
  # afegim un zero a l'esquerra del mes
  if len(messtr)<2:
      messtr="0"+messtr
  anystr = sys.argv[1].strip()

  # Mirem mesos anterior i posterior, i els passem a string
  (messeg, anyseg) = nextmes(mes,anyllegit)
  messegstr = "%02d" % messeg
  anysegstr = "%d" % anyseg
  
  (mesprev, anyprev) = prevmes(mes,anyllegit)
  mesprevstr = "%02d" % mesprev
  anyprevstr = "%d" % anyprev

  # accedim a viquipèdia per llegir el registre d'agraïments
  # construïm end i start a partir de les variables anteriors
  casite = pywikibot.Site('ca')
  registre = casite.logevents(logtype="thanks",
                              end   =  anystr+"-"+messtr+"-01T00:00:00",
                              start =  anysegstr+"-"+messegstr+"-01T00:00:00",
                              #total=10,
                              )
  # creem els conjunts de gent que rep agraïments, i el que els fa
  # de moment, buits
  agraciats={}
  graciadors={} 

  if registre != None:      # si hem llegit alguna cosa del registre
     for l in registre:     # l'anem llegint registre per registre
       # el paràmetre page() ens diu qui ha rebut l'agraïment, per tant
       # en sumem 1.
       # la primera vegada que aparegui un usuari determinat, donarà error
       # llavors (dins l'except), aprofitem per inicialitzar-lo a 1
       try:
         agraciats[l.page()]=agraciats[l.page()]+1
       except KeyError:
         agraciats[l.page()]=1
       # el paràmetre user() ens diu qui ha fet l'agraïment, per tant
       # fem el mateix procés que abans, però per als que agraeixen
       try:
         graciadors[l.user()]=graciadors[l.user()]+1
       except KeyError:
         graciadors[l.user()]=1

  # Ara ja tenim les dades, només cal crear la pàgina corresponent i
  # formatejar-la amb una mica de gràcia.
  # Primer, la navegació a mes anterior i mes següent
  txtout = u"<center>[[Usuari:JoRobot/Agraïments/"+anyprevstr+"/"+mesprevstr+u"|Mes anterior]] {{·}} '''Historial''' {{·}} [[Usuari:JoRobot/Agraïments/"+anysegstr+"/"+messegstr+u"|Mes següent]]</center>\n"
  # Ara centrem les taules
  txtout = txtout + u"<div align=\"center\">\n{{Columnes|66%}}\n"
  # Posem capçaleres de les taules
  txtout = txtout + u"{| class=\"wikitable sortable\"\n|+ Agraïments rebuts per usuari durant el mes de "+mescatala(mes)+" de "+anystr+"\n"
  txtout = txtout+u"|-\n! scope=\"col\" | Usuari\n! scope=\"col\" | Agraïments\n"

  # Aquest bucle és per cada fila. Primer els que reben agraïments
  # No ho posem en cap ordre especial, tal com raja del conjunt que hem anat
  # omplint. Com que fem la taula sortable, ja l'ordenarà el lector si vol
  for u, num in agraciats.items():
      #print dir(u)
      txtout = txtout+"|-\n"
      us= u.username
      usuaristr = u"[[Usuari:"+us+"|"+us+"]]"
      txtout = txtout+"| "+ usuaristr +"||"+ ("%d" % num)+"\n"

  # Tanquem la taula, canvi de columna
  txtout = txtout+"|}\n"
  txtout = txtout+"{{Columna nova}}\n"

  # ara ve la capçalera de la segona taula, la dels que fan agraïments
  txtout = txtout + u"{| class=\"wikitable sortable\"\n|+ Agraïments fets per usuari durant el mes de "+mescatala(mes)+" de "+anystr+"\n"
  txtout = txtout+u"|-\n! scope=\"col\" | Usuari\n! scope=\"col\" | Agraïments\n"
  # bucle amb les files dels que agraeixen
  for u, num in graciadors.items():
      txtout = txtout+"|-\n"
      usuaristr = u"[[Usuari:"+u+"|"+u+"]]"
      txtout = txtout+"| "+ usuaristr +"||"+ ("%d" % num)+"\n"
  # Tanquem taula, columnes i secció
  txtout = txtout+"|}\n"
  txtout = txtout+"{{Final columnes}}\n</div>\n"
  # Categoria, que no falti
  txtout = txtout+u"[[Categoria:Registre d'agraïments per mesos]]\n"

  # I ara gravem la pàgina. Primer generem el nom
  titolpag = u"Usuari:JoRobot/Agraïments/"+anystr+"/"+messtr
  # I amb això ho gravem
  pag = pywikibot.Page(casite,titolpag)
  pag.put(txtout,comment=u"Estadístiques d'agraïments",force=True)

# Ara cridem el main que hem definit, a la pythonesca manera
if __name__ == '__main__':
    try:
        main()
    finally:
        pass
