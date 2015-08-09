<!--
markdown/_about.md -> templates/generated/_about.html
!-->
<div class="text-center" style="font-size: xx-large">[Add]({{add_link}})/[Search]({{search_link}})</div>
{% include "generated/_add_panel.html" %}


###*Skier* is a GnuPG compatible key server designed as an alternative to the aging SKS.  
Skier makes no guarantee to work with other PGP implementations such as Enigmail that connect to keyservers. It also makes no guarantee to be compatible with SKS in any way other than the required routes for GnuPGP.

#### Current Key Count: {{currkeys}}

#### FAQ

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
