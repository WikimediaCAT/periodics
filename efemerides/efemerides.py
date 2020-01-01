# -*- coding: utf-8 -*-

import pywikibot
import re
import sys
import codecs

# Diu si una pàgina enllaçada des de la Viquipèdia correspon a un humà
# Ho fa mirant la propietat corresponent de wikidata
def eshuma(nom):
  wdsite = pywikibot.Site("wikidata","wikidata")
  casite = pywikibot.Site("ca")
  # primer carreguem la pàgina des de la Viquipèdia
  pagina = pywikibot.Page(casite,nom)
  try:
     noelvolem = pagina.get()
  except pywikibot.NoPage:  # si la pàgina no existeix, no és humà
     return False
  except pywikibot.IsRedirectPage:
     pagina = pagina.getRedirectTarget()
     noelvolem = pagina.get()
  except Exception as e: print(e)

  # Ara mirem l'item corresponent a Wikidata, a partir de la nostra
  try:
     item = pywikibot.ItemPage.fromPage(pagina,wdsite)
  except Exception as e: print(e)

  # pugem la info que conté l'item de Wikidata
  item_dict = item.get()

  if 'P31' in item.claims:  # si tenim "instància de" (P31)
      llista = item.claims['P31']
      for clm in llista:
          quees = clm.getTarget()
          if quees.getID() == 'Q5':     # si és ésser humà (Q5)
            #print nom,u"és humà"
            return True

  return False

def mescatala(mes):
  nomsmesos = ['gener', 'febrer', 'març', 'abril', 'maig', 'juny', 'juliol', 'agost', 'setembre', 'octubre', 'novembre', 'desembre']
  return nomsmesos[mes-1]

# Extreu una secció sencera (a partir del títol) d'un article, i en retorna
# text sencer. Ho fa amb expressions regulars
def trobar_capcalera(text,titol):
   # Busca el títol entre ==, seguit de text, seguit de un altre encapçalament
   # de nivell 2
   # Posem parèntesi, per si ens passen una alternativa com Necrològiques|Defuncions
   m = re.search(r'==\s*('+titol+r')\s*==(.+?)^==',text,re.DOTALL|re.MULTILINE|re.IGNORECASE)
   # En general ho trobarà a la primera
   try:
      seccio = m.group(2)
   # però podria ser que fos l'última secció de totes. Llavors no hi haurà
   # cap més encapçalament després
   except:
      # Per si era l'última secció, busquem fins al final
      m = re.search(r'==\s*('+titol+')\s*==(.+?)',text,re.DOTALL|re.MULTILINE|re.IGNORECASE)
      try:
         seccio = m.group(2)
      except:       # Si ni així, retornem un None
         return None
   return seccio

# Obté la descripció de l'esdeveniment, que ve després de l'any. Sempre hi
# solen haver cometes i espais al davant, i les saltem
def retallar_esdev(text):
   # treu comes i espais del principi, i fins el primer salt de línia o
   # claudàtor
   ind = 0
   llargada = len(text)
   # primer saltem fins el primer text o número
   while ind < llargada and not (text[ind].isalnum() or text[ind] == '[' or \
                                 text[ind] =='\n'):
      ind = ind + 1
   # a partir d'aquí i fins el salt de línia ho guardem
   inici = ind
   while ind < llargada and text[ind]!='\n': 
       ind = ind + 1

   # abans, traiem les referències, si n'hi hagués
   retornar = treure_refs(text[inici:ind])
   return retornar

# Aquesta busca al text de la pàgina els esdeveniments. Seran de l'estil
# * [[1914]], comença la [[primera guerra mundial]]
# o bé
# * [[1492]]
# ** [[Colom]] descobreix Amèrica
# ** els [[reis Catòlics]] conquereixen el regne de Granada.
#
def buscar_esdeveniments(text,inici,final):
   # si hi ha múltiples esdeveniments, estaran en línies començades per **
   # les busquem, i si no hi ha això, busquem igualment (serà un sol esdeveniment)
   # quan entrem aquí, una altra funció ja ha parsejat l'any. Ens concentrem
   # en l'esdeveniment
   lesde = re.findall(r'^\*\*(.*)',text[inici:final],re.MULTILINE)
   # Aquesta expressió captura tots els esdeveniments que comencin per **
   # i vagin seguits
   #
   # retornarem la llista de toret, de moment la inicialitzem com a buida
   toret = []
   if len(lesde) > 0:
      for linia in lesde:
         esdev = linia
         if len(esdev) > 0:
            # directament afegim l'esdeveniment a la llista, només
            # retallem les cometes i espais del principi
            toret.append(retallar_esdev(esdev))
      return toret
   else:
      # si no hi ha més asteriscos, l'esdeveniment ve directament darrere
      # l'any, i només hem de fer una mica de neteja
      esdev = text[inici:final]
      if len(esdev) > 0:
         # el retornem empaquetat en una llista d'un sol element, per
         # homogeneïtat
         return [retallar_esdev(esdev)]
      else:         # això no crec que passi mai
         return []

