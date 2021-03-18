import urllib
from bs4 import BeautifulSoup
import requests

kop = 1
cookie = ""

# ESKAERAK


def doGet(uria, goiburuak):

    erantzuna = requests.request('GET', uria, headers=goiburuak, allow_redirects=False)
    return erantzuna


def doPost(uria, edukia, goiburuak):

    edukia_encoded = urllib.parse.urlencode(edukia)
    goiburuak['Content-Length'] = str(len(edukia_encoded))

    erantzuna = requests.request('POST', uria, data=edukia_encoded, headers=goiburuak, allow_redirects=False)

    return erantzuna


def printeskaera(uria, metodo,datuak):
    global kop

    print("\n\n·········· "+str(kop) + '.ESKAERA' + " ··········")
    kop += 1
    print('\n\nMetodoa: ' + metodo)
    print("URIa : " + uria)
    if len(datuak)>0:
        print(" <-- Datuak --> ")
        for datua in datuak:
            print(datua + ": " + datuak[datua])


def printerantzuna(erantzuna):
    kodea = erantzuna.status_code
    deskribapena = erantzuna.reason
    print("\n~ ERANTZUNA ~")
    print("Status : "+str(kodea) + " " + deskribapena)
    print(" <-- Goiburuak --> ")
    for goiburua in erantzuna.headers:
        print(goiburua + ": " + erantzuna.headers[goiburua])
    if erantzuna.status_code == 200 and "JON GONDRA LUZURIAGA" in str(erantzuna.content):
        edukia = erantzuna.content
        print(" <-- Edukia --> ")
        print(edukia)

# MAIN


def kautotu():
    global cookie
    kautotuta = False
    datuak = ""
    goiburuak = {'Host': 'egela.ehu.eus', 'Content-Type': 'application/x-www-form-urlencoded',
                 'Content-Length': '0', "Cookie": cookie}
    uria= "https://egela.ehu.eus"

    # 1.ESKAERA (https://egela.ehu.eus) GET, 303 See Other

    uria, goiburuak = prozesatuesk(uria, datuak, goiburuak)

    # 2.ESKAERA (https://egela.ehu.eus/login/index.php) GET, 200 OK

    uria, goiburuak = prozesatuesk(uria, datuak, goiburuak)

    # 3.ESKAERA (https://egela.ehu.eus/login/index.php) POST erabiltzailea, pasahitza, 303 See Other
    # 4.ESKAERA (https://egela.ehu.eus/login/index.php?testsession=56558) POST, 303 See Other
    # 5.ESKAERA (https://egela.ehu.eus/) POST, 200 OK and "JON GONDRA LUZURIAGA" erantzunean dago
    while not kautotuta:
        printeskaera(uria, 'POST', datuak)
        erantzuna = doPost(uria, datuak, goiburuak)
        printerantzuna(erantzuna)
        kautotuta = (erantzuna.status_code == 200 and "JON GONDRA LUZURIAGA" in str(erantzuna.content))
        if erantzuna.status_code == 303:
            uria = erantzuna.headers['Location']
            print("Location : " + uria)
        if "Set-Cookie" in erantzuna.headers:
            cookie = erantzuna.headers["Set-Cookie"].split(';')[0]
            goiburuak = {'Host': 'egela.ehu.eus', 'Content-Type': 'application/x-www-form-urlencoded',
                         'Content-Length': str(len(datuak)), "Cookie": cookie}
            print("Cookie : " + cookie)
            datuak=""
        if erantzuna.status_code == 200 and "eGela UPV/EHU: Sartu gunean" in str(erantzuna.content):
            print("\n\n-------- eGela UPV/EHU: Sartu gunean --------")
            print("Gradu, Master Ofizial, Berezko Titulu eta Doktoregorako irakasgaientzako plataforma")
            print("\nErabiltzaile-izena")
            erabiltzialea = input()
            print("Pasahitza")
            pasahitza = input()
            datuak = {'username': erabiltzialea, 'password': pasahitza}
            input("SARTU")


def prozesatuesk(uria, datuak, goiburuak):
    printeskaera(uria, 'GET', datuak)
    erantzuna = doGet(uria, goiburuak)
    printerantzuna(erantzuna)
    if erantzuna.status_code == 303:
        uria = erantzuna.headers['Location']
        print("Location : " + uria)
    if "Set-Cookie" in erantzuna.headers:
        cookie = erantzuna.headers["Set-Cookie"].split(';')[0]
        print("Cookie : " + cookie)
        goiburuak["Cookie"] = cookie
    return uria, goiburuak


def irakasgaia():
    uria = "https://egela.ehu.eus/course/view.php?id=42336"
    datuak = ""
    goiburuak = {'Host': 'egela.ehu.eus', 'Content-Type': 'application/x-www-form-urlencoded',
                 'Content-Length': '0', "Cookie": cookie}
    printeskaera(uria, 'GET', datuak)
    erantzuna = doGet(uria, goiburuak)
    printerantzuna(erantzuna)
    soup = BeautifulSoup(erantzuna.content, "html.parser")
    print("\n------------- Web Sistemak -------------")
    print("\n\n Eskola magistralak eta gelako praktikak")
    print("\n*sakatu enter PDF-ak jaisteko*")
    input()
    downloadPDF(soup, goiburuak)


def downloadPDF(soup, goiburuak):
    pdf_results = soup.find_all('div', {"class": "activityinstance"})
    for pdf in pdf_results:
        if pdf.find("img", {"src": "https://egela.ehu.eus/theme/image.php/fordson/core/1611567512/f/pdf"}):
            print("\n")
            uria = str(pdf).split("onclick=\"window.open('")[1].split("\'")[0].replace("amp;", "")
            erantzuna = doGet(uria, goiburuak)
            uriapdf = erantzuna.headers['Location']
            erantzuna = doGet(uriapdf, goiburuak)
            izenapdf = uriapdf.split("mod_resource/content/")[1].split("/")[1].replace("%20", "_")
            print("Downloading "+izenapdf+" ...")
            pdfa = erantzuna.content
            print(uria)
            file = open("./pdf/" + izenapdf, "wb")
            file.write(pdfa)
            file.close()
            print(izenapdf + " downloaded !")
    print("\n\n DONE!")


if __name__ == "__main__":
    kautotu()
    print("\n\n *************** eGELA ***************")
    print("Nire ikastaroak: Martxan eta Etorkizunean")
    print("\n*sakatu enter Web Sistemak ikasgaian sartzeko*")
    input()
    irakasgaia()
