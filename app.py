from flask import Flask, render_template, request, jsonify, redirect, url_for
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime

import pymongo
from pymongo import DESCENDING
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import json

import string
import random

import os

from bson.json_util import dumps


# Türkiye Saati'ni belirtmek için timezone objesi oluşturulur
import pytz # turkiye saatiyle kayitlari eklemek icin
turkey_tz = pytz.timezone('Europe/Istanbul')

# .env dosyasının varlığını kontrol edin ve yükleyin
if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    
# 'DATABASE_URL' anahtarına karşılık gelen değeri alın
uri = os.getenv('DATABASE_URL')
secret = os.getenv('SECRETKEY')


# ENV degisken ekle
# uri = "mongodb+srv://===:====@clusterkredi.ryzdktr.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.otovitrin
customers = db.musteriler       # proje ilk basladiginda musteri uzerinden gitmistim. bu nedenle kredi dosyalari customers databaseinde
users_collection = db.users     # hem web sitesi kullanicilarini hemde galerileri tutar
selected_customers = db.selected_customers  # masa ustu uygulamasinda personelin secili dosyasinin bilgilerini almasini saglar
harcamalar_db = db.harcamalar

hazir_veriler = client["form_hazir_verileri"]   # vergi daireleri, iller, ilceler ve arac modelleri bu collectionda
modellerDb = hazir_veriler["modeller"]          # ilk sutun integer. sonrakiler string
il_ilce_tb = hazir_veriler["il_ilce"]           # il ve ilce select boxlarinda kullanmak icin.
vergi_daire_il_ilceler = hazir_veriler["vergi_daireleri"]


app = Flask(__name__)
app.secret_key = secret


# Index sayfasi
@app.route('/')
@login_required
def index():
    # index.html adlı template'i döndür
    return render_template('index.html')

@app.route('/destek')
@login_required
def destek():

    metadata = {
        'sayfa_baslik': 'Yardım Sayfası'
    }

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
    }
    
    return render_template('destek.html', metadata=metadata, user_data=user_data)

# Index sayfasi
@app.route('/harcamalar')
@login_required
def harcamalar():

    # Sayfa numarasını al
    page = int(request.args.get('page', 1))
    # Her sayfada kaç harcama gösterileceğini belirle
    per_page = int(request.args.get('per_page', 10))

    # Toplam harcama sayısını al
    total_customers = harcamalar_db.count_documents({})

    # Pagination hesaplamaları
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_customers)

    # harcamaleri veritabanından getir
    harcamalar_list = list(harcamalar_db.find({}, {'_id':1, 'harcama_tarihi':1, 'il_secimi_harcama':1, 'harcama_aciklamasi':1, 'tutar':1 }).sort("_id", -1).skip(start_index).limit(per_page))

    
    # Pagination metadatasını oluştur
    metadata = {
        'page': page,
        'per_page': per_page,
        'total_customers': total_customers,
        'total_pages': int(total_customers / per_page) + 1,
        'sayfa_baslik': 'Harcamalar'
    }

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
    }
    
    return render_template('harcamalar.html', data=harcamalar_list , metadata=metadata, user_data=user_data)

# Index sayfasi
@app.route('/iletisim')
@login_required
def iletisim():

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
    }
    
    
    return render_template('iletisim.html', user_data=user_data)

# Index sayfasi
@app.route('/hesabim')
@login_required
def hesabim():

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
    }
    
    
    return render_template('hesabim.html', user_data=user_data)

# Index sayfasi
@app.route('/userlist')
@login_required
def userlist():
    
    # Sayfa numarasını al
    page = int(request.args.get('page', 1))
    # Her sayfada kaç müşteri gösterileceğini belirle
    per_page = int(request.args.get('per_page', 10))

    # Toplam müşteri sayısını al
    total_customers = users_collection.count_documents({})

    # Pagination hesaplamaları
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_customers)

    # Müşterileri veritabanından getir
    customer_list = list(users_collection.find({}, {'_id':1, 'isim_soyisim':1, 'gallery_name':1, 'city':1, 'district':1, 'username':1, 'yetki':1 }).sort("_id", -1).skip(start_index).limit(per_page))

    
    # Pagination metadatasını oluştur
    metadata = {
        'page': page,
        'per_page': per_page,
        'total_customers': total_customers,
        'total_pages': int(total_customers / per_page) + 1,
        'sayfa_baslik': 'Kullanıcılar'
    }

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
    }
    
    return render_template('userlist.html', data=customer_list , metadata=metadata, user_data=user_data)

