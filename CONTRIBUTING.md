# Contributing to Skier

You want to contribute to Skier? That's great! But before you do, please review the List of Things Not To Do:

 - Add in a new feature that you think is 'cool' just because you think it's 'cool'
 - Add something in that pulls in more dependencies (unless it's absolutely essential)
 - Make another way of running Skier that isn't gunicorn based (hint: it's always going to be gunicorn based)
 - Write code that depends on GnuPG or other GPG implementations.
 - Write code that is there for the sole purpose of interfacing with PKS applications.
 - Write a [Keybase](https://keybase.io) integrator
 - Write code that works around a hacky thing in pgpdump or the likes
 
Your idea doesn't fit in with these? That's also great! But before you click that fork button, please review the List of Things To Do:

 - Comment your code thoroughly
 - Write docstrings for any functions intended to be called inside the application
 - Make sure your code is fast, abusing the redis cache and database if possible
 - Write a [Keybase](https://keybase.io) integrator
 - Make sure your changes don't break: The API, the PKS api, the frontend
 - If writing frontend HTML/Markdown, it fits with Bootstrap 3 and the general theme
 
If your code doesn't fit these guidelines, your pull requests will probably be rejected.

Otherwise, click that big 'fork' button up top.

