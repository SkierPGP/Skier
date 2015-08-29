# Skier - Security Key servIER

[![GitHub version](https://badge.fury.io/gh/SkierPGP%2FSkier.svg)](http://badge.fury.io/gh/SkierPGP%2FSkier)
[![Skier version](https://img.shields.io/badge/Skier-1.5-green.svg)](https://img.shields.io/badge/Skier-1.5-green.svg)
[![Code Climate](https://codeclimate.com/github/SkierPGP/Skier/badges/gpa.svg)](https://codeclimate.com/github/SkierPGP/Skier)

Skier is a PGP public key keyserver, built on top of the Flask microframework, designed a direct replacement for SKS.  

See Skier in action: [https://pgp.sundwarf.me](https://pgp.sundwarf.me/)

[Contributing](CONTRIBUTING.md)  
[Todo](TODO.md)


## About Skier

Skier is a keyserver for holding PGP public keys and information about them. It acts a central location for clients that use PGP as a method for encrypting data or verifying signatures.
It was made because SKS, the current major key server software, is showing its age and faults in its design. 

## Getting Skier

Skier runs in the form of Docker containers derived from specialized images. For more information on how to run Skier in production, see [Skier Docker](https://git.sundwarf.me/Skier/skier_docker)

## Development

Skier is written in Python, using Flask. This makes getting a server up very easily.

#### Requirements:
 - Python 3.2 or higher
 - Virtualenv for Python 3
 - A PostgreSQL server
 - A redis server
 - Mercurial and Git for downloading certain dependencies
 
#### Setup instructions:  
 1. **Verify sources.**  
    You need the keybase.io node client for this to work.
    
        keybase dir verify --assert github:sundwarf --assert reddit:octagonclock --assert dns:sundwarf.me
 
    This will verify the directory's contents against @SunDwarf 's keybase PGP key. 
    
 2. **Install dependencies.**  
    This step assumes you are inside a virtualenv. If you are not, please read up on virtualenvs and how to use them effectively before developing on Skier.
    
        pip install -r requirements.txt
        
    This will download and install the requirements for Skier to run, including development requirements from GitHub and Bitbucket.
    
 3. **Setup the database.**  
    Assuming you have a postgresql server running and setup, login to the server as a superuser account.
    Then run the following SQL commands:
    
        CREATE USER skier WITH PASSWORD 'yourpassword';
        CREATE DATABASE skier;
        GRANT ALL PRIVILEGES ON DATABASE skier TO skier;
        
    Next, upgrade the database to the latest migrations.
    
        ./manager.py db upgrade
        
 4. **Configure the server.**  
    The relevant sections in the server config are:  
         - The database section (`db`)  
         - The redis section (`redis`)  
         - The pool section  
        
    For typical development usage, you'll want to change the DB data and the redis information, and disable the pool functionality.
 
 5. **Generate the autotemplates.**
    
        ./setup.sh $(cwd)
 
 6. **Import some sample data.**  
    There are three ways to go about this:  
        - Add your own PGP keys, or generate some fake ones.  
        - Import keys from an SKS dump.  
        - Synch your server with the official skier servers.  
        
    The first one is the best, as you can control exactly what keys you want to put on there, and what data.
    If you import keys from an SKS dump, you get a more diverse range of keys, but you may not get exactly what you want.
    If you synch your server, it will take forever, as there are a few hundred thousand keys on the official servers. This method is dumb and should not be used.
    
 
 7. **Run the development server.**
    Assuming you set everything up correctly, you can proceed to run the development server.
    
        python3 skier.py
       
    Skier will then become visible on port 5000.
    