# İstatistik Veriler sayfasi
@app.route('/istatistik')
@login_required
def istatistik():

    
    # Pagination metadatasını oluştur
    metadata = {
      
        'sayfa_baslik': 'İstatistik'
    }

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
    }
    
    return render_template('istatistik.html', metadata=metadata, user_data=user_data)


# Yeni Kredi Dosyası Ekle
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        
        data = request.json
        
        # galeri kontrolu yap. eğer yoksa yeni kullanıcı ekle
        galeri_telefonu = request.json.get('galeri_telefonu')
        existing_user = users_collection.find_one({'username': galeri_telefonu})
        if existing_user:
            print('Bu galeri adı zaten kullanılıyor. ')
        else:
            username = galeri_telefonu
            password = str(random.randint(100000, 999999))
            gallery_name = request.json.get('galeri_adi')
            city = request.json.get('galeri_ili')
            
            # Şifreyi hashleyin, kullanıcıyı veritabanına kaydedin ve otomatik olarak giriş yapın
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({'username': username, 'password': hashed_password, 'gallery_name': gallery_name, 'city': city, 'district': '', 'yetki': 'Oto Galeri', 'address': '', 'isim_soyisim':''})


        ## marka ve model bilgisi kasko kodundan alinarak db'ye eklenir
        # form gonderildiginde kasko kodu ve model yili verisiyle arac marka modeli getirilir
        kasko_kodu = str(request.json.get('kaskokodu'))
        model_yili = int(request.json.get('model_yili'))

        if model_yili and kasko_kodu is not None:
            # Veritabanından model yılına ait araci çek
            arac_kasko_bedel = modellerDb.find_one({
                                            "Model yılı": model_yili,
                                            "Kasko Kodu": kasko_kodu
                                            })
            
        if arac_kasko_bedel is not None:
            data["marka_adi"] = arac_kasko_bedel['Marka']
            data["tip_adi"] = arac_kasko_bedel['Model']

        # musteriyi ekleyen kullanıcının cep telefonu. unique dir ekle
        data['created_by'] = current_user.id
        data['created_by_isim'] = current_user.isim_soyisim
        

        # eger dokuman id baska bir dokumanda varsa bilgileri gunceller. not kelimesi dikkat
        dosya_id=request.json.get('dosya_id')
        if not (dosya_id=='' or dosya_id == "yeni"):
            # Veritabanından model yılına ait markai çek
            kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})
            
            # JSON formatında modelleri döndür
            if kayitli_dosya_bilgisi:
                #alttaki degerler bosluk ve gereksiz degerler guncellenmemesi icin jsondan kaldir
                del data["dosya_id"]
                del data["dosya_numarasi"]

                dataGuncelle = {
                    'inputValue': 'Dosya guncellendi',
                    'created_by': current_user.id,
                    'isim_soyisim': current_user.isim_soyisim,
                    'status': 'otomatik',   # success  pending  failed
                    'created_time': datetime.now(),
                }

                data['guncellemeler'] = kayitli_dosya_bilgisi['guncellemeler']

                data["guncellemeler"].append(dataGuncelle)

                new_data = {
                    "$set": data
                }
                
                result = customers.update_one({"_id": ObjectId(dosya_id)}, new_data)
                
                return jsonify({'message': 'Form kaydedildi'}), 200

        if "dosya_id" in data:
            del data["dosya_id"]

        # eger dosya daha onceden yoksa ve İLK DEFA BİR DOSYA OLUŞTURULUyorsa
        data['created_time'] = datetime.now(turkey_tz)

        data['status'] = 'Devam'   # surec sayfasindaki renkli butonlar

        # Rastgele 5 haneli büyük harf, rakam ve tirelerden oluşan benzersiz bir dizi oluşturuyoruz.
        dosya_numarasi = ''.join(random.choices(string.ascii_uppercase + string.digits + '-', k=5))

        # Benzersiz dosya numarasi daha önce kullanılmış mı diye kontrol ediyoruz.
        while customers.find_one({"dosya_numarasi": dosya_numarasi}) is not None:
            dosya_numarasi = ''.join(random.choices(string.ascii_uppercase + string.digits + '-', k=5))

        # benzersiz dosya numarasi eklenir
        data['dosya_numarasi'] = dosya_numarasi

        dataGuncelle = {
            'inputValue': 'Dosya oluşturuldu.',
            'created_by': current_user.id,
            'isim_soyisim': current_user.isim_soyisim,
            'status': 'otomatik',   # success  pending  failed
            'created_time': datetime.now(),
        }

        # yeni yaratildigi icin
        data['guncellemeler'] = []
        
        data["guncellemeler"].append(dataGuncelle)

        # Database kayıt işlemi
        result = customers.insert_one(data)

        document_id = result.inserted_id
        print(f"_id of inserted document {document_id}")

        # Başarılı bir şekilde kaydedildi sayfasını göster
        return jsonify({'message': 'Form kaydedildi','dosya_id': str(document_id)}), 200
        
    return jsonify({'message': 'Form gonderilmedi'}), 401


