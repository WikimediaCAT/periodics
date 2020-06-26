# -*- coding: utf-8 -*-

import pywikibot
import re
import sys
import codecs
import json
import requests
import datetime

# Va a wikidata, busca si hi ha un fitxer d'imatge, i el torna. Si no,
# retorna None
# El paràmetre és una pywikibot.Page
def wd_imatge(pagina):
   trobat = False
   try:
      item = pywikibot.ItemPage.fromPage(pagina,pywikibot.Site("wikidata","wikidata"))
   except:   # si no hi ha item, ja podem plegar
      return None
   item_dict = item.get()
   if 'P18' in item.claims:     # P18 és la imatge
      clm_dict = item_dict["claims"]
      clm_fitxer = clm_dict["P18"]
      for clm in clm_fitxer:
          tg = clm.getTarget()
          nom_fitxer = tg.title(with_ns=False)
          trobat = True
          break         # Només passarem un cop pel bucle, ja n'hi ha prou
   if trobat:
      return nom_fitxer
   else:
      return None

# Funció booleana que indica si un fitxer és a commons, a cawiki o no existeix
def fitxer_existeix(nomfit):
   commons = pywikibot.Site('commons','commons')
   wp_file = pywikibot.FilePage(commons,nomfit)
   try:
      fitxerexisteix = wp_file.exists()
   except:
      fitxerexisteix = False
   # Si ja l'hem trobat a Commons no cal buscar més
   if fitxerexisteix:
      return True
   # ara busquem a cawiki
   casite = pywikibot.Site('ca')
   wp_file = pywikibot.FilePage(casite,nomfit)
   try:
      fitxerexisteix = wp_file.exists()
   except:
      fitxerexisteix = False
   return fitxerexisteix

# Salta espais en blanc, i retorna un punter al primer caràcter que no és blanc
# s'utilitza a saltar_plantilles()
def saltar_blancs(text):
   p = 0
   while p < len(text):
      if text[p].isspace():
          p = p+1
      else:
          break
   return p

# Funció que utilitza llegir_intro() per saltar-se les plantilles de l'inici
# d'un article: infotaules, coses de manteniment, el que sigui. Així, la
# introducció que s'agafi ja serà directament text.
def saltar_plantilles(text):
   nivell = 0
   p = saltar_blancs(text)
   while True:
       if text[p] == '{':
           nivell = nivell + 1
       elif text[p] == '}':
           nivell = nivell - 1
       elif text[p].isspace():
           p = p + 1
           continue
           # Aquest continue és important perquè no volem fer la comprovació
           # de nivell ara. Si hi ha dues plantilles seguides només separades
           # per blancs o salts de línia, també ens les volem saltar
       else:
           if nivell == 0:
              break
       p = p + 1
    # D'aquí en sortim amb el primer caràcter no blanc que està fora d'una 
    # plantilla
   return p

def llegir_intro(article):
   casite = pywikibot.Site('ca')
   page = pywikibot.Page(casite,article)
   try:
      txt = page.get()
   except pywikibot.IsRedirectPage:
      page = page.getRedirectTarget()
      txt = page.get()
   except:
      print("La pàgina "+article+" no existeix ?????")
      exit()

   # Primer saltem les plantilles que hi pugui haver. Buscarem a partir d'aquí
   p = saltar_plantilles(txt)

   # Aquesta expressió regular agafa el principi de l'article, i s'atura
   # quan troba o bé un punt i apart (línia en blanc, ^$), o bé el principi
   # d'un encapçalament (^==). Multiline i Dotall perquè podem agafar moltes
   # línies
   mobj=re.match(r"(.*?)(^$|^==)",txt[p:],re.MULTILINE|re.DOTALL)
   # Si ho trobem, traiem les referències i ho retornem.
   # Si no, retornem en blanc. No hauria de passar, però tampoc no és cap
   # tragèdia.

   if mobj != None:
      capcalera = treure_refs(mobj.group(1))
   else:
      capcalera = ""
   # Ara busquem si a wikidata hi ha una imatge
   nom_fitxer = wd_imatge(page)

   # Si no hi ha imatge a wikidata, busquem al text a veure si hi ha sort
   if nom_fitxer == None:
       mobj = re.match(r"\|\s*imat?ge\s*=(.*?)\.([Pp][Nn][Gg]|[Jj][Pp][Gg])",txt,re.MULTILINE|re.DOTALL)
       if mobj != None:
           nom_fitxer = mobj.group(1)+'.'+mobj.group(2)
   # retornem la capcalera generada i el suggeriment de fitxer, encara que
   # sigui None
   return (capcalera,nom_fitxer)