# Aquesta funció té la mateixa estructura que buscar esdeveniments, de fet
# estan copiades. Es fa servir per naixements i defuncions
# la diferència és que es posa en camps separats el nom de la persona, i la
# descripció que ve a continuació.
# Això fallarà si el text diu.
# 1234, neix el fill de Denethor, [[Boromir]]
# Hauria de ser:
# 1234, neix [[Boromir]], fill de Denethor.
def buscar_persones(text,inici,final):
   # si hi ha múltiples persones, estaran en línies començades per **
   # les busquem, i si no hi ha això, busquem igualment (serà una sola persona)
   lpers = re.findall(r'^\*\*(.*)',text[inici:final],re.MULTILINE)
   toret = []
   if len(lpers) > 0:
      for linia in lpers:
        # un cop tenim cada línia, busquem on hi ha el protagonista del
        # naixement o defunció
        persona = trobar_huma(linia,0,len(linia))
        if len(persona) > 0:
           toret.append(persona)
      return toret
   else:
      persona = trobar_huma(text,inici,final)
      if len(persona)> 0:
        return [persona]
      else:     # això passa si la persona no té article, retornem llista buida
        return []

def buscar_persona_cell(celles):
   #print "buscant huma ",celles[1]
   persona = trobar_huma(celles[1],0,len(celles[1]))
   if len(persona)>0 and len(celles)>2:
      try:
        toret = (persona[0],celles[2].rstrip()+' '+celles[3].lstrip())
      except IndexError:
        toret = (persona[0],celles[2].rstrip())
      #print toret
      return [toret]
   # hi ha vegades que no hi ha el lloc de naixement i està a la primera
   # que ens passen
   persona = trobar_huma(celles[0],0,len(celles[0]))
   if len(persona)>0 and len(celles)>2:
      return [(persona[0],celles[1].rstrip()+' '+celles[2].lstrip())]
   # si no l'hem trobat, llista buida
   return []

def trobar_huma(text,inici,final):
   # Aquesta regex posa al grup 1, si existeix, l'enllaç real seguit
   # de la barra | (l'haurem de treure).
   # Si no hi ha grup 1, l'enllaç estarà al grup 2
   # Anirem buscant fins que trobem el primer ésser humà.
   # Així, si el text posa [[Boromir]], fill de [[Dénethor]], només ens
   # quedem amb el primer.
   # Si el text diu, "neix el fill de [[Dénethor]], [[Boromir]], cagada
   for mobj in re.finditer(r'\[\[([^|\]]*\|)?([^\]]+)\]\]',text[inici:final]):
      if mobj.group(1)!= None:
         nomsenselabarra = mobj.group(1)[0:-1]  # traient l'últim caràcter (|)
      else:
         nomsenselabarra = mobj.group(2)
      #print "nomsenselabarra", nomsenselabarra
      if eshuma(nomsenselabarra):
          #print "es huma"
          descripcio = trobar_desc(text[inici+mobj.end():])
          #print descripcio
          return mobj.group(0), descripcio
   
   # Si hem arribat fins aquí, no hem trobat cap humà, retornem un string buit
   return ''

def trobar_desc(text):
   # Llegeix el text que hi ha després de l'enllaç que hem trobat, i que descriu
   # la persona. Ens aturem al primer salt de línia, i traiem els blancs i
   # cometes que hi poden haver al principi.
   index = 0
   llargada = len(text)
   while (index < llargada) and not (text[index].isalnum() \
           or text[index]=='[' or text[index]=='\n' or text[index]=='<'):
       index = index + 1
   inici = index
   while index < llargada and text[index]!='\n': 
       index = index + 1
   retornar = treure_refs(text[inici:index])
   #print "retornem", retornar
   return retornar

def treure_claudators(text):
   # Traiem els claudàtors i només deixem el test que es vegi
   # Model "[[article|text]]" dona "text"
   text = re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]",r"\1",text)
   # Model "[[text]]" dona "text"
   text = re.sub(r"\[\[([^\]]+)\]\]",r"\1",text)
   return text

def treure_refs(text):
   # Traiem les referències que hi pugui haver.
   text = re.sub(r"<[Rr][Ee][Ff](\s*name\s*=[^>]*)?\s*>.*<\s*\/[Rr][Ee][Ff]\s*>","",text)
   text = re.sub(r"<[Rr][Ee][Ff](\s*name\s*=[^>]*)?\s*\/\s*>","",text)
   return text

