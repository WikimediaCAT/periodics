# -*- coding: utf-8 -*-

import sys, re
import pywikibot
from pywikibot import pagegenerators as pg
import inspect

def main():

   if len(sys.argv)!=1:
      print("Ús: treure_llista_bona.py")
      print("Busca tots els articles marcats com a \"llista bona\" a Wikidata i")
      print("els treu la distinció")
      return

   msg = ""
   error = 0

   # variables que necessitarem
   wdsite = pywikibot.Site("wikidata", "wikidata")
   repowd = wdsite.data_repository()
   casite = pywikibot.Site('ca')
   site_string = 'enwiki'

   # Aquest item és el que identifica que és llista bona
   # Les distincions són una llista d'items, i aquest és el de la llista bona
   item_llista_bona= pywikibot.ItemPage(wdsite,"Q51759403")  # Llista bona

   with open('llista_bona.rq','r') as fit_query:
      #QUERY = fit_query.read().replace('\n','')
      #Abans s'havien de treure els salts de línia, ara si ho fas dona error
      QUERY = fit_query.read()

   print(QUERY)
   # Aquesta crida fa la consulta SPARQL i retorna un iterador amb tots els
   # items qeu la compleixen. En aquest casa, tots els que tenen distinció
   # de llista bona

   #generador = pg.WikidataSPARQLPageGenerator(QUERY,item_name='item',site=wdsite)
   #for Q in generador:
   # Això ho descomentem per les proves, si no fem el bucle normal
   #prova= pywikibot.ItemPage(wdsite,"Q274866") # un paio, Émile-Alexandre Taskin
   prova= pywikibot.ItemPage(wdsite,"Q4115189")  # wikidata sandbox

   for Q in [prova]:
   # fins aquí és per fer proves
     item = Q

     try:
       item_dict = item.get()
     except pywikibot.NoPage:
       print("Això no haria de passar en article ",article)
       continue

     # No hi ha una primitiva que ens doni els Sitelinks com a tals,
     # getSitelink només et diu l'string del nom de l'article.
     # Per accedir als badges hem d'anar pel diccionari de l'item
     sls = item_dict['sitelinks']
     # sls és una SitelinkCollection
     # agafem el sitelink que ens interessa, que és cawiki
     casl = sls[site_string]
     strlink = item.getSitelink(site_string)
     # casl és el Sitelink a la wiki catalana
     # Existeix segur perquè si no, no hauria sortit a la query de SPARQL

     # casl.badges és una llista de badges associats a l'article i la wiki
     bdini = casl.badges
     try:
        bdini.remove(item_llista_bona)
     except ValueError:
        # aquesta excepció salta si l'item no té el badge de llista bona.
        # no ha de passar perquè si no no hauria sortit a la query de SPARQL
        # però a les proves t'hi pots trobar
        break
     # Amb això traiem només la distinció de llista_bona i si n'hi ha d'altres
     # les deixem intactes

     # print(casl.badges)

     # creem un sitelink nou en forma de diccionari i el gravem ja amb la
     # distinció treta.
     # S'ha de vigilar, perquè setSitelink només funciona si la llista de
     # badges és la mateixa que ja hi era o si la llista és buida. Si no, peta
     # Pel cas que ens ocupa, tant és, perquè no n'hi ha cap que sigui article
     # bo ni de qualitat, però si passés petaria i
     # - o fem l'item aquest a mà
     # - o hauríem d'esborrar l'enllaç i tornar-lo a crear.
     #
     dictnou = {'site':site_string, 'title':strlink, 'badges': bdini}
     item.setSitelink(dictnou, summary="Test to remove badges")

     #print(type(links))
     #print(dir(links))
     #print(links)


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()