def capcalera_plantilla():
  a = '<noinclude><templatestyles src="Portada600k/styles.css" />[[Categoria:Plantilles de la portada 600k]]</noinclude>\n'
  a = a+'<div class="portada-slider" style="max-width:100%;position:relative">\n'
  a = a+'<ul>\n'
  return a

def final_plantilla():
  a = '</ul>\n'
  a = a + '<div style="width:100%;position:absolute;bottom:0;left:0;padding:10px;background-color:{{linear-gradient|top|rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.75)}}; text-align:center;color:white; border-top-right-radius: 5px; box-shadow: rgba(0,0,0,0.8) 0 0 15px; border-top-left-radius: 5px;font-weight:bold">Tendències</div>\n'
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
  a = a + '|títol='+treure_subratllats(titol)+'\n'
  #quan només mirem l'aplicació web no donem el nombre de visites
  #a = a + u"|descripció= '''"+strvisites+" visites'''<br>"
  a = a + "|descripció= "
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
   (rap,fitxer) = llegir_intro(titol)
   if fitxer == None:
      model = "Posar_imatge_bona.jpg"
   else:
      model = fitxer
   dicc_json = {}
   dicc_json['portada'] = []
   dicc_json['portada'].append({
       'article':titol,
       'imatge':model,
       'visites':visites,
       'text':rap
   })
   with open("./staging/"+titol+".json","w") as sortida:
      json.dump(dicc_json,sortida)
      sortida.close()

def treure_refs(text):
   # Traiem les referències que hi pugui haver.
   text = re.sub(r"<[Rr][Ee][Ff](\s*(name|group)\s*=[^>]*)?\s*>.*?<\s*\/[Rr][Ee][Ff]\s*>","",text)
   text = re.sub(r"<[Rr][Ee][Ff](\s*(name|group)\s*=[^>]*)?\s*\/\s*>","",text)
   return text

def seguir_redirects(article):

   casite = pywikibot.Site('ca')

   # Mirem l'article corresponent
   pg = pywikibot.Page(casite,article)
   # si és redirecció, mirem on va i anem resseguint
   while pg.isRedirectPage():
      pg = pg.getRedirectTarget()
   # mirem quin títol ha quedat al final
   pagename = pg.title()

   pagename = pagename.replace(" ","_")
   return pagename

def logsortida(cadena,fitxer):
   fitxer.write(cadena+'\n')
   print(cadena)
   return

