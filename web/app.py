from pkgutil import extend_path
from urllib import request
from flask import Flask, render_template, request
import pymongo
from bson import json_util
import json

app=Flask(__name__)

myclient=pymongo.MongoClient("mongodb://localhost:27017/")
mydb=myclient["database1"]
mycol=mydb["products"]
mycol2=mydb["prices"]

List=[]# product tablosu
for x in mycol.find({},{ "_id": 0}):
    Y=json.loads(json_util.dumps(x))
    List.append(Y)

List1=[]# prices tablosu
for x in mycol2.find({},{ "_id": 0}):
    Y=json.loads(json_util.dumps(x))
    List1.append(Y)   

markalar=mycol.distinct("marka")
site=mycol.distinct("site")
isletimSistemi=mycol.distinct("isletimSistemi")
ekranBoyutu=mycol.distinct("ekranBoyutu")
diskTuru=mycol.distinct("diskTuru")
diskKapasitesi=mycol.distinct("diskKapasitesi")
bellekTuru=mycol.distinct("bellekTuru")
bellekKapasitesi=mycol.distinct("bellekKapasitesi")
islemciModeli=mycol.distinct("islemciModeli")

@app.route("/",methods=['GET','POST'])
def home():
    
    if request.method=='POST':
        list=request.form.getlist('mycheckbox')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"marka":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue 
            list.clear()  
        list=request.form.getlist('mycheckbox1')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"site":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue  
        list=request.form.getlist('mycheckbox2')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"isletimSistemi":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue  
        
        list=request.form.getlist('mycheckbox3')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"diskTuru":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue  
        
        list=request.form.getlist('mycheckbox4')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"diskKapasitesi":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue  
        
        list=request.form.getlist('mycheckbox5')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"bellekTuru":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue 
        list=request.form.getlist('mycheckbox6')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"diskTuru":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue     
        list=request.form.getlist('mycheckbox7')
        if list!=[]:
            List.clear()
            for x in list:
                try:
                    myquery={"islemci Modeli":x}
                    mydoc = mycol.find(myquery)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue                   
        if request.form.get("submit-button") == 'Fiyat Artan': 
            List2=[]
            List3=[]
            for x in List:
                try:
                    myquery={"model":x["model"]}
                    mydoc=mycol2.find(myquery)
                    List2.clear()
                    for x in mydoc:
                        List2.append(x)   
                    minPricedItem = min(List2, key=lambda x:x['fiyat'])
                    List3.append({"fiyat":minPricedItem["fiyat"],"model":minPricedItem["model"]})
                except KeyError:
                    continue
            newlist = sorted(List3, key=lambda d: float(d['fiyat'].replace('.','').replace(',','.')))
            List.clear() 
            for x in newlist:
                try:
                    myquary={"model":x["model"]}
                    mydoc=mycol.find(myquary)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue
        if request.form.get("submit-button") == 'Fiyat Azalan': 
            List2=[]
            List3=[]
            for x in List:
                try:
                    myquery={"model":x["model"]}
                    mydoc=mycol2.find(myquery)
                    List2.clear()
                    for x in mydoc:
                        List2.append(x)   
                    minPricedItem = min(List2, key=lambda x:x['fiyat'])
                    List3.append({"fiyat":minPricedItem["fiyat"],"model":minPricedItem["model"]})
                except KeyError:
                    continue
            newlist = sorted(List3, key=lambda d: float(d['fiyat'].replace('.','').replace(',','.')), reverse=True)
            List.clear() 
            for x in newlist:
                try:
                    myquary={"model":x["model"]}
                    mydoc=mycol.find(myquary)
                    for x in mydoc:
                        List.append(x)
                except KeyError:
                    continue
                
        if request.form.get("submit-button") == 'Puan Artan':
            newlist = sorted(List, key=lambda d: d['puan'])
            List.clear() 
            for x in newlist:
                List.append(x)
                
        if request.form.get("submit-button") == 'Puan Azalan':      
            newlist = sorted(List, key=lambda d: d['puan'], reverse=True)
            List.clear() 
            for x in newlist:
                List.append(x)
                
    return render_template('home.html',my_list=List,my_list1=List1,markalar=markalar,site=site,isletimSistemi=isletimSistemi,
                           bellekKapasitesi=bellekKapasitesi,bellekTuru=bellekTuru,diskKapasitesi=diskKapasitesi,diskTuru=diskTuru,islemciModeli=islemciModeli)
@app.route("/urun",methods=['GET','POST'])
def urun():
    if request.method=='POST':
        x=None
        if None!=request.form.get('click'):
            x=request.form.get('click')
        return render_template('urun.html',my_list=List,my_list1=List1,x=x)


if __name__=="__main__":
    app.debug=True
    app.run()
    
