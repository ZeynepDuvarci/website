import requests
from bs4 import BeautifulSoup
import pymongo

myclient=pymongo.MongoClient("mongodb://localhost:27017/")
mydb=myclient["database1"]
mycol=mydb["products"]
mycol2=mydb["prices"]

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}
keys=["model","marka","isletimSistemi","islemciModeli","bellekTuru","bellekKapasitesi",
            "diskTuru","diskKapasitesi","ekranBoyutu","puan","tamAdi","islemciTipi","islemciNesli"]
dizi=["Model","Marka","İşletim Sistemi","İşlemci Modeli","Bellek Türü","Bellek Kapasitesi","Disk Türü",
                  "Disk Kapasitesi","Ekran Boyutu"]


delete = mycol.delete_many({})
delete = mycol2.delete_many({})
def duplicate(mycol, mycol2):
    # urun tablosu kontrol
    for x in mycol.find():
        i = 0
        j = 0
        for y in mycol.find():
            try:
                if x['model'] == y['model'] and x['site'] == "n11" and y['site'] == "n11":
                    i = i + 1
                if i > 1:
                    myquary = {"model": y["model"], "site": y["site"]}
                    mycol.delete_one(myquary)
                    i = 1
                if x["tamAdi"] == y["tamAdi"] and x["site"] == y["site"]:
                    j = j + 1
                if j > 1:
                    myquary = {"tamAdi": y["tamAdi"], "site": y["site"]}
                    mycol.delete_one(myquary)

                    j = 1
            except KeyError:
                continue
    # fiyat tablosu kontrolu
    for x in mycol2.find():
        i = 0
        for y in mycol2.find():
            try:
                if x["model"] == y["model"] and x["site"] == y["site"] and x["satici"] == y["satici"]:
                    i = i + 1
                if i > 1:
                    myquary = {"model": y["model"], "site": y["site"], "satici": y["satici"]}
                    mycol2.delete_one(myquary)
                    i = 1
            except KeyError:
                continue

def nearDuplicate(mycol, mycol2):
    for x in mycol.find():
        for y in mycol.find():
            try:
                if x["site"] == "n11" and y["site"] != "n11":
                    cumle = y["tamAdi"]
                    ilkdurum = len(y["tamAdi"])
                    sondurum = len(cumle.replace(x["model"], ""))
                    sondurum2 = len(cumle.replace(x["model"].swapcase(), ""))
                    if (ilkdurum - sondurum != 0) or (ilkdurum - sondurum2 != 0):
                        myquery = {"tamAdi": y["tamAdi"]}
                        newvalues = {"$set": {"model": x["model"]}}
                        mycol.update_one(myquery, newvalues)
                        myquery = {"model": y["tamAdi"]}
                        mycol2.update_one(myquery, newvalues)
                        # n11 degerleri degissin
                        myquery = {"model": x["model"]}
                        newvalues = {
                            "$set": {"islemciTipi": y["islemciTipi"], "islemciNesli": y["islemciNesli"], "site": "tam"}}
                        mycol.update_one(myquery, newvalues)

                    else:
                        myquery = {"tamAdi": y["tamAdi"]}
                        mycol.delete_one(myquery)
                        myquery = {"model": y["tamAdi"]}
                        mycol2.delete_one(myquery)
            except KeyError:
                continue
def kayitn11 (URL):
    List = []
    sayfa = requests.get(URL , headers=headers)
    icerik = BeautifulSoup(sayfa.content, 'lxml')
    List = icerik.find_all("div", {"class": "pro"})
    for urun in List:
        link=urun.find('a').get('href')
        print(link)
        sayfa = requests.get(link, headers=headers)
        icerik = BeautifulSoup(sayfa.content, 'lxml')
        L = icerik.find_all("li", {"class": "unf-prop-list-item"})
        if L!=[]:
            thisdict={}
            pricedict={}
            for ozellik in L:
                x=ozellik.find("p",{"class":"unf-prop-list-title"}).text
                y=ozellik.find("p", {"class": "unf-prop-list-prop"}).text
                for el in dizi:
                    if el==x:
                        num=dizi.index(el)
                        thisdict[keys[num]]=y.lstrip()

                    if x=="Model":
                        pricedict["model"] = y.lstrip()

            pricedict["site"] = "n11"
            pricedict["satici"] = icerik.find("a", {"class": "unf-p-seller-name"}).text
            thisdict[keys[9]] =icerik.find("strong", {"class", "ratingScore"}).text
            pricedict["fiyat"]=icerik.find("div", {"class": "unf-p-summary-price"}).text
            pricedict["link"]=link
            thisdict[keys[10]] = icerik.find("h1", {"class": "proName"}).text.rstrip().lstrip()
            foto=icerik.find("div",{"class":"imgObj"})
            foto=foto.find('a').get('href')
            thisdict["image"]=foto
            thisdict[keys[11]] = None
            thisdict[keys[12]] = None
            thisdict["site"]="n11"
            mycol.insert_one(thisdict)
            mycol2.insert_one(pricedict)
            del thisdict
            del pricedict

