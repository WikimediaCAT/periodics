# -*- coding: utf-8 -*-

import pywikibot
import re
import sys
import codecs
import json
import requests
import datetime

def llegir_intro(article):
   casite = pywikibot.Site('ca')
   page = pywikibot.Page(casite,article)
   try:
      txt = page.get()
   except:
      print u"La pàgina "+article+" no existeix ?????"

   # Aquesta expressió regular agafa el principi de l'article, i s'atura
   # quan troba o bé un punt i apart (línia en blanc, ^$), o bé el principi
   # d'un encapçalament (^==). Multiline i Dotall perquè podem agafar moltes
   # línies
   mobj=re.match(r"(.*?)(^$|^==)",txt,re.MULTILINE|re.DOTALL)
   # Si ho trobem, traiem les referències i ho retornem.
   # Si no, retornem en blanc. No hauria de passar, però tampoc no és cap
   # tragèdia.

   if mobj != None:
      capcalera = treure_refs(mobj.group(1))
   else:
      capcalera = ""
   return capcalera

def capcalera_plantilla():
  a = '<noinclude><templatestyles src="Portada600k/styles.css" />[[Categoria:Plantilles de la portada 600k]]</noinclude>\n'
  a = a+'<div class="portada-slider" style="max-width:100%;position:relative">\n'
  a = a+'<ul>\n'
  return a

def final_plantilla():
  a = '</ul>\n'
  a = a + u'<div style="width:100%;position:absolute;bottom:0;left:0;padding:10px;background-color:{{linear-gradient|top|rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.75)}}; text-align:center;color:white; border-top-right-radius: 5px; box-shadow: rgba(0,0,0,0.8) 0 0 15px; border-top-left-radius: 5px;font-weight:bold">Els més llegits</div>\n'
  a = a + '</div>\n'
  return a

# per no liar-me amb locales, em faig una funció pròpia que posi els punts
# de milers en un enter
def puntsdemilers(numero):
  enlletres = "%d" % numero
  llargada = len(enlletres)
  final = enlletres[-3:]
  i = 1
  while i*3 < llargada:
     final = enlletres[-(i+1)*3:-i*3]+"."+final
     i = i + 1
  return final
    
def treure_subratllats(text):
  return text.replace("_"," ")

def element_carrusel(imatge,titol,descripcio,visites):
  strvisites = puntsdemilers(visites)
  a = '<li>\n'
  a = a + '{{Portada600k/elementcarrusel\n'
  a = a + '|imatge='+imatge+'\n'
  a = a + u'|títol='+treure_subratllats(titol)+'\n'
  a = a + u"|descripció= '''"+strvisites+" visites'''<br>"
  a = a + descripcio+'\n'
  a = a + '}}\n</li>\n'
  return a

def llegir_bd(titol):
   # Si existeix el fitxer a la base de dades, el llegim, i retornem el que
   # hem llegit
   try:
     with open("./textos/"+titol+".json","r") as entrada:
       dicc_json= json.load(entrada)
       return dicc_json
   # Si no, retornem un None, i ja farem
   except:
       return None

# Crea un fitxer model a l'àrea de staging, i l'omple amb info d'exemple
def crear_staging(titol, visites):
   rap = llegir_intro(titol)
   dicc_json = {}
   dicc_json['portada'] = []
   dicc_json['portada'].append({
       'article':titol,
       'imatge':"Posar_imatge_bona.jpg",
       'visites':visites,
       'text':rap
   })
   with open("./staging/"+titol+".json","w") as sortida:
      json.dump(dicc_json,sortida)
      sortida.close()

def treure_refs(text):
   # Traiem les referències que hi pugui haver.
   text = re.sub(r"<[Rr][Ee][Ff](\s*name\s*=[^>]*)?\s*>.*?<\s*\/[Rr][Ee][Ff]\s*>","",text)
   text = re.sub(r"<[Rr][Ee][Ff](\s*name\s*=[^>]*)?\s*\/\s*>","",text)
   return text

