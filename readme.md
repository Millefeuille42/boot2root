# Boot2Root

----------

!! STOP !!

If you are reading this, you are probably trying to copy our work or even worse
> "TrYinG to GeT sOme InsPiraTion"

![Actual depiction of you](figs/spongebob.gif)

Don't do this, there is multiple reasons for that:
- Seriously? Cheating?
- You are not helping yourself with that
- You are not helping the other students
- You are not helping the school, setting mediocrity as a standard
- We know where you live, and if we don't, we will find you
and we will do horendous things to your computer, like installing Windows (yuck)!
You shouldn't try us, you have been warned!

----------

Avant de commencer, faire les commandes
```
git submodule init
git submodule update
```

## La VM
ISO trouvable dans le sujet
mettre sur une VM Ubuntu 64-bits, pas besoin de disque dur
et mettre le mode de réseau de la VM en "host_only" (sur VirtualBox)

## Ajouter un tool
Faire la commande
```
git submodule add "https://github.com/sullo/nikto.git" "tools/<nom de l'outil>"
```

## Bosser
Se créer un document `writeup_<pseudo/login>.md`
Documenter TOUT dedans, les recherches, même les essais infructueux !

TODO: Faire un exploit dirtycow avec un fichier python et php