def processar_esdeveniment(text,codi):
   esde = trobar_capcalera(text,"Esdeveniments|Fets històrics")
   if esde == None:
      return "No hi ha secció d'Esdeveniments"
   # Busquem strings com "* [[1234]]". Ignorem els anys anteriors al 100
   # Ens quedem només amb la posició. Entre any i any, tornarem a buscar,
   # perquè no sempre està tot en una línia.
   mobjant = None
   toret = []
   for mobj in re.finditer(r'\*\s*\[\[(\d{3,4})\]\]',esde):
      # Aquest bucle és complicat perquè la informació per buscar n
      # no la tens fins al pas n+1. Per això ens quedem referència del mobj
      # anterior. Busquem des del final de l'any anterior fins al principi
      # de l'actual
      if mobjant != None:
         lesdev = buscar_esdeveniments(esde,mobjant.end(),mobj.start())

         # Retornarem una llista de tuples (any, llista de persones)
         toret.append((mobjant.group(1),lesdev))
      mobjant = mobj
   # Quan sortim del bucle, encara en falta un
   if mobjant != None:
      lesdev = buscar_esdeveniments(esde,mobjant.start(),len(esde))
      toret.append((mobjant.group(1),lesdev))
      # return toret     No retornem, mirarem si hi ha taules
   # Fins aquí, és amb la sintaxi habitual. Hi ha articles, com el
   # [[7 d'abril]] que ho fan amb una taula en comptes de text. Ho tractem
   # aquí.
   # En altres articles, com [[10 de novembre]] hi conviuen els dos estils,
   # per tant mirem les dues coses.
   # else: Ho fem igualment
     # aquí no hi ha la dificultat d'abans. Tot està en una posició fixa
     # dins de la taula. Fem un split per cel·les de la taula
   for mobj in re.finditer(r'^\|\s*\[?\[?(\d{3,4})\]?\]?\s*\|\|(.*)',esde,re.MULTILINE):
        resta_fila = mobj.group(2)
        celles = resta_fila.split("||")
        desc_esdev = celles[0]+", "+celles[1]
        llistadesc = [desc_esdev]
        if len(llistadesc) > 0:
          toret.append((mobj.group(1),llistadesc))
   # i aquesta és pel cas de taules amb una cel·la per línia, com al 28 de
   # desembre
   for mobj in re.finditer(r'^\|\-\s*\n^\|\s*([^\n]*)\n^\|\s*([^\n]*)\n^\|\s*([^\n]*)\n^\|\s*([^\n]*)\n',esde,re.MULTILINE|re.DOTALL):
        # en aquest cas, l'any pot estar entre claudàtors
        anyet = treure_claudators(mobj.group(1))
        lloc = mobj.group(2)
        desc_esdev = mobj.group(3)
        destaca = mobj.group(4)
        perdesar = [lloc+", "+destaca+": "+desc_esdev]
        #print perdesar
        if len(perdesar)>0:
          toret.append((anyet,perdesar))
   return toret