# Ozet sayfası
@app.route('/dashboard')
@login_required
def dashboard():
   
    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
    }
    
    metadata ={
        'sayfa_baslik': 'Özet'
    }
    # Template'e JSON verisini gönderin
    return render_template("dashboard.html", user_data=user_data, metadata=metadata)


# GET isteği ile müşterileri pagination ile getirme
@app.route('/basvurular', methods=['GET'])
@login_required
def get_basvurular():
    # Sayfa numarasını al
    page = int(request.args.get('page', 1))
    # Her sayfada kaç müşteri gösterileceğini belirle
    per_page = int(request.args.get('per_page', 10))

    # İl seçimini al
    selected_city = request.args.get('city')

    # Durum seçimini al
    dosya_durumu = request.args.get('durum')

    query = {}

    if selected_city and selected_city != 'Tüm':
        query['galeri_ili'] = selected_city

    if dosya_durumu and dosya_durumu != 'Hepsi':
        query['status'] = dosya_durumu

    # Get total number of customers with the specified filters
    total_customers = customers.count_documents(query)

    # Get customers from the database with the specified filters
    customer_list = list(customers.find(query, {'_id': 1, 'adi': 1, 'soyadi': 1, 'dosya_numarasi': 1, 'galeri_ili': 1, 'galeri_adi': 1, 'kredi_tutari': 1, 'kredi_vadesi': 1, 'calisma_sekli': 1, 'kredi_miktar': 1, 'kredi_vadesi': 1, 'created_time': 1, 'musteri_cep_telefonu': 1, 'model_yili': 1, 'marka_adi': 1, 'tip_adi': 1, 'created_by_isim': 1, 'status': 1}).sort("created_time", -1))

    # Sayfa numarasını al
    page = int(request.args.get('page', 1))
    # Her sayfada kaç müşteri gösterileceğini belirle
    per_page = int(request.args.get('per_page', 10))

    # Pagination hesaplamaları
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_customers)

    # Müşterileri pagination ile sınırlandır
    customer_list = customer_list[start_index:end_index]

    # Pagination metadatasını oluştur
    metadata = {
        'page': page,
        'per_page': per_page,
        'total_customers': total_customers,
        'total_pages': int(total_customers / per_page) + 1,
        'city': selected_city,
        'durum': dosya_durumu,
        'sayfa_baslik': 'Kredi Başvuru Dosyaları'
    }

    # secim yapilmis musteri dokumanini kullaniclara gore getirir. bu secim masaustu uygulamasi icin referanstir
    # eger bu kullanici icin secim yapima collectionunda bir dokuman varsa bul getir
    query = {"current_user": current_user.id }
    existing_doc = selected_customers.find_one(query)

    if existing_doc:
        # Doküman mevcut, secili musteri dosya bilgisini getirir
        lstest_customer_id = existing_doc["customer_id"]
    else:
        lstest_customer_id = '0'

    user_data = {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
    }

    return render_template('basvurular.html', data=customer_list , metadata=metadata, lstest_customer_id=lstest_customer_id, user_data=user_data)

#kullanici secimi ekle
@app.route('/add_customer_selection', methods=['POST'])
@login_required
def add_customer_selection():

    # İstekten gelen JSON verilerini al
    data = request.get_json()
    customer_id = data['customer_id']    # secilen musterinin id'si
    selection_date = datetime.now(turkey_tz)

    current_user_id = current_user.id       # secimi yapan kullanicinin cep telefonu. idsi

    # dokumanda mevcut kullanicinin baska bir kaydi varsa al
    query = {'current_user': current_user_id}
    existing_doc = selected_customers.find_one(query)

    if existing_doc:
        # Doküman mevcut, güncelleme yapılabilir
        existing_doc["customer_id"] = customer_id
        existing_doc["selection_date"] = selection_date
        result = selected_customers.replace_one(query, existing_doc)
    else:
        # Doküman yok, yeni bir öge oluşturulabilir
        # Seçilen müşteriyi selected_customers koleksiyonuna ekle
        result = selected_customers.insert_one({
            'current_user': current_user_id,
            'customer_id': customer_id,
            'selection_date': selection_date
        })

    return jsonify(str(result))

