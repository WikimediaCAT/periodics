# -*- coding: utf-8 -*-

import pywikibot
import sys
import os
from os import listdir

# Mira si algun article ha canviat de nom i és redirecció, i posa el nom final
def main():

   # Són els directoris on treballarem
   dirbase = './'
   dirbd   = dirbase+'textos'
   dirsta  = dirbase+'staging'

   casite = pywikibot.Site('ca')

   # ho fem pels dos directoris, successivament
   for directori in dirbd,dirsta:
     # llegim el directori i ho posem en una llista
     fitxers = [f for f in listdir(directori)]
     for f in fitxers:
        # seguim la llista i tractem cada fitxer
        # separem l'extensió, només ens interessen els json
        article, extensio = os.path.splitext(f)
        if extensio == '.json':
           #article = str(article,'utf-8')
           # Mirem l'article corresponent
           pg = pywikibot.Page(casite,article)
           # si és redirecció, mirem on va i anem resseguint
           while pg.isRedirectPage():
              pg = pg.getRedirectTarget()
           # mirem quin títol ha quedat al final
           pagename = pg.title()
           # preparem el nom de fitxer amb _ i el comparem amb el del directori
           pagename = pagename.replace(" ","_")
           article = article.replace(" ","_")
           # si el nom ha canviat, és que era redirecció, i ho hem de canviar
           # a la nostra base de dades
           if pagename != article:
             print(pagename + " era un redirect")
             os.rename(directori+'/'+f,directori+'/'+pagename+'.json')
   exit()


if __name__ == '__main__':
    try:
        main()
    finally:
        pass

