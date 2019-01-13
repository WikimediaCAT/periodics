**GESTIÓ DELS MES LLEGITS A LA PORTADA**

*mesllegits.py* - Script python que llegeix les estadístiques del dia abans i
actualitza la plantilla del carrusel de la portada.

Per fer-ho, té dos directoris: *textos* i *staging*
A *textos*, hi ha fitxers amb la informació que sortirà a la portada i la imatge
que es treurà. L'script python no escriu en aquest directori, només en llegeix.
Se suposa que algun humà hi posarà les coses. Només si els quatre articles més
llegits tenen el seu fitxer corresponent a *textos* s'actualitzarà la portada.
Si no, es quedarà igual.

A *staging*, l'script python hi crea uns fitxers de model com els que necessita
per funcionar. Són en format JSON, i es poden editar amb un editor de text.
Hi posa, com a suggeriment, el primer paràgraf de l'article de la Viquipèdia.
Es crea per als 10 primers articles. L'ideal seria que, abans d'arribar al
top-4, un article arribi al top-10, es creï a staging, i doni temps per
actualitzar-lo, però ja veurem.
El que ha de fer algú si veu un fitxer a *staging* és arreglar-lo, triar la
foto, i moure'l al directori *textos* (idealment, a *staging* no hi ha d'haver
res).

S'engegarà per crontab, a la matinada amb l'script *mesllegits.sh*, i ho anirà
provant al llarg del dia. Si s'executa moltes vegades en un dia, tampoc no
passa res, perquè intentarà gravar exactament el mateix article.