# secili musteri getir. masa ustu uygulamasi icin cep telefonu gonderilen kullaninicnin secili musteri bilgileri gonderilir
@app.route('/secili_musteri/<string:parametre>', methods=['GET'])
def last_selected_customer(parametre):
    
    # Son seçilen müşterinin bilgilerini al
    secili_dosya = selected_customers.find_one({'current_user': parametre})
    if secili_dosya:
        customer_id = str(secili_dosya['customer_id'])  # ObjectId to str

        # Müşteri bilgilerini veritabanından al
        customer = customers.find_one({'_id': ObjectId(customer_id)})
        
        if customer is None:
            return jsonify({'message': 'Müşteri bulunamadı.', 'id': customer_id}), 404

        # Convert ObjectId to string
        customer['_id'] = str(customer['_id'])
        del customer['guncellemeler']
        del customer['status']
        del customer['_id']

        return jsonify(customer), 200
    
    return {'Hata':'hatali paralo'}, 200
    


###### LOGIN BAS ##############

# Flask-Login'in başlatılması
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Kullanıcı model sınıfının oluşturulması
class User(UserMixin):
    def __init__(self, username, password, gallery_name, city, district, address, isim_soyisim, yetki):
        self.id = username
        self.password = password
        self.gallery_name = gallery_name
        self.city = city
        self.district = district
        self.address = address
        self.isim_soyisim = isim_soyisim
        self.yetki = yetki

    def __repr__(self):
        return f'<User {self.id}>'


# Kullanıcıları veritabanından getirme
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'username': user_id})
    if not user:
        return None
    return User(user['username'], user['password'], user['gallery_name'], user['city'], user['district'], user['address'], user['isim_soyisim'], user['yetki'])


# Kayıt Olma İşlevi
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Form verilerini alın
        username = request.form['username']
        password = request.form['password']
        gallery_name = request.form['gallery_name']
        city = request.form['city']
        district = request.form['district']
        address = request.form['address']
        isim_soyisim = request.form['isim_soyisim']
        yetki = request.form['yetki'] if 'yetki' in request.form else 'Kullanıcı'

        # Kullanıcının mevcut olup olmadığını kontrol edin
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            error = 'Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.'
            return render_template('signup.html', error=error)

        # Şifreyi hashleyin, kullanıcıyı veritabanına kaydedin ve otomatik olarak giriş yapın
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password, 'gallery_name': gallery_name, 'city': city, 'district': district, 'address': address, 'isim_soyisim':isim_soyisim, 'yetki': yetki})
        user = User(username, hashed_password, gallery_name, city, district, address, isim_soyisim, yetki)
        return render_template('kaydedildi.html', username=username)

    # GET isteklerinde kayıt sayfasını göster
    return render_template('signup.html')



# Giriş İşlevi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Form verilerini alın
        # username = request.form['username']
        # password = request.form['password']
        username = request.json.get('username')
        password = request.json.get('password')

        # Kullanıcıyı veritabanından alın
        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            user_obj = User(user['username'], user['password'], user['gallery_name'], user['city'], user['district'], user['address'], user['isim_soyisim'], user['yetki'])
            login_user(user_obj)
            return jsonify({'message': 'Login successful'}), 200
            # return redirect(url_for('index'))

        # Geçersiz kimlik bilgileri durumunda buraya yönlendir
        return jsonify({'message': 'Login failed'}), 401
        return render_template('sign-in.html', error='Kullanıcı adı veya şifre hatalı.')

    # GET isteklerinde login sayfasını göster
    return render_template('sign-in.html')


# Çıkış İşlevi
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#######LOGIN SON ###########


####### ARAC SECIMI BASLANGIC  ####


# Model Yılı Seçenekleri endpoint'i
@app.route('/model_yili_secenekleri', methods=['GET'])
def model_yili_secenekleri():
    # Veritabanından tüm model yıllarını çek
    model_yillari = modellerDb.distinct('Model yılı')

    # JSON formatında model yıllarını döndür
    return jsonify(model_yillari)

@app.route('/markalar', methods=['GET'])
def markalar():
    # İstemciden model yılını al
    model_yili = int(request.args.get('model_yili'))

    # Veritabanından model yılına ait markai çek
    markalar = modellerDb.distinct('Marka', {'Model yılı': model_yili})
    
    # JSON formatında modelleri döndür
    return jsonify(markalar)

@app.route('/modeller', methods=['GET'])
def modeller():
    # İstemciden model yılını al
    marka = request.args.get('marka_adi')
    model_yili = int(request.args.get('model_yili'))
    
    # print (marka, model_yili)

    # Veritabanından model yılına ait araci çek
    modeller = modellerDb.distinct('Model', {'Model yılı': model_yili, 'Marka': marka})
    
    # JSON formatında modelleri döndür
    return jsonify(modeller)