# Actualitza la pàgina [[Plantilla:Portada600k/carruselmésllegits]]
def main():
   if len(sys.argv)!=1:
       print("Ús: python3 mesllegits.py")
       exit()

   # Proves
   #crear_staging(u"Carles Sabater i Hernàndez","1234")
   #exit()
   fout = open("./mesllegits.resultat","w")
   avui = datetime.date.today()
   ahir = avui + datetime.timedelta(days=-1)
   any_actual = ahir.year
   mes = ahir.month
   dia = ahir.day
   # Obtenim les dades que es generen automàticament
   # això era quan miràvem els accessos totals
   #uri = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ca.wikipedia.org/all-access/%d/%02d/%02d" % (any_actual,mes,dia)
   # ara mirarem des del web mòbil
   uri = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ca.wikipedia.org/mobile-web/%d/%02d/%02d" % (any_actual,mes,dia)
   #print "llegint",uri
   try:
     resposta = requests.get(uri)
   except:
     logsortida("Problema llegint dades de wikimedia.org",fout)
     exit()
   if resposta.status_code != 200:
     logsortida("Llegint dades de wikimedia.org hem obtingut codi %d" % resposta.status_code,fout)
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
     llista = list(ranking.items())[0][1][0]['articles']
   except:
     logsortida("Error accedint a les dades JSON",fout)
     exit()

   candidats = 0
   # Candidats són els articles que poden anar a la portada. N'excloem la
   # pròpia portada, que sempre és la primera, i els que comencin per
   # "Especial:", com "Especial:Cerca" i "Especial:Canvis_recents"
   # Igual amb els "Special:", que de vegades surt "Special:Search"
   mes_vistos = []
   # mes_vistos és una llista que anirem omplint amb tuples (article, visites)
   for elt_article in llista:
      titol = elt_article['article']
      vistes = elt_article['views']

      if titol!="Portada" and titol[0:9]!="Especial:" and titol[0:11]!="Viquipèdia:" and titol[0:8]!="Special:" and titol[0:7]!="Usuari:" and titol[0:8]!="Usuària:" and titol[0:12]!="Usuari Discu" and titol[0:7]!="Fitxer:":
         # Mirem si hi ha redireccions, i posem només el del final
         # i només si encara no hi és. De vegades passa que el mateix
         # article està al top 10 dues vegades amb noms diferents
         titol = seguir_redirects(titol)
         if titol not in mes_vistos:
           candidats = candidats + 1
           mes_vistos.append((titol,vistes))
      if candidats >= 10:
         break

   # ara comencem un bucle per veure si tenim totes les dades per publicar.
   # primer suposarem que sí, però només que ens en falti una, serà que no.
   textplantilla = capcalera_plantilla()
   podemgravar = True

   # Fitxer que creem per la integració amb l'aplicació web. Indica quins són
   # els articles del top 4 del dia
   ftop4 = open("./mesllegits.top4","w")
   for i in mes_vistos[0:4]:    # Recorrem els quatre primers del rànquing
     article = i[0]
     visites = i[1]

     # Escrivim el nom de l'article al fitxer de Top 4
     ftop4.write(article+'\n')

     # Mirem si ja tenim preparada foto i introducció
     info_json = llegir_bd(article)
     # si no la tenim preparada, no podrem gravar, 
     # i creem el fitxer de staging, però continuem fent els
     # altres articles
     if info_json == None:
        podemgravar = False
        logsortida(("No podem gravar perquè l'article "+article+" no és a la BD"),fout)
        crear_staging(article,visites)
     else:
        imatge = info_json['portada'][0]['imatge']
        text = info_json['portada'][0]['text']
        # Ara comprovem que la imatge llegida existeix, per si de cas
        # Total, és un fitxer generat manualment i podria haver-hi un error.
        # Si no existeix, no podrem
        # gravar
        # important aquest and, perquè sinó un fitxer que existia invalidava
        # totes les proves precedents
        podemgravar = podemgravar and fitxer_existeix(imatge)
        if not fitxer_existeix(imatge):
           logsortida("No podem gravar perquè el fitxer "+imatge+" no existeix",fout)
        textplantilla = textplantilla+element_carrusel(imatge,article,text,visites)

   ftop4.close()        # ja estem d'aquest fitxer

   if podemgravar:
     textplantilla = textplantilla + final_plantilla()
     casite = pywikibot.Site('ca')
     nomplant = "Plantilla:Portada600k/carruselmésllegits"
     pagina = pywikibot.Page(casite,nomplant)

     # abans de gravar, mirem si ja està bé. Per crontab s'executarà uns
     # quants cops i potser és redundant
     textactual = pagina.get()
     # Pot ser que siguin iguals, excepte el salt de línia final. Fem un
     # rstrip() per si de cas
     if textactual.rstrip() != textplantilla.rstrip():
        pagina.put(textplantilla,comment="Robot actualitza carrusel de més llegits amb dades de %d/%d/%d" % (dia,mes,any_actual))
        #print textplantilla

     # Això ho diem tant si ha gravat com si no. La qüestió és que està bé.
     logsortida("Pàgina actualitzada OK", fout)
   else:
     # Si pel que sigui no hem gravat, donem un missatge
     logsortida("Pàgina no actualitzada", fout)

   # la resta, directes a staging
   for i in mes_vistos[4:]:
     article = i[0]
     visites = i[1]
     # Per la resta, només creem l'staging si no existeix a textos
     info_json = llegir_bd(article)
     if info_json == None:
        crear_staging(article,visites)
     
   fout.close()

if __name__ == '__main__':
    try:
        main()
    finally:
        pass

