# -*- coding: utf-8 -*-

import pywikibot
import re
import sys
import codecs
import csv
import datetime

# Bloc del principi de la pàgina d'efemèrides, amb contingut constant
# simplement, es bolca tot en un string, i es retorna aquest string
def capcalera_plantilla(mes):
  contingut=u'<noinclude><templatestyles src="Portada600k/styles.css" />[[Categoria:Efemèrides de '+ mescatala(mes)+u' de la portada 600k]]</noinclude>'
  contingut = contingut + '\n' + "<div class=caixa-flex>"
  contingut = contingut + '\n' + '<div style="display:flex; flex:1 1 0; flex-direction:column;min-width:75%;height:100%">'
  contingut = contingut + '\n'
  contingut = contingut + '\n' + '<div class=caixa-flex>'
  contingut = contingut + '\n' + u'{{Portada600k/blocefemèrides\n|contingut=\n'
  #print contingut
  return contingut

# Bloc del final de la pàgina d'efemèrides, amb contingut constant
# simplement, es bolca tot en un string, i es retorna aquest string
def final_plantilla():
   contingut = '}}\n{{Portada600k/imatge |imatge=Exemple.jpg |peu= }}'
   contingut = contingut + '\n'+'</div><!--tanquem caixa -->'
   contingut = contingut + '\n'+'<div>'
   contingut = contingut + '\n'+'<div style="padding:5px 10px 5px 10px;text-align:center">'
   #print contingut
   return contingut

# Aquesta funció busca al fitxer una efemèride que hagi passat exactament
# en un dia concret de fa "quantfa" anys
def buscar_efemerides(fitxer, dia, mes, anyv, quantfa):
   # En general, el fitxer estarà ordenat per dies, però és igual
   # el llegim tot igualment.
   fitxer.seek(0)       # Ens posem al principi, perquè el cridarem molts cops

   # Segurament podríem fer-ho més eficient, ordenant el fitxer, però com
   # que és petit, tampoc no cal matar-s'hi gaire
   any_objectiu = anyv - quantfa
   # variable que contindrà la sortida, per escriure al fitxer
   contingut = ""
   # aquest bucle el podria haver fet amb csv, però falla amb Unicode
   # Total, amb un split vas que t'estrelles
   for fil in fitxer:
       # Trenca la fila en un màxim de 6 strings separats per comes
       # 5 hi són segurs a totes [0:4]
       # 6 hi són segurs a naixements i defuncions [0:5]
       # a esdeveniments no té per què haver-hi el sisè
       fila = fil.split(',',5)
       if any_objectiu == int(fila[0]) and mes == int(fila[1]) and \
          dia == int(fila[2]):
          # Hem trobat una efemèride. Diem què ha passat.
          if fila[3] == 'N':
             fet_biol = "Neix "
             text = fila[4]+", "+fila[5]
          elif fila[3] == 'D':
             fet_biol = "Mor "
             text = fila[4]+", "+fila[5]
          else:
             fet_biol = u" "
             try:                   # provem si hi ha fila[5]
                text = fila[4]+", "+fila[5]
             except IndexError:     # si fila[5] no existeix, posem fila[4] i prou
                text = fila[4]
          # Traiem el salt de línia que hem llegit al final
          text = text.rstrip()
          # Ja podem generar la línia que escriurem
          contingut = contingut+(u"{{Portada600k/efemèride |anys = %d|text =%s%s}}" % (quantfa,fet_biol,text)).encode("utf-8")+'\n'
   return contingut

# Funció per construir el dia, que posi "2 de gener" o "1 d'octubre"
def const_dia(dia,mes):
  if mes == 4 or mes == 8 or mes == 10: # abril, agost, octubre
    deod = "d'"
  else:
    deod = "de "
  return("%s %s%s" % (dia,deod,mescatala(mes)))

def mescatala(mes):
  nomsmesos = ['gener', 'febrer', u'març', 'abril', 'maig', 'juny', 'juliol', 'agost', 'setembre', 'octubre', 'novembre', 'desembre']
  return nomsmesos[mes-1]