@app.route('/fiyat', methods=['GET'])
def fiyat():
    # İstemciden model yılını al
    marka = request.args.get('marka_adi')
    model_yili = int(request.args.get('model_yili'))
    tip_adi = request.args.get('tip_adi')

    if (tip_adi == '----'):
        return 
    
    # print (marka, model_yili, tip_adi)
    # Veritabanından model yılına ait araci çek
    arac_kasko_bedel = modellerDb.find_one({'Model yılı': model_yili, 'Marka': marka, 'Model':tip_adi})
    if arac_kasko_bedel is not None:
        # print(arac_kasko_bedel['Kasko Bedeli'])
        return {'kaskobedeli':arac_kasko_bedel['Kasko Bedeli'], 
                'kaskokodu':arac_kasko_bedel['Kasko Kodu'],
                'modelyili':arac_kasko_bedel['Model yılı'], 
                'marka':arac_kasko_bedel['Marka'], 
                'model':arac_kasko_bedel['Model'],}
    else:
        print("arac_kasko_bedel is None")
        
# kasko kodu ve model yılı ıle arac sorgula
@app.route('/fiyat2', methods=['GET'])
def fiyat2():
    # İstemciden model yılını al
    kasko_kodu = request.args.get('kasko_kodu')
    model_yili = int(request.args.get('model_yili'))

    if model_yili is None:
        return

    
    # print (marka, model_yili, tip_adi)
    # Veritabanından model yılına ait araci çek
    arac_kasko_bedel = modellerDb.find_one({
                                    "Model yılı": model_yili,
                                    "Kasko Kodu": kasko_kodu
                                    })
    if arac_kasko_bedel is not None:
        print("calisti")
        # print(arac_kasko_bedel['Kasko Bedeli'])
        return {'kaskobedeli':arac_kasko_bedel['Kasko Bedeli'], 
                'modelyili':arac_kasko_bedel['Model yılı'], 
                'marka':arac_kasko_bedel['Marka'], 
                'model':arac_kasko_bedel['Model'], 
                }
    else:
        print("arac_kasko_bedel is None")
    
    

####### ARAC SECIMI SON  ########

####### il ilçe SECIMI BASLANGIC  ####

@app.route('/il_secimi', methods=['GET'])
@login_required
def il_secimi():
    # Veritabanından tüm model yıllarını çek
    iller = il_ilce_tb.distinct('il')

    # JSON formatında model yıllarını döndür

    json_response = json.dumps(iller, ensure_ascii=False)

    return json_response, 200
    

@app.route('/ilce_secimi', methods=['GET'])
@login_required
def ilce_secimi():
    # İstemciden model yılını al
    il = request.args.get('il_secimi')

    # Veritabanından model yılına ait markai çek
    ilceler = il_ilce_tb.distinct('ilce', {'il': il})
    
    # JSON formatında modelleri döndür
    
    
    json_response = json.dumps(ilceler, ensure_ascii=False)

    return json_response, 200


###### Vergi daireleri il ilce sorgu Baslangic #####
@app.route('/vergi_ilce_secimi', methods=['GET'])
def vergi_ilce_secimi():
    def turkish_upper(text):
        # Türkçe karakterleri büyütme
        text = text.replace("i", "İ").replace("ı", "I").upper()
        return text
    
    # İstemciden ili al
    il = turkish_upper(request.args.get('il_secimi'))
    print(il)
    # Veritabanından model yılına ait markai çek
    ilceler = vergi_daire_il_ilceler.distinct('vergi_dairesi', {'ili': il})
    
    # JSON formatında modelleri döndür
    
    
    json_response = json.dumps(ilceler, ensure_ascii=False)

    return json_response, 200
###### Vergi daireleri il ilce sorgu SON #####


####### Telefondan Oto Galeri bul baslangic  ####
@app.route('/galeri_sorgu', methods=['GET'])
@login_required
def galeri_sorgu():
    # İstemciden ili al
    galeri_telefonu = request.args.get('galeri_telefonu')
    
    # Veritabanından model yılına ait markai çek
    user = users_collection.find_one({'username': galeri_telefonu})
    
    # JSON formatında modelleri döndür
    if user:
        json_response = {
            'galeri_adi': user['gallery_name'],
            'galeri_il': user['city']
        }
        return json_response, 200
    
    return jsonify({'message': 'Galeri kayıtlı değil'}), 401

####### Telefondan Oto Galeri bul son  ####


