# g2b
G2B README FILE

A module for creating, accessing and maintaining GIT repositories in dropbox!
G2B implements the following functions:
-Put: Create a 'server' repository inside dropbox. 
-Clone: Clone a repository found in dropbox. The repository should have been created by G2B previously
-Push: Push changes from your local repository to the dropbox hosted repository
-Pull: Retrieve changes submitted to dropbox repository


Instructions:
First of all you should make G2B a globally callable application. In Linux run:
sudo ln -s /path/to/g2b.py /usr/local/bin/g2b
The navigate to a repository you want to upload to dropbox and run "g2b --put".
If this is your first operation in the spesific folder you will be promted to run "g2b --configure" first

You will then be able to run push and pull operations!

Do not forget to add g2b.config to .gitignore!


If two users push simultaniously (in a normal dropbox environment this would result in a corrupt repository) G2B will resolve the issue and the second user will be asked to merge the changes (if it can't be done automatically) before pushing again!

