# -*- coding: utf-8 -*-

import sys, re
import pywikibot
from pywikibot import pagegenerators as pg
import json

def main():

   if len(sys.argv)!=1:
      print("Ús: distincions.py")
      print("Treu un llistat de tots els articles que tenen alguna distinció a Wikidata")
      return

   # variables que necessitarem
   wdsite = pywikibot.Site("wikidata", "wikidata")
   repowd = wdsite.data_repository()
   casite = pywikibot.Site('ca')
   site_string = 'enwiki'
   error_critic = False
   l_estadistiques = []

   with open('llistar_badges.rq','r') as fit_query:
      #QUERY = fit_query.read().replace('\n','')
      #Abans s'havien de treure els salts de línia, ara si ho fas dona error
      QUERY = fit_query.read()

   print(QUERY)
   # Aquesta crida fa la consulta SPARQL i retorna un iterador amb tots els
   # items que la compleixen. En aquest cas, les diferents distincions que com
   # a mínim té algun item

   generador = pg.WikidataSPARQLPageGenerator(QUERY,item_name='badge',site=wdsite)
   for badge in generador:
   # Això ho descomentem per les proves, si no fem el bucle normal
   #prova= pywikibot.ItemPage(wdsite,"Q4115189")  # wikidata sandbox

   #for Q in [prova]:
   # fins aquí és per fer proves
     item = badge

     try:
       item_dict = item.get()
     except pywikibot.NoPage:
       print("Això no haria de passar en badge ",badge)
       continue

     if 'ca' in item.labels:
         print("Badge ",item.labels['ca'])
         badge_sense_espais= item.labels['ca'].replace(" ", "_")
         idbadge = item.getID()
         print(type(idbadge))
     else:
         print("Badge ", badge, "no té etiqueta en català")
         error_crític = True
         break

     query_badge = """SELECT ?sitelink ?laq ?laqLabel WHERE {
     ?sitelink schema:isPartOf <https://ca.wikipedia.org/>;
        schema:about ?laq;
        wikibase:badge wd:"""+str(idbadge)+" .\n"
     query_badge += """SERVICE wikibase:label { bd:serviceParam wikibase:language "ca" } .
}  ORDER BY ?sitelink
"""
     # si és "enllaç a una redirecció (Q70893996)
     # o bé "enllaç intencionat a una redirecció (Q70894304)
     # o bé "llista bona (Q51759403)
     # posem un límit al llistat, perquè igualment no ens interessa
     if (idbadge == "Q70893996") or (idbadge == "Q70894304") or (idbadge == "Q51759403"):
        query_badge += "LIMIT 50"
     print(query_badge)
     iterador = pg.WikidataSPARQLPageGenerator(query_badge,item_name='laq',site=wdsite)
     fout = open("articles/articles."+badge_sense_espais+"."+idbadge,"w")

     cmpt = 0
     print("anem a entrar al bucle")
     for qbadge in iterador:
         itemqbadge = qbadge.get()
         nom_article = qbadge.getSitelink(casite)
         fout.write(nom_article+"\n")
         cmpt += 1

     fout.close()
     estadistiques = { 'badge':idbadge , 'n_articles':cmpt}
     l_estadistiques.append(estadistiques)

   stats_json=json.dumps(l_estadistiques)
   with open("estadistiques.json","w") as stats:
       stats.write(stats_json)



     #print(type(links))
     #print(dir(links))
     #print(links)


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()