####### Sase no dan arac bilgilerini getir bul baslangic  ####
@app.route('/saseden_arac_bilgileri', methods=['GET'])
@login_required
def saseden_arac_bilgileri():
    # İstemciden ili al
    sasi_no = request.args.get('sasi_no')
    
    # Veritabanından model yılına ait markai çek
    kayitli_arac_bilgisi = customers.find_one({'sasi_no': sasi_no}, sort=[('created_time', -1)])
    
    # JSON formatında modelleri döndür
    if kayitli_arac_bilgisi:
        json_response = {
            'model_yili': kayitli_arac_bilgisi['model_yili'],
            'kaskokodu': kayitli_arac_bilgisi['kaskokodu'],
            'motor_no': kayitli_arac_bilgisi['motor_no'],
            'tescil_belge_no': kayitli_arac_bilgisi['tescil_belge_no'],
            'arac_plakasi': kayitli_arac_bilgisi['arac_plakasi'],
        }
        return json_response, 200
    
    return jsonify({'message': 'Arac kayıtlı değil'}), 401
####### Sase no dan arac bilgilerini getir bul son  ####


####### Dosya_id ile dosya icerigini tamemen getir. edit icin baslangic  ####
@app.route('/id_ile_dosya_bilgisi_getir', methods=['GET'])
@login_required
def id_ile_dosya_bilgisi_getir():
    # İstemciden ili al
    dosya_id = request.args.get('dosya_id')
    
    
    # Veritabanından model yılına ait markai çek
    kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})
    
    # JSON formatında modelleri döndür
    if kayitli_dosya_bilgisi:

        json_response = json_util.dumps(kayitli_dosya_bilgisi)

        return json_response, 200
    
    return jsonify({'message': 'Dosya kayıtlı değil'}), 401

####### Dosya_id ile dosya icerigini tamemen getir. edit icin son  ####


######## Dosya Guncellemeleri Servisi get ve post  baslangic #########

# dosya guncellemeleri genel fonlsiyon/ sadece edit ve create icin bu fonksiyon kullanilmadi/ eger yeni alan eklenirse oralarida guncelle
def dosya_guncelleme_ekle(dosya_id, inputValue, status):
    # ilgili_galeri = customers.find_one({'_id': ObjectId(dosya_id)})['galeri_telefonu'] #bunu daha sonra galeri guncellemlerini eklerken kullanacagim
    dataGuncelle = {
                    'inputValue': inputValue,
                    'created_by': current_user.id,
                    'isim_soyisim': current_user.isim_soyisim,
                    'status': status,   # otomatik(kendiliginden) kullanici(kullanici aciklama ekler) standart(dugmeler ile)
                    'created_time': datetime.now(),
                }

    result = customers.update_one(
        {"_id": ObjectId(dosya_id)},
        {"$push": {"guncellemeler": dataGuncelle}}
    )

    return result

########### Kredi dosyasi guncellemelri ekliyoruz ve getiriyoruz BASLANGIC ########

@app.route('/dosya_guncellemeleri', methods=['GET', 'POST'])
@login_required
def dosya_guncellemeleri():
    
    if request.method == 'POST':
        dosya_id = request.json['dosya_id']
        
        try:
            # Veritabanından id ye ait kisibilgisini cek
            kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})

            # if (request.json['inputValue'] == 'Devam') or (request.json['inputValue'] == 'Kullandırıldı') or (request.json['inputValue'] == 'Sonlandı'):
            #     ekleyen = 'standart'
            # else:
            #     ekleyen = 'kullanici'

            ekleyen = 'kullanici'
            result = dosya_guncelleme_ekle(dosya_id, request.json['inputValue'], ekleyen)
            
            return jsonify({'message': 'Form kaydedildi'}), 200
        
        except Exception as e:
            print(e)
            return jsonify({'message': 'Bir hata oluştu'}), 500
        
    dosya_id = request.args.get('dosya_id')
    
    documents = customers.find_one({'_id': ObjectId(dosya_id)})['guncellemeler']
    
    documents_reverse = sorted(documents, key=lambda k: k['created_time'], reverse=True)
    json_documents = dumps(documents_reverse)
    return jsonify(json_documents), 200

######## Dosya Guncellemeleri Servisi get ve post  Son #########

