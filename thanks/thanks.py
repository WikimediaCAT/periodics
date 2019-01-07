# -*- coding: utf-8 -*-

import pywikibot 
import re
import sys
from pywikibot.version import getversion
from pywikibot.login import LoginManager
 
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

def mescatala(mes):
  nomsmesos = ['gener', 'febrer', u'març', 'abril', 'maig', 'juny', 'juliol', 'agost', 'setembre', 'octubre', 'novembre', 'desembre']
  return nomsmesos[mes-1]

def prevmes(mes,any):
    if mes > 1:
       return (mes-1,any)
    else:
       return (12,any-1)

def nextmes(mes,any):
    if mes < 12:
       return (mes+1,any)
    else:
       return (1,any+1)

def main():
  #print sys.version
  #print getversion()

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
  if len(messtr)<2:
      messtr="0"+messtr
  anystr = sys.argv[1].strip()

  (messeg, anyseg) = nextmes(mes,anyllegit)
  messegstr = "%02d" % messeg
  anysegstr = "%d" % anyseg
  
  (mesprev, anyprev) = prevmes(mes,anyllegit)
  mesprevstr = "%02d" % mesprev
  anyprevstr = "%d" % anyprev

  casite = pywikibot.Site('ca')
  registre = casite.logevents(logtype="thanks",
                              end   =  anystr+"-"+messtr+"-01T00:00:00",
                              start =  anysegstr+"-"+messegstr+"-01T00:00:00",
                              #total=10,
                              )
  agraciats={}
  graciadors={} 

  if registre != None:
     for l in registre:
       try:
         agraciats[l.page()]=agraciats[l.page()]+1
       except KeyError:
         agraciats[l.page()]=1
       try:
         graciadors[l.user()]=graciadors[l.user()]+1
       except KeyError:
         graciadors[l.user()]=1

  txtout = u"<center>[[Usuari:JoRobot/Agraïments/"+anyprevstr+"/"+mesprevstr+u"|Mes anterior]] {{·}} '''Historial''' {{·}} [[Usuari:JoRobot/Agraïments/"+anysegstr+"/"+messegstr+u"|Mes següent]]</center>\n"
  txtout = txtout + u"<div align=\"center\">\n{{Columnes|66%}}\n"
  txtout = txtout + u"{| class=\"wikitable sortable\"\n|+ Agraïments rebuts per usuari durant el mes de "+mescatala(mes)+" de "+anystr+"\n"
  txtout = txtout+u"|-\n! scope=\"col\" | Usuari\n! scope=\"col\" | Agraïments\n"

  for u, num in agraciats.items():
      #print dir(u)
      txtout = txtout+"|-\n"
      us= u.username
      usuaristr = u"[[Usuari:"+us+"|"+us+"]]"
      txtout = txtout+"| "+ usuaristr +"||"+ ("%d" % num)+"\n"

  txtout = txtout+"|}\n"
  txtout = txtout+"{{Columna nova}}\n"

  txtout = txtout + u"{| class=\"wikitable sortable\"\n|+ Agraïments fets per usuari durant el mes de "+mescatala(mes)+" de "+anystr+"\n"
  txtout = txtout+u"|-\n! scope=\"col\" | Usuari\n! scope=\"col\" | Agraïments\n"
  for u, num in graciadors.items():
      txtout = txtout+"|-\n"
      usuaristr = u"[[Usuari:"+u+"|"+u+"]]"
      txtout = txtout+"| "+ usuaristr +"||"+ ("%d" % num)+"\n"
  txtout = txtout+"|}\n"
  txtout = txtout+"{{Final columnes}}\n</div>\n"
  txtout = txtout+u"[[Categoria:Registre d'agraïments per mesos]]\n"

  titolpag = u"Usuari:JoRobot/Agraïments/"+anystr+"/"+messtr
  pag = pywikibot.Page(casite,titolpag)
  pag.put(txtout,comment=u"Estadístiques d'agraïments",force=True)

main()
