# gogoanime-DL
**Educational Purposes**

This app allows you to download full seasons from gogoanime.video

At the moment it will only download 1 season (plans to extend this)

**How to use**

There are two options, 

You can download the premade .exe which requires windows. This was tested on windows 10. This app will trigger false positives from antivirus software.

If you dont trust my app your free to compile yourself (I used PyInstaller). also be aware of gogoanime also triggering your antivirus as they have dodgy URLS.

Its required to have Chrome V85 (latest) installed. If the app fail it may be b/c Chrome has updated and you will need to download the latest Chromedriver.exe (32bit)

The second option is to use python 3.8 32bit this will allow you to use other operating systems like linux. Look up guides on installing python.

Once installed use pip install on requirements.txt.

**Features**

Multithreading for faster downloads, its set to 3 by default.

Chrome webbrowser based.

Automatic Plex folder structure (You just copy and paste to plex server!)

**other comments**

Report bugs on git please.
Your free to copy and edit it as you like.


**Todo list**

Add the ability to do more then 1 season.