URL = 'https://www.n11.com/bilgisayar/dizustu-bilgisayar'
for i in range(2,21):
    if i != 6 and i != 7 and i != 8:
        kayitn11(URL+"?pg="+str(i))

#trendyol
URL = 'https://www.trendyol.com/laptop-x-c103108'
sayfa = requests.get(URL, headers=headers)
icerik = BeautifulSoup(sayfa.content, 'lxml')
List = icerik.find_all("div", {"class": "p-card-chldrn-cntnr card-border"})
i = 0
for j in range(2, 20):
    for link in List:
        thisdict = {}
        pricedict = {}
        Url = link.find('a').get('href')
        Url = 'https://www.trendyol.com' + Url
        sayfa = requests.get(Url, headers=headers)
        icerik = BeautifulSoup(sayfa.content, 'lxml')
        marka = icerik.find("h1", {"class": "pr-new-br"}).a.text
        thisdict[keys[1]]=marka
        L = icerik.find("ul", {"class": "detail-attr-container"}).find_all("li")
        sayac = 0
        for urun in L:
            b = urun.find("span").text
            c = urun.find("b").text
            if b == "İşletim Sistemi":
                thisdict[keys[2]]=c
            if b == "İşlemci Tipi":
                thisdict[keys[11]]=c
            if b == "İşlemci Nesli":
                thisdict[keys[12]]=c
            if b == "Ram (Sistem Belleği)":
                thisdict[keys[4]] = "RAM"
                thisdict[keys[5]] = c
            if b == "Ekran Boyutu":
                thisdict[keys[8]]=c
            if b == "SSD Kapasitesi" and (c != "Yok" or c != "SSD Yok"):
                thisdict[keys[6]] = "SSD"
                thisdict[keys[7]] = c
            if (b == "Hard Disk Kapasitesi" and c != "HDD Yok"):
                if (c != "Yok"):
                    thisdict[keys[6]] = "HDD"
                    thisdict[keys[7]] = c
            if (b == "SSD Kapasitesi" and (c == "SSD Yok" or c == "Yok")) or (
                    b == "HDD Kapasitesi" and (c == "Yok" or c == "HDD Yok")):
                sayac = sayac + 1

        if sayac != 2:
            print("Geçerli kayıt")
            thisdict[keys[0]]=None
            thisdict[keys[9]] = None
            thisdict["site"]="trendyol"
            pricedict["fiyat"]=icerik.find("span", {"class": "prc-dsc"}).text
            pricedict["site"]="trendyol"
            ad=icerik.find("h1",{"class":"pr-new-br"})
            ad=ad.find("span").text
            thisdict[keys[10]]=ad
            thisdict["model"]=ad
            pricedict["model"]=ad
            satici=icerik.find("div",{"class":"merchant-box-wrapper"})
            if satici != None :
                satici=satici.find("a").text
                pricedict["satici"]=satici
            else:
                pricedict["satici"] = None
            link=link.find('a').get('href')
            link = 'https://www.trendyol.com' + link
            pricedict["link"]=link
            print(link)
            image=icerik.find("img",{"class":"detail-section-img"}).get("src")
            thisdict["image"]=image
            mycol.insert_one(thisdict)
            mycol2.insert_one(pricedict)

    List.clear()
    URL = URL + "?pi" + str(j)
    sayfa = requests.get(URL, headers=headers)
    icerik = BeautifulSoup(sayfa.content, 'lxml')
    List = icerik.find_all("div", {"class": "p-card-chldrn-cntnr card-border"})
