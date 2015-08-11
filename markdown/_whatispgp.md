<!--
markdown/_whatispgpmd -> templates/generated/_whatispgp.html
!-->

<blockquote>

   <p>Pretty Good Privacy (PGP) is a data encryption and decryption computer program that provides cryptographic privacy and authentication for data communication. PGP is often used for signing, encrypting, and decrypting texts, e-mails, files, directories, and whole disk partitions and to increase the security of e-mail communications. It was created by Phil Zimmermann in 1991.</p>
   <footer>[Wikipedia](https://en.wikipedia.org/wiki/Pretty_Good_Privacy)</footer>
    
</blockquote>

PGP, or *Pretty Good Privacy*, is a system invented by Phil Zimmerman for the purpose of protecting your data and messages from being read by people you don't want. PGP allows you to encrypt (scramble) your files or messages, preventing anyone you don't want from seeing what is inside the files.

Each person has two keys, one called a 'public' key; you share this key with everyone, because this key allows people to encrypt messages.
These encrypted messages cannot be decrypted with the 'public' key, however. This is where the second key, the 'private' key comes in. This private key is used to decrypt the message that the public key was used on before.
If somebody managed to find your private key, they could decrypt and read any messages sent to you by other people. 

These public keys are stored on 'keyservers'; a list of keys and their owners. These key servers allow anybody to look up your name, download your public key, and use it to send you a message.
Your private key must never go on a key server - if it does, your data that you are protecting with these keys will be compromised.
