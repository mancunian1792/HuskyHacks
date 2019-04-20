from flask import Flask, request, jsonify
import os, uuid, json
import io
from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account
from dateutil.parser import parse
from natty import DateParser
from google.cloud import translate
import zxing
import datefinder
import time,datetime
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
    import Features, EntitiesOptions, KeywordsOptions

app = Flask(__name__)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        filename = os.path.splitext(file.filename)[0]
        ts = time.time()
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')
        f_name = str(filename + "_" + time_stamp) + extension
        file.save(os.path.join("/home/ubuntu/", f_name))
        out = detect_text("/home/ubuntu/"+f_name)
        print(out)
       # return jsonify({'json':out})
        return jsonify(out)

def detect_text(path):
    credentials=service_account.Credentials.from_service_account_file('/home/ubuntu/key.json')
    client = vision.ImageAnnotatorClient(credentials=credentials)
    date=""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    a=texts[0].description.split("\n")
    if texts[0].locale is "en":
        name=a[0]+" "+a[1]
        des=getdescription(a)
    else:
        des=""
        v=list(language_converter(a[0]).values())
        k=''.join(v)
        o=list(language_converter(a[1]).values())
        p=''.join(o)
        name=k+" "+p
    place=None
    x=None
    count=0
    qr_exist,qr_link=qrcode(path)
    #print(des)
    for i in a:
        count=count+1

        if texts[0].locale is not "en":
            i=list(language_converter(i).values())
            i=i[0]

        if count >=2:
            des=des+" "+i
        c=remove_delimiters(i)
        #print(c)
        #print(x,y)
        if x is None:
            #print("yo")
            x=is_date(c)
            #date=x.strftime('%Y-%m-%d')
        if place is None:
            place=location(i)
    words=get_keywords(des)
    js =  { "name":name, "description":des, "created_date":x.strftime('%Y-%m-%d'),"location":place,"is_qr": qr_exist,"qr_url":qr_link,"category":words}
    return js

def getdescription(n):
    g=n[2:]
    return ' '.join(g)

def remove_delimiters(r):
    k=[","]
    for i in k:
        r=r.replace(i," ")
    return r

def location(t):
    t=t.lower()
    loc=["10 Coventry Street","142 Hemenway St","144 Hemenway St","146 Hemenway St","BK","148 Hemenway St","177 Huntington Ave","271 Huntington","319 Huntington","335 Huntington Ave","337 Huntington Ave","407 Huntington Ave","Asian American Center","Badger-Rosen SquashBusters Center","Barletta Natatorium","Behrakis Health Sciences Center","Blackman Auditorium","Burlington Campus","Burstein Hall","Cabot Physical Education Center","Cahners Hall","Cargill Hall","Catholic Center","Charlotte Campus","Churchill Hall","Columbus Place and Alumni Center","Curry Student Center","Dana Research Center","Davenport Commons A","Davenport Commons B","Dockser Hall","Dodge Hall","East Village","Ell Hall","Fenway Center","Forsyth Building","Hastings Hall","Hayden Hall","Kariotis Hall","Kennedy Hall","Knowles Center","Kerr Hall","ISEC","ISEC 142","Marino Recreation Center","Light Hall","Marino Recreation Center","Matthews Arena","Meserve Hall","Nightingale Hall","Richards Hall","Robinson Hall","Rubenstein Hall","ROTC Office","Ryder Hall","Seattle Campus","Shillman Hall","Shillman","Hastings","Smith Hall","Snell Engineering Center","West Village G","West Village H"]
    for i in loc:
        i=i.lower()
        if i in t:
            return i
def qrcode(path):
    reader = zxing.BarCodeReader()
    barcode = reader.decode(path)
    if barcode is None:
        boo=False
        link="Does not exist"
    else:
        boo=True
        link=barcode.raw
    return boo,link

def is_date(string):
    #date=None
    try:
        matches = datefinder.find_dates(string)
        third = next(matches)
        #print("I am here")
    except StopIteration:
        third = None
    #print(date)
    return third

def language_converter(i):
    credentials=service_account.Credentials.from_service_account_file('/home/ubuntu/key.json')
    translate_client = translate.Client(credentials=credentials)
    text = i
    target = 'en'
    translation = translate_client.translate(text,target_language=target)
    return translation

def get_keywords(i):
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey="xNNHsjSVkGoSPSTZLfpmUOs62WUdzRj3JaYAxzkO9jEa",
        url='https://gateway.watsonplatform.net/natural-language-understanding/api'
    )
    response = natural_language_understanding.analyze(
        text=i,
        features=Features(
            entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),keywords=KeywordsOptions(emotion=True, sentiment=True,limit=2))).get_result()
    #print(response.get('keywords'))
    #a=json.loads(response, indent=2)
    #print(type(response))
    cat = []
    for item in response.get('keywords'):
        if(item != None):
            for txt in item.get('text').split(' '):
                cat.append(txt)
    return ",".join(cat)

if __name__ == "__main__":
    app.run(debug=True)
