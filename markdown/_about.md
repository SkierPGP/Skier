<!--
markdown/_about.md -> templates/generated/_about.html
!-->
<div class="text-center" style="font-size: xx-large">[Add]({{add_link}})/[Search]({{search_link}})</div>
###*Skier* is a GnuPG compatible key server designed as an alternative to the aging SKS.  
Skier makes no guarantee to work with other PGP implementations such as Enigmail that connect to keyservers. It also makes no guarantee to be compatible with SKS in any way other than the required routes for GnuPGP.

#### Why not SKS?

A better question is why SKS?
- SKS is slow
- SKS is written in ML, which is a functional language from *1973*
- SKS frontends are ugly
- SKS is monolithic
- SKS raises an error if you look at it funny

Now, just because something is old and ugly, that doesn't make it bad software. SKS isn't bad, but it's not up to date with modern technologies.
Some of the problems cannot be resolved because of basic computing constraints - searching for keys will always be slow, as searching a binary list is O(n).
But Skier solves some of the other problems.

- SKS is slow; Skier is designed for speed, with caching and special workers.
- SKS is written in ML; Skier is written in Python, which is well-known, with many devs, and on a stable web ecosystem.
- SKS frontends are ugly; Skier uses Bootstrap 3, which fits the modern standards of a pretty website.
- SKS is monolithic; Skier is minimal and interfaces with other applications for other purposes.
- SKS is error-prone; Skier will always attempt to get your result. 500 errors can and will happen, but only under exceptional circumstances.

SKS also boasts about it's 'syncing' and 'pool' capabilities. This is an important functionality of a keyserver, to always be synced with other key servers. But this feature is nothing special in 2015.
Skier (as of the current version) does **not** implement key syncing. This will come in a future version.
Key syncing isn't magic; it's basic use of an API. It doesn't need to be intelligent; the internet and web have come far enough that spending the few extra milliseconds making a request to every key server on upload doesn't matter as much as it did when SKS was around.

Skier comes inside Docker containers, which allows it to be completely isolated from the rest of the system. It also means you can put it on any random machine your computer lab has with a few commands, add a section to your nginx/apache2/whatever server, and instantly have a keyserver setup.