# Aquesta es crida per naixements i defuncions
def processar_fet_biologic(text,codi):
   if codi == 'N':
      capcalera = "Naix[ie]ments"
   elif codi == 'D':
      capcalera = "Necrològiques|Defuncions|Morts"
   else:
      print('Error en la crida a processar_fet_biologic, hem rebut codi ',codi)
   naix = trobar_capcalera(text,capcalera)
   if naix == None:
      return "No hi ha secció de", capcalera
   # Busquem strings com "* [[1234]]". Ignorem els anys anteriors al 100
   # Ens quedem només amb la posició. Entre any i any, tornarem a buscar,
   # perquè no sempre està tot en una línia.
   mobjant = None
   toret = []
   for mobj in re.finditer(r'\*\s*\[\[(\d{3,4})\]\]',naix):
      # Aquest bucle és complicat perquè la informació per buscar n
      # no la tens fins al pas n+1. Per això ens quedem referència del mobj
      # anterior. Busquem des del final de l'any anterior fins al principi
      # de l'actual
      if mobjant != None:
         lpersones = buscar_persones(naix,mobjant.end(),mobj.start())

         # Retornarem una llista de tuples (any, llista de persones)
         toret.append((mobjant.group(1),lpersones))
      mobjant = mobj
   # Quan sortim del bucle, encara en falta un
   if mobjant != None:
     lpersones = buscar_persones(naix,mobjant.start(),len(naix))
     toret.append((mobjant.group(1),lpersones))
     # return toret     No retornem, mirarem si hi ha taules
   # Fins aquí, és amb la sintaxi habitual. Hi ha articles, com el
   # [[18 de març]] que ho fan amb una taula en comptes de text. Ho tractem
   # aquí.
   # En altres articles, com [[10 de novembre]] hi conviuen els dos estils,
   # per tant mirem les dues coses.
   # else: Ho fem igualment
     # aquí no hi ha la dificultat d'abans. Tot està en una posició fixa
     # dins de la taula. Fem un split per cel·les de la taula
   for mobj in re.finditer(r'^\|\s*\[?\[?(\d{3,4})\]?\]?\s*\|\|(.*)',naix,re.MULTILINE):
        resta_fila = mobj.group(2)
        celles = resta_fila.split("||")
        lpersones = buscar_persona_cell(celles)
        if len(lpersones)>0:
          toret.append((mobj.group(1),lpersones))

   # aquesta és pel cas d'enllaços on posa l'any enllaçant al lloc de naixement
   # estil
   # | [[Garigliano|1503]] || [[Pere II de Mèdici]] ''l'Infortunat'' || [[República de Florència|senyor]] || [[florentí]] || {{Age nts|1472|2|15|1503|12|28}}
   for mobj in re.finditer(r'^\|\s*\[\[[ \w,.\']+\|(\d{3,4})\]\]\s*\|\|(.*)',naix,re.MULTILINE):
        resta_fila = mobj.group(2)
        celles = resta_fila.split("||")
        lpersones = buscar_persona_cell(celles)
        if len(lpersones)>0:
          toret.append((mobj.group(1),lpersones))
   # i aquesta és pel cas de taules amb una cel·la per línia, com al 28 de
   # desembre
   for mobj in re.finditer(r'^\|\-\s*\n^\|\s*([^\n]*)\n^\|\s*([^\n]*)\n^\|\s*([^\n]*)\n^\|\s*([^\n]*)\n',naix,re.MULTILINE|re.DOTALL):
        # en aquest cas, l'any pot estar entre claudàtors
        anyet = treure_claudators(mobj.group(1))
        lloc = mobj.group(2)
        cellapersona = mobj.group(3)
        destaca = mobj.group(4)
        celles = [lloc,cellapersona,destaca]
        #print celles
        lpersones = buscar_persona_cell(celles)
        #print lpersones
        if len(lpersones)>0:
          toret.append((anyet,lpersones))
   return toret
 
# escrivim al fitxer de sortida, en un format estàndard
def gravar_fitxer(estructura,fitx,dia,mes,fet):
   for element in estructura:
       any_event = element[0]
       if fet=='N' or fet == 'D':   # Naixements o Defuncions
         for persona in element[1]:
           fitx.write("%s,%02d,%02d,%s,%s,%s\n" % (element[0],mes,dia,fet,persona[0],persona[1]))
       else:                        # Esdeveniments
         for esdeveniment in element[1]:
           fitx.write("%s,%02d,%02d,%s,%s\n" % (element[0],mes,dia,fet,esdeveniment))

# Llegeix tots els articles de dia d'un mes determinat, i crea una base de
# dades amb naixements, defuncions i esdeveniments, que després es podrà
# utilitzar per buscar efemèrides
def main():
   if len(sys.argv)!=2:
       print("Ús: python efemerides.py <número de mes>")
       exit()
   try:
       mes = int(sys.argv[1])
   except:
       print("Mes incorrecte")
       exit()

   casite = pywikibot.Site('ca')
   # Aquest serà el fitxer que gravarem, al subdirectori bd
   try:
       sortida = codecs.open("bd/efemerides_%02d.txt" % mes,'w',encoding='utf-8')
   except:
       print("No s'ha pogut crear el fitxer de sortida bd/efemerides_%02d.txt" % mes)
       exit()

   for dia in range(1,32):
       # apòstrof
       if mescatala(mes)[0] in ['a','o']:   # abril, agost o octubre
         strpag = "%d d'%s" % (dia,mescatala(mes))
       else:
         strpag = "%d de %s" % (dia,mescatala(mes))
       print(strpag)
       page = pywikibot.Page(casite,strpag)
       try:
           txt = page.get()
       except:
           # el dia no existeix: 30 de febrer o 31 de novembre
           continue
       naix = processar_fet_biologic(txt,'N')
       #print naix
       gravar_fitxer(naix,sortida,dia,mes,'N')
       defu = processar_fet_biologic(txt,'D')
       #print defu
       gravar_fitxer(defu,sortida,dia,mes,'D')
       esde = processar_esdeveniment(txt,'E')
       #print esde
       gravar_fitxer(esde,sortida,dia,mes,'E')

   sortida.close()

if __name__ == '__main__':
    try:
        main()
    finally:
        pass