# Actualitza la pàgina [[Plantilla:Portada600k/carruselmésllegits]]
def main():
   if len(sys.argv)!=1:
       print u"Ús: python mesllegits.py"
       exit()

   avui = datetime.date.today()
   ahir = avui + datetime.timedelta(days=-1)
   any_actual = avui.year
   mes = avui.month
   dia = ahir.day
   # Obtenim les dades que es generen automàticament
   uri = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ca.wikipedia.org/all-access/%d/%02d/%02d" % (any_actual,mes,dia)
   #print "llegint",uri
   try:
     resposta = requests.get(uri)
   except:
     print "Problema llegint dades de wikimedia.org"
     exit()
   if resposta.status_code != 200:
     print "Llegint dades de wikimedia.org hem obtingut codi %d" % resposta.status_code
     exit()
   # Ara tenim les dades, i les passem a JSON
   ranking = json.loads(resposta.text)
   # Ja tenim un diccionari a ranking. Només té una clau, que és items
   # Hi accedim fent ranking.items() (encara que suposo que podria fer-se amb
   # ranking['items']
   # ranking.items() és una llista d'un sol element. Per tant, hem de fer
   # ranking.items()[0]
   # Aquest element és una tupla que conté primer l'string 'items' i després
   # la info de veritat. Per tant, ranking.items()[0][1]
   # Aquí tenim una llista d'un sol element. Per tant, ranking.items()[0][1][0]
   # Amb això arribem a un altre diccionari que conté més items, com
   # project, access, year, month, ... Però el que ens interessa és 'articles'
   # Ara ja tenim una llista de diccionaris que ja tenen les dades
   # Si no arribem aquÍ hi ha hagut algun problema i sortim
   try:
     llista = ranking.items()[0][1][0]['articles']
   except:
     print "Error accedint a les dades JSON"
     exit()

   candidats = 0
   # Candidats són els articles que poden anar a la portada. N'excloem la
   # pròpia portada, que sempre és la primera, i els que comencin per
   # "Especial:", com "Especial:Cerca" i "Especial:Canvis_recents"
   mes_vistos = []
   # mes_vistos és una llista que anirem omplint amb tuples (article, visites)
   for elt_article in llista:
      titol = elt_article['article']
      vistes = elt_article['views']
      if titol!="Portada" and titol[0:9]!="Especial:":
         candidats = candidats + 1
         mes_vistos.append((titol,vistes))
      if candidats >= 10:
         break

   # ara comencem un bucle per veure si tenim totes les dades per publicar.
   # primer suposarem que sí, però només que ens en falti una, serà que no.
   textplantilla = capcalera_plantilla()
   podemgravar = True
   for i in mes_vistos[0:4]:    # Recorrem els quatre primers del rànquing
     article = i[0]
     visites = i[1]
     # Mirem si ja tenim preparada foto i introducció
     info_json = llegir_bd(article)
     # si no la tenim preparada, no podrem gravar, 
     # i creem el fitxer de staging, però continuem fent els
     # altres articles
     if info_json == None:
        podemgravar = False
        crear_staging(article,visites)
     else:
        imatge = info_json['portada'][0]['imatge']
        text = info_json['portada'][0]['text']
        textplantilla = textplantilla+element_carrusel(imatge,article,text,visites)
   if podemgravar:
     textplantilla = textplantilla + final_plantilla()
     casite = pywikibot.Site('ca')
     nomplant = u"Plantilla:Portada600k/carruselmésllegits"
     pagina = pywikibot.Page(casite,nomplant)
     #print textplantilla
     pagina.put(textplantilla,comment=u"Robot actualitza carrusel de més llegits amb dades de %d/%d/%d" % (dia,mes,any_actual))
   # la resta, directes a staging
   for i in mes_vistos[4:]:
     article = i[0]
     visites = i[1]
     # Per la resta, només creem l'staging si no existeix a textos
     info_json = llegir_bd(article)
     if info_json == None:
        crear_staging(article,visites)
     

if __name__ == '__main__':
    try:
        main()
    finally:
        pass