# construim la part de navegació de la plantilla, amb enllaços a:
# ahir
# demà
# mes d'ahir
# mes de demà (que sovint serà el mateix que ahir)
def navegacio_efemerides(dia,mes,anyv):
   data = datetime.date(anyv,mes,dia)
   # manera de fer aritmètica de dates amb python. Saltes un dia enrere i
   # tens ahir
   dia_abans = data + datetime.timedelta(days=-1)
   # saltes un dia endavant i tens demà
   endema = data + datetime.timedelta(days=1)
   # li mirem el mes
   mes_abans = dia_abans.month
   mes_despres = endema.month
   # obtenim el nom en català
   text_mes_abans = mescatala(mes_abans)
   # hi posem majúscula
   text_mes_abans = text_mes_abans[0].upper()+text_mes_abans[1:]
   # el mateix amb el mes de l'endemà
   text_mes_despres = mescatala(mes_despres)
   text_mes_despres = text_mes_despres[0].upper()+text_mes_despres[1:]
   text_dia_volgut = const_dia(dia,mes)
   text_dia_abans = const_dia(dia_abans.day,dia_abans.month)
   text_dia_despres = const_dia(endema.day,endema.month)
   # Ara ja ho podem construir
   contingut = (u'{{Portada600k/navegacióefemèrides|mesanterior=%s |diaanterior=%s |avui=%s |diaposterior= %s|mesposterior=%s}}' % (text_mes_abans,text_dia_abans,text_dia_volgut,text_dia_despres,text_mes_despres)).encode("utf-8")
   contingut = contingut + '\n' + '</div>'
   contingut = contingut + '\n' + '</div>'
   contingut = contingut + '\n' + '</div>'
   #print contingut
   return contingut

# Els arguments són:
# any mes i dia primer que es crearà
# nombre de dies que es vol fer d'una tongada
# un 1 si es vol crear ja els articles; si només es volen fer proves, o no
# poses res, o poses qualsevol cosa que no sigui un 1
def main():
   if len(sys.argv)!=5 and len(sys.argv)!=6:
       print u"Ús: python dates_rodones.py <any> <mes> <dia> <nombre_dies> <gravar (1 o 0)>"
       exit()
   try:
       any_volgut = int(sys.argv[1])
   except:
       print u"Any incorrecte"
       exit()

   try:
       mes = int(sys.argv[2])
   except:
       print u"Mes incorrecte"
       exit()

   try:
       dia = int(sys.argv[3])
   except:
       print u"Dia incorrecte"
       exit()

   try:
       n_dies = int(sys.argv[4])
   except:
       print u"Nombre de dies incorrecte"
       exit()

   try:
       ngravar = int(sys.argv[5])
       if ngravar == 1:
         gravar = True
       else:
         gravar = False
   except:
       # si no hi ha el número o no és enter, no gravem
       gravar = False

   casite = pywikibot.Site('ca')
   data = datetime.date(any_volgut,mes,dia)
   # obrim la base de dades que toca segons el mes
   try:
      fitx_efem = codecs.open("bd/efemerides_%02d.txt" % mes,'r',encoding='utf-8')
   except:
      print u"No hem pogut obrir el fitxer bd/efemerides_%02d.txt" % mes
      exit()
   # Comencem el bucle principal, que fem per cada dia que hem de tractar
   i = 0
   while i < n_dies:
      # És important posar el .encode a la primera, perquè llavors el python
      # ja sap que contingut serà de tipus unicode, i no petarà quan li
      # vinguin accents i ces trencades a la resta de línies
      # si no, petava al primer accent (el d'efemèrides)
      contingut = capcalera_plantilla(mes).encode("utf-8")
      # Anys interessants del primer segle
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,1)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,2)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,3)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,4)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,5)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,10)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,15)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,20)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,25)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,30)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,40)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,42)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,49)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,50)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,60)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,70)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,75)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,80)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,90)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,99)
      # anys rodons de segles
      for anys in range(1,19):
         contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,anys*100)
      # algun altre més
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,150)
      contingut = contingut + buscar_efemerides(fitx_efem,dia,mes,any_volgut,250)
      # Ara ja tanquem
      contingut = contingut + '\n' + final_plantilla()
      contingut = contingut + '\n' + navegacio_efemerides(dia,mes,any_volgut)
      print contingut
      # si ens han dit que creem la pàgina, ho fem
      if gravar:
         nomplant = u"Plantilla:Portada600k/efemèride %s %d" % (mescatala(mes),dia)
         page = pywikibot.Page(casite,nomplant)
         page.put(contingut,comment=u"Robot prepara plantilla amb efemèrides")

      # ara ja comptem quin dia és demà, per la següent volta al bucle
      data = data + datetime.timedelta(days=1)
      dia = data.day
      mes = data.month
      any_volgut = data.year
      i = i +1
   pass

if __name__ == '__main__':
    try:
        main()
    finally:
        pass