#vatan
for vsayfa in range(1,12):
    url="https://www.vatanbilgisayar.com/notebook/?page={}".format(vsayfa)
    v_r=requests.get(url,headers=headers)
    v_soup = BeautifulSoup(v_r.content,"lxml")
    veri = v_soup.find("div",attrs={"class":"wrapper-product wrapper-product--list-page clearfix"})\
        .find_all("div",attrs={"class":"product-list product-list--list-page"})

    for m in veri:
        thisdict = {}
        pricedict = {}
        vtamad=m.find("div",attrs={"class":"product-list__content"}).find("a",attrs={"class":"product-list__link"})\
        .find("div",attrs={"class":"product-list__product-name"}).text.strip()
        thisdict["tamAdi"]=vtamad
        vlink_basi="https://www.vatanbilgisayar.com"
        vlink_sonu=m.a.get("href")
        vlink=vlink_basi+vlink_sonu
        pricedict["link"]=vlink
        print(vlink)
        vr1 = requests.get(vlink, headers=headers)
        vsoup1 = BeautifulSoup(vr1.content, "lxml")
        vfiyat=m.find("div",attrs={"class":"product-list__content"}).find("div",attrs={"class":"product-list__cost"})\
        .find("span",attrs={"class":"product-list__price"}).text.strip()
        pricedict["fiyat"]=vfiyat
        pricedict["satici"]="vatan"
        vpuan=vsoup1.find("strong",attrs={"id":"averageRankNum"}).text
        thisdict["puan"]=vpuan
        vdizi=str(vtamad).split()
        vmarka=vdizi[0]
        thisdict["marka"]=vmarka
        thisdict["site"]="vatan"
        pricedict["site"]="vatan"
        vresim= vsoup1.find("div",attrs={"class":"swiper-slide"})
        vresim=vresim.get("data-img")
        thisdict["image"]=vresim
        thisdict["model"]=vtamad
        pricedict["model"]=vtamad
        List=vsoup1.find_all("table",{"class":"product-table"})
        thisdict["islemciModeli"]=None
        islemciTipi=""
        for n in List:
            a=n.find_all("tr")
            for b in a:
                degisken=b.find("td").text
                deger=b.find("p").text
                if degisken=="İşlemci Markası":
                    if islemciTipi=="":
                        islemciTipi=islemciTipi+deger
                if degisken=="İşlemci Teknolojisi":
                    if islemciTipi!="":
                        islemciTipi=islemciTipi+deger
                if degisken == "İşlemci Nesli":
                    thisdict["islemciNesli"]=deger
                if degisken =="İşletim Sistemi":
                    thisdict["isletimSistemi"]=deger
                if degisken=="Ekran Boyutu":
                    thisdict["ekranBoyutu"]=deger
                if degisken =="Ram Tipi":
                    thisdict["bellekTuru"]=deger
                if degisken =="Ram (Sistem Belleği)":
                    thisdict["bellekKapasitesi"]=deger
                if degisken =="Disk Türü":
                    thisdict["diskTuru"]=deger
                if degisken=="Disk Kapasitesi":
                    thisdict["diskKapasitesi"]=deger
            thisdict["islemciTipi"]=islemciTipi
        mycol.insert_one(thisdict)
        mycol2.insert_one(pricedict)

for hx in range(2,15):
    hurl="https://www.hepsiburada.com/laptop-notebook-dizustu-bilgisayarlar-c-98?filtreler=harddiskkapasitesi1:Yok&sayfa="+str(hx)
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}
    h_r=requests.get(hurl,headers=headers)
    h_soup = BeautifulSoup(h_r.content,"lxml")
    hst1=h_soup.find("div",attrs={"class":"productListContent-pXUkO4iHa51o_17CBibU"}).find("ul",attrs={"class":"productListContent-frGrtf5XrVXRwJ05HUfU productListContent-rEYj2_8SETJUeqNhyzSm"})
    hst2=hst1.find_all("li",attrs={"class":"productListContent-zAP0Y5msy8OHn5z7T_K_"})
    for hdetaylar in hst2:
        thisdict = {}
        pricedict = {}
        hlink_sonu=hdetaylar.a.get("href")
        hlink_basi="https://www.hepsiburada.com"
        hlink=hlink_basi+hlink_sonu
        print(hlink)
        pricedict["link"]=hlink
        hr1 = requests.get(hlink, headers=headers)
        hsoup1 = BeautifulSoup(hr1.content, "lxml")
        hfiyat = hsoup1.find("span", attrs={"data-bind": "markupText:'currentPriceBeforePoint'"}).text
        pricedict["fiyat"]=hfiyat
        htamismi = hsoup1.find("span", attrs={"class": "product-name"}).text
        thisdict["tamAdi"]=htamismi
        hsatici=hsoup1.find("a",attrs={"data-bind":"text: product().currentListing.merchantName, attr: { href: product().currentListing.isHepsiburadaProduct ? 'javascript:;' : product().currentListing.merchantPageUrl, 'data-hbus': userInformation() && userInformation().userId && isEventReady() ? productDetailHbus('GoToSellerClick' ): ''}, css: {hepsiburada: product().currentListing.isHepsiburadaProduct}"}).text.strip()
        pricedict["satici"]=hsatici
        hmarka = hsoup1.find("span", attrs={"class": "brand-name"}).text.strip()
        thisdict["marka"]=hmarka
        hresim = hsoup1.img.get("src")
        thisdict["image"]=hresim
        thisdict["site"]="hepsiburada"
        pricedict["site"]="hepsiburada"
        pricedict["model"]=htamismi
        thisdict["model"]=htamismi
        thisdict["puan"]=None
        thisdict["islemciModeli"]=None
        urun=hsoup1.find("table",{"class":"data-list tech-spec"})
        List=urun.find_all("tr")
        for n in List:
            a=n.find("th").text.strip()
            b=n.find("td").text.strip()
            if a=="İşlemci Tipi":
                thisdict["islemciTipi"]=b
            if a=="İşlemci Nesli":
                thisdict["islemciNesli"]=b
            if a=="İşletim Sistemi":
                thisdict["isletimSistemi"]=b
            if a=="Ekran Boyutu":
                thisdict["ekranBoyutu"]=b
            if a=="SSD Kapasitesi":
                thisdict["diskTuru"]="SSD"
                thisdict["diskKapasitesi"]=b
            if a=="Ram Tipi":
                thisdict["bellekTuru"]=b
            if a=="Ram (Sistem Belleği)":
                thisdict["bellekKapasitesi"]=b

        mycol.insert_one(thisdict)
        mycol2.insert_one(pricedict)