####### Dosya durumu devam kullanildi sonlandi felan baslangic #######   Devam , Sonlandı , Kullandırıldı
# Dökümanı güncelleme işlemi
@app.route('/dosya-durum-data', methods=['GET', 'POST'])
@login_required
def get_dosya_durum_data():

    if request.method == 'POST':
        dosya_id = request.json['dosya_id']

        try:
          
            status = request.json['status']

            customers.update_one({'_id': ObjectId(dosya_id)}, {'$set': {'status': status}})
            mesaj = 'Dosya durumu güncellendi -> ' + status
            dosya_guncelleme_ekle(dosya_id, mesaj, 'standart')

            return jsonify({'success': True})
        
        except Exception as e:
            print(e)
            return jsonify({'message': 'Bir hata oluştu'}), 500
        
    dosya_id = request.args.get('dosya_id')
    
    # Veritabanından son durumu çekin
    dosya_status = customers.find_one({'_id': ObjectId(dosya_id)})['status']
        
    # JSON olarak verileri döndürün
    return jsonify(dosya_status)

####### Dosya durumu devam kullanildi sonlandi felan son #######

######## Banka yanlarındakı radıo butonlar ıle surec takibı için servis başlangıç #########

@app.route('/radio-data', methods=['GET', 'POST'])
@login_required
def get_radio_data():

    if request.method == 'POST':
        dosya_id = request.json['dosya_id']

        try:
            # Veritabanından id ye ait kisibilgisini cek
            kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})

            name = request.json['name']
            value = request.json['value']

            # Eğer güncellemeler listesi henüz tanımlanmadıysa, boş bir dokuman olarak başlatın
            if 'durum' not in kayitli_dosya_bilgisi:
                kayitli_dosya_bilgisi['durum'] = {}
            
            # durum dokumanina yeni güncelleme verisini ekleyin
            kayitli_dosya_bilgisi["durum"][name] = value

            # MongoDB'deki belgeyi güncelleyin
            result = customers.update_one({"_id": ObjectId(dosya_id)}, {"$set": {"durum": kayitli_dosya_bilgisi['durum']}})

            mesaj = name + ' -> <strong> ' + value + '</strong>'
            dosya_guncelleme_ekle(dosya_id, mesaj, 'standart')
            
            # Başarılı bir şekilde kaydedildi sayfasını göster
            return jsonify({'message': 'Form kaydedildi'}), 200
        
        except Exception as e:
            print(e)
            return jsonify({'message': 'Bir hata oluştu'}), 500
    
    data = {}

    dosya_id = request.args.get('dosya_id')
    
    # Veritabanından son durumu çekin
    kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})
    if 'durum' in kayitli_dosya_bilgisi:
        data = kayitli_dosya_bilgisi['durum']
        
    # JSON olarak verileri döndürün
    return jsonify(data)

######## Banka yanlarındakı radıo butonlar ıle surec takibı için servis son #########


######## Kullandirim sonrasi verileri ve hesaplamalar baslangic #######

@app.route('/kredi-kullandir', methods=['GET', 'POST'])
def kredi_kullandir():
    if request.method == 'POST':
        dosya_id = request.json['document_id']

        kullanım_bilgileri = {
            'kredi': request.json['kredi'],
            'bayi_odemesi': request.json['bayi_odemesi'],
            'noter': request.json['noter'],
            'saha_ekibi': request.json['saha_ekibi'],
            'bayi': request.json['bayi'],
            'kredi_primi': request.json['kredi_primi'],
            'kullandirim': request.json['kullandirim'],
            'banka_kullandirim': request.json.get('banka_kullandirim', ''),
            'kullandirim_tarihi': request.json.get('kullandirim_tarihi', ''),
            'net_gelir': request.json['net_gelir']
        }

       
        result = customers.update_one(
            {"_id": ObjectId(dosya_id)},
            {'$set': {'kullandirim_bilgileri': kullanım_bilgileri}}
        )

        mesaj = '* * * Kullandırım bilgileri eklendi * * *'
        dosya_guncelleme_ekle(dosya_id, mesaj, 'standart')

        # Başarılı bir şekilde kaydedildi sayfasını göster
        return jsonify({'message': 'Form kaydedildi'}), 200

    data = {}

    dosya_id = request.args.get('dosya_id')
    
    # Veritabanından son durumu çekin
    kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})
    if 'kullandirim_bilgileri' in kayitli_dosya_bilgisi:
        data = kayitli_dosya_bilgisi['kullandirim_bilgileri']
        
    # JSON olarak verileri döndürün
    return jsonify(data)
    

######## Kullandirim sonrasi verileri ve hesaplamalar sonuc #######

