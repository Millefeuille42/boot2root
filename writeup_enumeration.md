# Boot2Root

## 1. Trouver le serveur
On a pas l'IP du serveur.
On lance un `nmap -sn <mask>` pour énumerer les serveurs qui répondent au ping
    
Heureusement on trouve une IP différente de la notre qui répond au ping

## 2. Enumerer
### 2.1 Hote et services
On lance alors on `nmap -p- -A -sV -T4 <ip>` pour obtenir un max d'info sur le serveur
    
On y trouve différent services:
- ftp sur le port 21 (vsftpd 2.0.8 or later)
- ssh sur le port 22 (OpenSSH 5.9p1)
- http(s) sur le port 80 et 443 (Apache httpd 2.2.22)
- imap(s) sur le port 143 et 993 (Dovecot imapd)

On conserve le log sous le coude au cas ou on puisse en tirer plus d'infos utiles.

### 2.2 HTTP
On décide de commencer par le serveur http(s)
On lance alors nikto sur le port 80, et on ne tire rien de bien probant pour le moment
On essaie le mode ssl, et la on obtient plus d'infos

Différentes routes
- `/forum`
- `/phpmyadmin`
- `/webmail`
- `/icons`
La plupart des routes nosu donnent des pistes a explorer.

Différentes faiblesses potentielles

- `Hostname '192.168.56.106' does not match certificate's names: BornToSec. See: https://cwe.mitre.org/data/definitions/297.html`
- `The Content-Encoding header is set to "deflate" which may mean that the server is vulnerable to the BREACH attack. See: http://breachattack.com/`
- `/icons/README: Server may leak inodes via ETags, header found with file /icons/README, inode: 47542, size: 5108, mtime: Tue Aug 28 12:48:10 2007. See: http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2003-1418`

#### 2.2.1 PHPMyAdmin
On décide d'aller vers le plus évident: PHPMyAdmin

En allant sur la route `/phpmyadmin` on trouve deux infos intéressantes:
- L'URL de l'image contient un token `token=3e6cab1c9cf8cda6115b523f5d6b353`
- En cliquant sur le bouton d'aide du formulaire de login, on a accès au numéro de version de PHPMyAdmin
a savoir `3.4.10.1`

De la page d'aide on deviner quelques infos supplémentaires
- PHP version 5.2.0 minimum
- MySQL Version 5.0 minimum
- Extension ZIP de PHP

#### 2.2.2 Webmail
On va ensuite voir le webmail
sur la route `/webmail` on trouve sur la page d'accueil la version `1.4.22`

#### 2.2.3 Forum
On va ensuite voir le forum

On identifie la brique de forum: `my little forum`
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
on trouve que ce mdp appartient à lmezard sur le forum. La suite dans `writeup_lmezard.md`

Il y a aussi un formulaire de contact, un potentiel endroit a exploiter
En appuyant sur le lien `Users` on découvre que l'on peut envoyer des mails à `admin`

### 2.3 Webmail
On essaye de se connecter au webmail avec telnet.
On obtient cette banniere:
`* OK [CAPABILITY IMAP4rev1 LITERAL+ SASL-IR LOGIN-REFERRALS ID ENABLE IDLE STARTTLS LOGINDISABLED] Dovecot ready.`

En essayant de se connecter en imaps, on obtient cette information sur le certificat:
`emailAddress=root@mail.borntosec.net`

