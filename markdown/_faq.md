### FAQ

* Q: How do I upload/recieve a key from within GnuPG?

* A: Simple! Just use `gpg --keyserver hkp://pgp.example.com --send-keys/--recv-keys <keyid>` for it to download the key. 

* Q: Does this verify that the person actually owns the key?  

* A: No.

* Q: Can I prevent people from uploading my key?

* A: No.

* Q: Somebody else uploaded a key in my name, can I get it deleted?

* A: No.

* Q: I uploaded the wrong key, can I get it deleted?

* A: No.

* Q: Somebody signed my key and I don't want it signed. Can I get rid of their signature?

* A: No.

* Q: Is there any way I can get rid of my key?

* A: If you have the private key, you can upload a key revocation certificate. This won't delete the key, but tell people who download it that the key should not be used.
