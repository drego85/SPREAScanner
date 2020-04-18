#!/usr/bin/python3
import re
import sys
import Config
import logging
import urllib3
import requests
import smtplib
from datetime import datetime
from bs4 import BeautifulSoup

headerdesktop = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:62.0) Gecko/20100101 Firefox/62.0",
                 "Accept-Language": "it,en-US;q=0.7,en;q=0.3",
                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                 "Content-Type": "application/x-www-form-urlencoded",
                 "DNT": "1",
                 "Connection": "keep-alive",
                 "Upgrade-Insecure-Requests": "1",
                 "Pragma": "no-cache",
                 "Cache-Control": "no-cache",
                 "TE": "Trailers"}
timeoutconnection = 10

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Inizializzo i LOG
logging.basicConfig(filename="sprea.log",
                    format="%(asctime)s - %(funcName)10s():%(lineno)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

hashrivisteindiviuateList = []


def load_hash_analizzati():
    try:
        f = open("sprea_hash_rilevati.txt", "r", errors="ignore")

        for line in f:
            if line:
                line = line.rstrip()
                hashrivisteindiviuateList.append(line)

        f.close()

    except IOError as e:
        logging.error(e, exc_info=True)
        sys.exit()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise


def save_hash_analizzati(hash):
    try:
        f = open("sprea_hash_rilevati.txt", "a")
        f.write(str(hash) + "\n")
        f.close()
    except IOError as e:
        logging.error(e, exc_info=True)
        sys.exit()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise


def send_email(pdfurl):
    try:
        username = Config.smtp_username
        password = Config.smtp_psw
        smtpserver = smtplib.SMTP(Config.smtp_server, 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        # smtpserver.ehlo() # extra characters to permit edit
        smtpserver.login(username, password)

        header = "From: " + Config.smtp_username + "\r\n"
        header += "To: " + ", ".join(Config.smtp_toaddrs) + "\r\n"
        header += "Subject: SPREA Scanner Nuova Rivista Individuata \r\n"
        header += "Date: " + datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S -0000") + "\r\n\r\n"

        msg = header + "Nuova rivista individuata\n\n"
        msg = msg + "Download PDF: " + pdfurl
        msg = msg + "\n\n"

        smtpserver.sendmail(Config.smtp_username, Config.smtp_toaddrs, msg.encode("utf-8"))

        smtpserver.quit()
    except Exception as e:
        logging.error(e, exc_info=True)
        pass


def main():
    # Carico la lista delle riviste già notificate
    load_hash_analizzati()

    abbonamentiList = []
    rivisteList = []

    # Apro una sessione per autenticarmi sul sito di sprea.it
    session = requests.Session()
    url2 = "https://sprea.it/login"
    usersprea = {"user": Config.username, "password": Config.password}

    session.post(url2, data=usersprea, headers=headerdesktop, timeout=timeoutconnection)
    cookie = session.cookies.get_dict()

    # Accedo alla pagina degli Abbonamenti Digitalia acquistati dall'utente
    url3 = "https://sprea.it/digitali"
    page = requests.get(url3, cookies=cookie, headers=headerdesktop, timeout=timeoutconnection)
    soup = BeautifulSoup(page.text, "html.parser")

    for div in soup.find_all("div", attrs={"class": "col-lg-3 col-md-4 col-xs-6"}):
        for link in div.find_all("a"):
            if "digitali" in link.get("href"):
                abbonamentiList.append("https://sprea.it" + link.get("href"))

    # Per ogni abbonamento rilevato identificato i numeri disponibili e il nome del file PDF
    for urlabbonamento in abbonamentiList:
        page = requests.get(urlabbonamento, cookies=cookie, headers=headerdesktop, timeout=timeoutconnection)
        soup = BeautifulSoup(page.text, "html.parser")

        for div in soup.find_all("div", attrs={"class": ["col-md-4", "col-xs-6"]}):
            for link in div.find_all("a"):
                pdfhash = re.findall(r"[a-zA-Z0-9]{40}\.pdf", link.get("href"))[0]
                rivisteList.append(pdfhash)

    # Analizzo ogni rivista individuata e notifico le eventuali nuovi riviste
    for pdfhash in rivisteList:
        if pdfhash not in hashrivisteindiviuateList:
            logging.info("Nuova rivista identificata: %s" % pdfhash)

            # URL Download PDF
            pdfurl = "http://pdf.sprea.it/r/php/pdf_2/%s" % pdfhash

            # Invio la notifica via eMail
            send_email(pdfurl)

            # Salvo la lista notifica
            hashrivisteindiviuateList.append(pdfhash)
            save_hash_analizzati(pdfhash)


if __name__ == "__main__":
    main()