##### Dosyalar sayfasindak'10 adet dosyanin yada daha fazla 60 saniyede bir g]ncellenmes icin servis baslangici ######
@app.route('/process_customer_ids', methods=[ 'POST'])
def process_customer_ids():
   
    customerIds = request.json['customerIds']

    # for dosya_id in customerIds: # her bir müşteri kimliği için
    #     print( customers.find_one({'_id': ObjectId(dosya_id)})['durum'] )       # kimliği ekrana yazdır     customers.find_one({'_id': ObjectId(dosya_id)})
    # results = [{'dosya_id': dosya_id, 'data': customers.find_one({'_id': ObjectId(dosya_id)})['durum'] } for dosya_id in customerIds]
    results = []
    for dosya_id in customerIds:
        document = customers.find_one({'_id': ObjectId(dosya_id)})
        
        # 'durum' alanı var mı diye kontrol edin
        status = document.get('durum')
        if status is None:
            # 'durum' alanı yok veya boş
            # results.append({'dosya_id': dosya_id, 'data': None})
            tekilDurum = None
        else:
            # results.append({'dosya_id': dosya_id, 'data': status})
            # Sözlüğü dolaşın ve secim-yok olanları çıkarın
            for anahtar, deger in status.copy().items():
                if deger == 'secim-yok':
                    del status[anahtar]
            tekilDurum = status

        # 'guncellemeler' alanındaki objectleri kontrol edin
        updates = document.get('guncellemeler', [])
        latest_update = None  # en son güncelleme yok varsayalım
        for update in updates:
            if update.get('status') == 'kullanici':
                if latest_update is None or update.get('created_time') > latest_update.get('created_time'):
                    latest_update = update
        
        sonDurum = document.get('status')
        
        results.append({'dosya_id': dosya_id, 'bankalar': tekilDurum, 'aciklama':latest_update, 'durum': sonDurum})

    response = {'success': True, 'results': results}
    return jsonify(response)

##### Dosyalar sayfasindak'10 adet dosyanin yada daha fazla 15 saniyede bir g]ncellenmes icin servis sonu ############# 

########silinecek deneme ############
@app.route('/veriler', methods=['GET'])
def veriler():
    # Verilerinizi bir şekilde elde edin ve JSON formatına dönüştürün.
    data = {
        "01": {"tarih": "01-2023", "sehir": "İstanbul", "kredi_adedi": 100, "komisyon_geliri": 5000, "harcama": 4000, "artan_para": 1000},
        "02": {"tarih": "01-2023", "sehir": "Ankara", "kredi_adedi": 200, "komisyon_geliri": 10000, "harcama": 8000, "artan_para": 2000},
        "03": {"tarih": "01-2023", "sehir": "İzmir", "kredi_adedi": 150, "komisyon_geliri": 7500, "harcama": 6000, "artan_para": 1500},
        "04": {"tarih": "02-2023", "sehir": "Bursa", "kredi_adedi": 175, "komisyon_geliri": 8750, "harcama": 7000, "artan_para": 1750},
        "05": {"tarih": "02-2023", "sehir": "İstanbul", "kredi_adedi": 100, "komisyon_geliri": 5000, "harcama": 4000, "artan_para": 1000},
        "06": {"tarih": "02-2023", "sehir": "Ankara", "kredi_adedi": 200, "komisyon_geliri": 10000, "harcama": 8000, "artan_para": 2000},
        "07": {"tarih": "03-2023", "sehir": "İzmir", "kredi_adedi": 150, "komisyon_geliri": 7500, "harcama": 6000, "artan_para": 1500},
        "08": {"tarih": "03-2023", "sehir": "Bursa", "kredi_adedi": 175, "komisyon_geliri": 8750, "harcama": 7000, "artan_para": 1750}
    }
    
    # Verileri JSON formatına dönüştürün ve istemciye gönderin.
    return jsonify(data)

##################################

########### Harcamlaar bolumu get ve post islemleri BASLANGIC ########

@app.route('/harcama_islemleri', methods=['POST'])
@login_required
def harcama_islemleri():
    
    if request.method == 'POST':
        data = request.json
        
        try:
            # Add user information and timestamp to the data before saving it to the database
            data['kayit_eden_kullanici_telefonu'] = current_user.id
            data['kayit_eden_kullanici_ismi'] = current_user.isim_soyisim
            data['kayit_zamani'] = datetime.now()
            
            # Insert the data into the "harcamalar" collection in your MongoDB database
            db.harcamalar.insert_one(data)
            
            return jsonify({'message': 'Form kaydedildi'}), 200
        
        except Exception as e:
            print(e)
            return jsonify({'message': 'Bir hata oluştu'}), 500
    
    else:
        return {'success': False, 'error': 'Invalid request method'}
    

######## Harcamlaar bolumu get ve post islemleri  Son #########

if __name__ == '__main__':
    app.run(debug=True)
