<!--
markdown/_about.md -> templates/generated/_about.html
!-->
###*Skier* is a PGP keyserver designed as a direct replacement to SKS.
Skier is compatible with any PGP client that uses the PKS endpoints used in SKS. This includes GnuPG and EnigMail.

#### Why not SKS?

A better question is why SKS?

- SKS is slow
- SKS is written in ML. What's ML? Exactly.
- SKS frontends are ugly
- SKS is monolithic
- SKS raises an error if you look at it funny

Now, just because something is old and ugly, that doesn't make it bad software. SKS isn't bad, but it's not up to date with modern technologies.
Skier uses a PostgreSQL database and a Redis cache, both modern technologies, designed to speed it up massively over SKS.
Skier's backend is designed to fetch results quickly, and only the ones needed, rather than crashing because it tries to search a file for 10,000 entries.

- SKS is slow; Skier is designed for speed, with caching and special workers.
- SKS is written in ML; Skier is written in Python, which is well-known, with many devs, and on a stable web ecosystem.
- SKS frontends are ugly; Skier uses Bootstrap 3, which fits the modern standards of a pretty website.
- SKS is monolithic; Skier is minimal, designed to glue many faster specially-designed applications together to get a working keyserver.
- SKS is error-prone; Skier will always attempt to get your result. 500 errors can and will happen, but only under exceptional circumstances.

SKS also boasts about it's 'synching' and 'pool' capabilities. This is an important functionality of a keyserver, to always be synced with other key servers. But this feature is nothing special in 2015.
Skier (as of the current version) does implement key synching. Keys are automatically synched inside a pool on boot, and keys are distributed on upload.

Skier comes inside Docker containers, which allows it to be completely isolated from the rest of the system. It also means you can put it on any random machine your computer lab has with a few commands, add a section to your nginx/apache2/whatever server, and instantly have a keyserver setup.



