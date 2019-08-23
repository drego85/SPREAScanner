# SPREA Scanner

Scanner in grado di notificare, via eMail, nuovi numeri dei propri abbonamenti digitali SPREA.

La notifica via eMail conterrà il link diretto per il download del PDF.

**Configurazione**

Il file Config.sample.py va rinominato in Config.py e compilato con i seguenti dati:
* smtp_username > eMail di autenticazione al server SMTP
* smtp_psw > password di autenticazione al server SMTP
* smtp_server > indirizzo del server SMTP
* smtp_tomail > Destinatari eMail di notifica
* smtp_from > Mittente dell'eMail di notifica 
* username > Username di accesso al portale di SPREA
* password > Password di accesso al portale di SPREA
