from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date
from functools import wraps

import pymongo
from pymongo import DESCENDING
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from collections import OrderedDict

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
gecici_guncellemeler = db.gecici_guncellemeler

hazir_veriler = client["form_hazir_verileri"]   # vergi daireleri, iller, ilceler ve arac modelleri bu collectionda
modellerDb = hazir_veriler["modeller"]          # ilk sutun integer. sonrakiler string
il_ilce_tb = hazir_veriler["il_ilce"]           # il ve ilce select boxlarinda kullanmak icin.
vergi_daire_il_ilceler = hazir_veriler["vergi_daireleri"]


app = Flask(__name__)
app.secret_key = secret

# Kullanıcı Bilgileri getir fonksiyonu. hersayfada kulllanildi
def user_data_getir():

    belgeler2 = customers.find({
        "created_time": {
            "$gte": datetime.now() - timedelta(days=30)
        }
    }, )

    toplam_belge_sayisi_30_gunluk = len(list(belgeler2))
    
    # 30 gunluk kullandirilan sorgu yap
    belgeler = customers.find({
        "status": "Kullandırıldı",
        "created_time": {
            "$gte": datetime.now() - timedelta(days=30)
        }
    }, )

    # Net geliri hesapla
    kullandirilan_30_gunluk = 0
    kullandirilan_belge_sayisi_30_gunluk = 0
    for belge in belgeler:
        try:
            net_gelir_str = belge['kullandirim_bilgileri']['kredi']
            if net_gelir_str: # string boş değilse devam et
                # net_gelir_str = net_gelir_str.replace('.', '')  # Noktaları kaldır
                # net_gelir_str = net_gelir_str.replace(',', '.')  # Virgülü noktaya çevir
                net_gelir_float = float(net_gelir_str)  # sayiyi integer donustur
                kullandirilan_30_gunluk += net_gelir_float
                # print(net_gelir_float, belge['dosya_numarasi'])
                kullandirilan_belge_sayisi_30_gunluk += 1
        except KeyError:
            continue

    # sureci devam eden sorgu yap
    belgeler3 = customers.find({
        "status": {"$in": ["Devam", "Kullandırılacak"]},
    }, )
    toplam_devam_eden_sayisi = len(list(belgeler3))
   
    return {
        "isim_soyisim": current_user.isim_soyisim,
        "cep_telefonu": current_user.id,
        "sehir": current_user.city,
        "yetki": current_user.yetki,
        "gallery_name": current_user.gallery_name,
        "ilce": current_user.district,
        "adres": current_user.address,
        "kullandirilan_30_gunluk": kullandirilan_30_gunluk,
        "kullandirilan_belge_sayisi_30_gunluk": kullandirilan_belge_sayisi_30_gunluk,
        "toplam_belge_sayisi_30_gunluk": toplam_belge_sayisi_30_gunluk,
        "toplam_devam_eden_sayisi":toplam_devam_eden_sayisi

    }

# Sadece yonetici yetkisiyle gorulebilecek sayfalari bununla kapsa
def yonetici_gerekli(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.yetki == 'Yönetici':
            metadata = {
                'sayfa_baslik': 'Yetkiniz Yok'
            }

            user_data = user_data_getir()
            
            return render_template('admin/hata.html', metadata=metadata, user_data=user_data)
            
        return f(*args, **kwargs)
    return decorated

# Index sayfasi
@app.route('/')
@login_required
def index():
    # index.html adlı template'i döndür
    return render_template('index.html')

# Index sayfasi
@app.route('/kvkk')
def kvkk():
    # index.html adlı template'i döndür
    return render_template('statik_sayfa/kvkk.html')

@app.route('/destek')
@login_required
def destek():

    metadata = {
        'sayfa_baslik': 'Yardım Sayfası'
    }

    user_data = user_data_getir()
    
    return render_template('destek.html', metadata=metadata, user_data=user_data)

# Index sayfasi
@app.route('/harcamalar')
@login_required
@yonetici_gerekli
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
    harcamalar_list = list(harcamalar_db.find({}, {'_id':1, 'harcama_tarihi':1, 'harcama_kisi_secimi':1, 'harcama_aciklamasi':1, 'tutar':1 }).sort([("harcama_tarihi", pymongo.DESCENDING), ("kayit_zamani", pymongo.DESCENDING)]).skip(start_index).limit(per_page))


    
    # Pagination metadatasını oluştur
    metadata = {
        'page': page,
        'per_page': per_page,
        'total_customers': total_customers,
        'total_pages': int(total_customers / per_page) + 1,
        'sayfa_baslik': 'Harcamalar'
    }

    user_data = user_data_getir()
    
    return render_template('harcamalar.html', data=harcamalar_list , metadata=metadata, user_data=user_data)

# Index sayfasi
@app.route('/iletisim')
@login_required
def iletisim():

    metadata = {
        'sayfa_baslik': 'İletişim Sayfası'
    }

    user_data = user_data_getir()
    
    
    return render_template('iletisim.html', metadata=metadata, user_data=user_data)

# Index sayfasi
@app.route('/hesabim')
@login_required
def hesabim():

    # Pagination metadatasını oluştur
    metadata = {
        'sayfa_baslik': 'Hesap Ayarları'
    }

    user_data = user_data_getir()
    
    
    return render_template('hesabim.html', user_data=user_data, metadata=metadata)

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

    user_data = user_data_getir()
    
    return render_template('userlist.html', data=customer_list , metadata=metadata, user_data=user_data)

# İstatistik Veriler sayfasi
@app.route('/istatistik/')
@app.route('/istatistik/<parametre>')
@login_required
@yonetici_gerekli
def istatistik(parametre=None):

    # Pagination metadatasını oluştur
    metadata = {
        'sayfa_baslik': 'İstatistik'
    }

    user_data = user_data_getir()

    if parametre:
        if parametre == 'bankalar':
            # Sayfa 1'in render edilmesi
            metadata = {
                'sayfa_baslik': 'Bankalara Göre Dağılım Grafiği'
            }
            return render_template('/istatistik/bankalar.html', metadata=metadata, user_data=user_data)

        elif parametre == 'gelir-gider':
            # Sayfa 2'nin render edilmesi
            metadata = {
                'sayfa_baslik': 'Gelir Gider İstatistikleri'
            }
            return render_template('/istatistik/gelir-gider.html', metadata=metadata,user_data=user_data)
        
        elif parametre == 'kullanicilar':
            
            metadata = {
                'sayfa_baslik': 'Kullanıcı İstatistikleri'
            }
            return render_template('/istatistik/kullanicilar.html', metadata=metadata,user_data=user_data)
        
        elif parametre == 'marka-model':
            
            metadata = {
                'sayfa_baslik': 'Marka/Model Kullandırım İstatistikleri'
            }
            return render_template('/istatistik/marka-model.html', metadata=metadata,user_data=user_data)
        
        elif parametre == 'sehirler':
            
            metadata = {
                'sayfa_baslik': 'Şehir Bazında Kullandırım İstatistikleri'
            }
            return render_template('/istatistik/sehirler.html', metadata=metadata,user_data=user_data)
        
        elif parametre == 'bankalar2':
            
            metadata = {
                'sayfa_baslik': 'Bankalara Göre Dağılım Tablosu'
            }
            return render_template('/istatistik/bankalar2.html', metadata=metadata,user_data=user_data)
        else:
            return render_template('/istatistik/ana.html', metadata=metadata, user_data=user_data)
    else:
        return render_template('/istatistik/ana.html', metadata=metadata, user_data=user_data)


# API - Yeni/Eski Kredi Dosyası Ekle , güncelle
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
        if not (dosya_id=='' or dosya_id == "yeni" or dosya_id == "eski"):
            # Veritabanından guncelenecek dosya bilgisini cek
            kayitli_dosya_bilgisi = customers.find_one({'_id': ObjectId(dosya_id)})
            
            # JSON formatında modelleri döndür
            if kayitli_dosya_bilgisi:
                #alttaki degerlerlerin guncellenmemesi icin jsondan kaldir
                del data["dosya_id"]
                del data["dosya_numarasi"]
                del data["created_time"]
                del data["created_by"]
                del data["created_by_isim"]

                # edit islemi esnasinda saha personeli silinemez
                if "saha_personeli" in data and data["saha_personeli"]:
                    del data["saha_personeli"]


                dosya_guncelleme_ekle(dosya_id, 'Dosya guncellendi', 'otomatik')
                # # guncelleme bılgılerı tımelıne ekleme
                # dataGuncelle = {
                #     'inputValue': 'Dosya guncellendi',
                #     'created_by': current_user.id,
                #     'isim_soyisim': current_user.isim_soyisim,
                #     'status': 'otomatik',   # success  pending  failed
                #     'created_time': datetime.now(),
                # }

                # data['guncellemeler'] = kayitli_dosya_bilgisi['guncellemeler']

                # data["guncellemeler"].append(dataGuncelle)

                new_data = {
                    "$set": data
                }
                
                result = customers.update_one({"_id": ObjectId(dosya_id)}, new_data)
                
                return jsonify({'message': 'Form kaydedildi','dosya_id': str(dosya_id)}), 200
            
        # 3 farkli dosya_id gelme ihtimali var: yeni, eski, varolan baska bir fokumanin id'si. ESKI dosya bilgisi kaydetmek icin id eski gelir
        if (dosya_id == "eski"):
            date_str = request.json.get('created_time')
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            data['created_time'] = date_obj
        else:
            # eger dosya daha onceden yoksa ve İLK DEFA BİR DOSYA OLUŞTURULUyorsa
            data['created_time'] = datetime.now(turkey_tz)

        # yeni ve eski kelimelerini siler. bu kayit esnasinda otomatik atanacak
        if "dosya_id" in data:
            del data["dosya_id"]
        
        data['status'] = 'Devam'   # surec sayfasindaki renkli butonlar

        # Rastgele 5 haneli büyük harf, rakam ve tirelerden oluşan benzersiz bir dizi oluşturuyoruz.
        dosya_numarasi = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Benzersiz dosya numarasi daha önce kullanılmış mı diye kontrol ediyoruz.
        while customers.find_one({"dosya_numarasi": dosya_numarasi}) is not None:
            dosya_numarasi = ''.join(random.choices(string.ascii_uppercase + string.digits + '-', k=5))

        # benzersiz dosya numarasi eklenir
        data['dosya_numarasi'] = dosya_numarasi

        # dosya numarasi belli olmadigi icin guncelleme fonksiyonu kullanilamadi
        # data["guncellemeler"] = [{
        #     "inputValue": "Dosya oluşturuldu.",
        #     "created_by": current_user.id,
        #     "isim_soyisim": current_user.isim_soyisim,
        #     "status": "otomatik",   # success  pending  failed
        #     "created_time": datetime.now(),
        # }]

        # Database kayıt işlemi
        result = customers.insert_one(data)

        dosya_id = result.inserted_id
        # print(f"_id of inserted document {dosya_id}")

        dosya_guncelleme_ekle(dosya_id, "Dosya oluşturuldu.", "otomatik")
        update_selected_customer(dosya_id)

       
        # Başarılı bir şekilde kaydedildi sayfasını göster
        return jsonify({'message': 'Form kaydedildi','dosya_id': str(dosya_id)}), 200
        
    return jsonify({'message': 'Form gonderilmedi'}), 401


# Ozet sayfası
@app.route('/dashboard')
@login_required
def dashboard():

    user_data = user_data_getir()
    # print( user_data['cep_telefonu'])
    def get_kredi_dosyalari(status):
        return list(customers.find({
            'created_by': user_data['cep_telefonu'],
            'silindi': {'$ne': 1},
            'status': status
        }, {
            '_id': 1,
            'adi': 1,
            'soyadi': 1,
            'dosya_numarasi': 1,
            'galeri_ili': 1,
            'galeri_adi': 1,
            'kredi_tutari': 1,
            'kredi_vadesi': 1,
            'calisma_sekli': 1,
            'kredi_miktar': 1,
            'kredi_vadesi': 1,
            'created_time': 1,
            'musteri_cep_telefonu': 1,
            'model_yili': 1,
            'marka_adi': 1,
            'tip_adi': 1,
            'created_by_isim': 1,
            'status': 1
        }).sort('_id', -1).limit(5))

    kredi_dosyalari = {}
    kredi_dosyalari['Devam'] = get_kredi_dosyalari('Devam')
    kredi_dosyalari['Kullandırıldı'] = get_kredi_dosyalari('Kullandırıldı')
    kredi_dosyalari['Kullandırılacak'] = get_kredi_dosyalari('Kullandırılacak')
    kredi_dosyalari['Sonlandı'] = get_kredi_dosyalari('Sonlandı')
    # print(kredi_dosyalari)
   
    
    
    metadata ={
        'sayfa_baslik': 'Özet'
    }

    # dosya durumlarinin sayilarini getir
    pipeline = [
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
    ]
    results = customers.aggregate(pipeline)

    dosya_durum_sayilari = {}
    for result in results:
        dosya_durum_sayilari[result['_id']] = result['count']
    # print (response_dict)

    # eger bu kullanici icin secim yapima collectionunda bir dokuman varsa bul getir
    query = {"current_user": current_user.id }
    existing_doc = selected_customers.find_one(query)

    if existing_doc:
        # Doküman mevcut, secili musteri dosya bilgisini getirir
        lstest_customer_id = existing_doc["customer_id"]
    else:
        lstest_customer_id = '0'

    # Template'e JSON verisini gönderin
    return render_template("dashboard.html", user_data=user_data, metadata=metadata, kredi_dosyalari= kredi_dosyalari, lstest_customer_id = lstest_customer_id, dosya_durum_sayilari=dosya_durum_sayilari)


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

    # Personel seçimini al
    saha_personeli = request.args.get('personel')

    # Adres satırından arama kelimesi al
    search_keyword = request.args.get('arama')

    query = {}

    if selected_city and selected_city != 'Tüm':
        query['galeri_ili'] = selected_city

    if dosya_durumu and dosya_durumu != 'Hepsi':
        query['status'] = dosya_durumu

    if saha_personeli and saha_personeli != 'Hepsi':
        query['saha_personeli'] = saha_personeli

    if search_keyword:
        # eger isim soyisim gonderilirse son kelimeyi soyisim olarak ayirip aramayi yapmak icin asagisi var
        kelimeler = search_keyword.split()

        if len(kelimeler) > 1:
            son_kelime = kelimeler[-1]
            diger_kisim = ' '.join(kelimeler[:-1])
        else:
            son_kelime = search_keyword
            diger_kisim = search_keyword

        query["$or"] = [{"adi": {"$regex": diger_kisim, "$options": "i"}},
                        {"soyadi": {"$regex": son_kelime, "$options": "i"}},
                        {"dosya_numarasi": {"$regex": search_keyword, "$options": "i"}},
                        {"galeri_adi": {"$regex": search_keyword, "$options": "i"}},
                        {"galeri_telefonu": {"$regex": search_keyword, "$options": "i"}},
                        {"galeri_ili": {"$regex": search_keyword, "$options": "i"}},
                        {"model_yili": {"$regex": search_keyword, "$options": "i"}},
                        {"saha_personeli": {"$regex": search_keyword, "$options": "i"}},
                        {"marka_adi": {"$regex": search_keyword, "$options": "i"}},
                        {"tip_adi": {"$regex": search_keyword, "$options": "i"}},
                        {"kaskokodu": {"$regex": search_keyword, "$options": "i"}},
                        {"sasi_no": {"$regex": search_keyword, "$options": "i"}},
                        {"motor_no": {"$regex": search_keyword, "$options": "i"}},
                        {"tescil_belge_no": {"$regex": search_keyword, "$options": "i"}},
                        {"arac_plakasi": {"$regex": search_keyword, "$options": "i"}},
                        {"musteri_cep_telefonu": {"$regex": search_keyword, "$options": "i"}},
                        {"tc": {"$regex": search_keyword, "$options": "i"}},
                        {"acik_adres_ev": {"$regex": search_keyword, "$options": "i"}},
                        {"isyeri_adi": {"$regex": search_keyword, "$options": "i"}},
                        {"acik_adres_is": {"$regex": search_keyword, "$options": "i"}},
                        {"guncellemeler": {"$elemMatch": {"inputValue": {"$regex": search_keyword, "$options": "i"}}} }]

    # silindi olarak işaretlenmiş dosyaları gösterme
    query = {'$and': [{'silindi': {'$ne': 1}}, query]}

    # Get total number of customers with the specified filters
    total_customers = customers.count_documents(query)

    # Get customers from the database with the specified filters
    # customer_list = list(customers.find(query, {'_id': 1, 'adi': 1, 'soyadi': 1, 'dosya_numarasi': 1, 'galeri_ili': 1, 'galeri_adi': 1, 'kredi_tutari': 1, 'kredi_vadesi': 1, 'calisma_sekli': 1, 'kredi_miktar': 1, 'kredi_vadesi': 1, 'created_time': 1, 'musteri_cep_telefonu': 1, 'model_yili': 1, 'marka_adi': 1, 'tip_adi': 1, 'created_by_isim': 1, 'status': 1}).sort("created_time", -1))
    customer_list = list(customers.find(query, {'_id': 1, 'adi': 1, 'soyadi': 1, 'dosya_numarasi': 1, 'galeri_ili': 1, 'galeri_adi': 1, 'kredi_tutari': 1, 'kredi_vadesi': 1, 'calisma_sekli': 1, 'kredi_miktar': 1, 'kredi_vadesi': 1, 'created_time': 1, 'musteri_cep_telefonu': 1, 'model_yili': 1, 'marka_adi': 1, 'tip_adi': 1, 'created_by_isim': 1, 'status': 1}).sort('created_time', pymongo.ASCENDING))
    customer_list.reverse()


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
        'saha_personeli': saha_personeli,
        'search_keyword': search_keyword,
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

    user_data = user_data_getir()

    return render_template('basvurular.html', data=customer_list , metadata=metadata, lstest_customer_id=lstest_customer_id, user_data=user_data)

# Fonksiyon - Secili kullanıcıyı degistir
def update_selected_customer(customer_id):
    current_user_id = current_user.id       # secimi yapan kullanicinin cep telefonu. idsi
    selection_date = datetime.now(turkey_tz)

    # dokumanda mevcut kullanicinin baska bir kaydi varsa al
    query = {'current_user': current_user_id}
    existing_doc = selected_customers.find_one(query)

    if existing_doc:
        # Doküman mevcut, güncelleme yapılabilir
        existing_doc["customer_id"] = customer_id   # Bunu karıştırma. Bu kredi dosyası id'si
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
    
    return result


# API - Secili kullanıcıyı degistir
@app.route('/add_customer_selection', methods=['POST'])
@login_required
def add_customer_selection():

    # İstekten gelen JSON verilerini al
    data = request.get_json()
    customer_id = data['customer_id']    # Bu kredi dosyası id'si
    

    result = update_selected_customer( customer_id )

    return jsonify(str(result))

# API - secili musteri getir. masa ustu uygulamasi icin cep telefonu gonderilen kullaninicnin secili musteri bilgileri gonderilir
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


# Giriş Sayfasi
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
        
    # GET isteklerinde login sayfasını göster
    return render_template('sign-in.html')

# Yeni Kullanici ekleme sayfasi
@app.route('/signup', methods=['GET', 'POST'])
@login_required
@yonetici_gerekli
def signup():
    # GET isteklerinde kayıt sayfasını göster
    user_data = user_data_getir()
    
    metadata ={
        'sayfa_baslik': 'Yeni Kullanıcı Ekle'
    }

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
            error = f'{username} cep telefonu numarası ile kayıtlı başka bir kullanıcı var. Lütfen farklı bir cep telefonu ile üyelik oluşturun yada mevcut kullanıcının şifresini sıfırlayın.'
            return render_template("signup.html", user_data=user_data, metadata=metadata, error=error)

        # Şifreyi hashleyin, kullanıcıyı veritabanına kaydedin ve otomatik olarak giriş yapın
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password, 'gallery_name': gallery_name, 'city': city, 'district': district, 'address': address, 'isim_soyisim':isim_soyisim, 'yetki': yetki})
        user = User(username, hashed_password, gallery_name, city, district, address, isim_soyisim, yetki)
        return render_template("signup.html", user_data=user_data, metadata=metadata, username=username)

    # Template'e JSON verisini gönderin
    return render_template("signup.html", user_data=user_data, metadata=metadata)
    

# API - Parola degistir api
@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    # Form verilerini alın
    username = request.form['username']
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    # Kullanıcının mevcut olup olmadığını kontrol edin
    user = users_collection.find_one({'username': username})
    if not user:
        error = 'Kullanıcı bulunamadı'
        return jsonify({'success': False, 'error': error}), 404

    # Mevcut şifreyi doğrulayın
    if not check_password_hash(user['password'], old_password):
        error = 'Eski parolayı yanlış girdiniz'
        return jsonify({'success': False, 'error': error}), 401

    # Yeni şifreyi hashleyin ve güncelleyin
    new_hashed_password = generate_password_hash(new_password)
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'password': new_hashed_password}}
    )

    return jsonify({'success': True})

# Çıkış İşlevi
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#######LOGIN SON ###########


####### ARAC SECIMI BASLANGIC  ####


# API - Model Yılı Seçenekleri endpoint'i
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

# dosya guncellemeleri genel fonlsiyon/ 
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

    galeri_adi = customers.find_one({'_id': ObjectId(dosya_id)})['galeri_adi']
    galeri_telefonu = customers.find_one({'_id': ObjectId(dosya_id)})['galeri_telefonu']
    gorunen_dosya_no = customers.find_one({'_id': ObjectId(dosya_id)})['dosya_numarasi']
    dosya_tarihi_long = customers.find_one({'_id': ObjectId(dosya_id)})['created_time']
    # String olarak verilen tarihi datetime nesnesine dönüştürme
    dosya_tarihi = dosya_tarihi_long.strftime("%d/%m/%Y")

    geciciDataGuncelle = {
        'galeri_adi':galeri_adi,
        'galeri_telefonu':galeri_telefonu,
        'gorunen_dosya_no':gorunen_dosya_no,
        'dosya_tarihi':dosya_tarihi,
        'inputValue': inputValue,
        'isim_soyisim': current_user.isim_soyisim,
        'created_by': current_user.id,  # kayit eden user telefonu
        'status': status,   
        'created_time': datetime.now(),
    }

    # print(geciciDataGuncelle)
    

    gecici_guncellemeler.insert_one(geciciDataGuncelle)

    # eger gecici guncellemeler 100 den fazlaysa tarihe gore ilk kayidi sil
    # if gecici_guncellemeler.count_documents({}) > 100:
    #     oldest_record = gecici_guncellemeler.find_one_and_delete(sort=[('_id', 1)])  

    # En son 100 belgeyi hariç tutarak tüm kayıtları getir
    docs_to_delete = gecici_guncellemeler.find().sort('_id', -1).skip(300)

    # Silme işlemini gerçekleştir
    delete_result = gecici_guncellemeler.delete_many({'_id': {'$in': [doc['_id'] for doc in docs_to_delete]}})             

    return result

####### API - Dosya id den dosya numarasi sorgula ######
@app.route('/api/dosya_no_getir', methods=['GET'])
@login_required
def dosya_no_getir():        
    dosya_id = request.args.get('dosya_id')
    document = customers.find_one({'_id': ObjectId(dosya_id)})['dosya_numarasi']
    return jsonify(document)

#######################################################


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


###### GEcici guncellmeleri json ile getir baslangic ##########
##### Bunu daha sonra kullaniciya yonelik gosterilmesi gerekenler olarak duzenle######
@app.route('/api/gecici_guncellemeler', methods=['GET'])
@login_required
def get_gecici_guncellemeler():
    
    gecici_guncellemeler_data = []
    for record in gecici_guncellemeler.find().sort("_id", -1).limit(40):
        # json_util.dumps() yöntemini kullanarak ObjectId'yi dizeye dönüştürün:
        serialized_record = json.loads(json_util.dumps(record))

        # ObjectId'i kaldır
        del serialized_record['_id']
        gecici_guncellemeler_data.append(serialized_record)

    return jsonify(gecici_guncellemeler_data)

@app.route('/api/gecici_guncellemeler/kullanici', methods=['GET'])
@login_required
def get_gecici_guncellemeler_kullanici():
    
    gecici_guncellemeler_data = []
    for record in gecici_guncellemeler.find({'isim_soyisim':current_user.isim_soyisim}).sort("_id", -1).limit(40):
        # json_util.dumps() yöntemini kullanarak ObjectId'yi dizeye dönüştürün:
        serialized_record = json.loads(json_util.dumps(record))

        # ObjectId'i kaldır
        del serialized_record['_id']
        gecici_guncellemeler_data.append(serialized_record)

    return jsonify(gecici_guncellemeler_data)

###### GEcici guncellmeleri json ile getir son ##########

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
@login_required
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

########### Harcamlaar bolumu get ve post islemleri BASLANGIC ########

@app.route('/harcama_islemleri', methods=['POST'])
@login_required
@yonetici_gerekli
def harcama_islemleri():
    
    if request.method == 'POST':
        data = request.json
        
        try:
            # Add user information and timestamp to the data before saving it to the database
            data['kayit_eden_kullanici_telefonu'] = current_user.id
            data['kayit_eden_kullanici_ismi'] = current_user.isim_soyisim
            data['kayit_zamani'] = datetime.now()
            
            # Insert the data into the "harcamalar" collection in your MongoDB database
            harcamalar_db.insert_one(data)
            
            return jsonify({'message': 'Form kaydedildi'}), 200
        
        except Exception as e:
            print(e)
            return jsonify({'message': 'Bir hata oluştu'}), 500
    
    else:
        return {'success': False, 'error': 'Invalid request method'}
    

######## Harcamlaar bolumu get ve post islemleri  Son #########

######### Harcamlar bolumu harcama silme ####################
@app.route('/harcama_sil', methods=['POST'])
@login_required
@yonetici_gerekli
def harcama_sil():
    harcamaid = request.form['harcamaid'] 
    harcamalar_db.delete_one({'_id': ObjectId(harcamaid)})
    return jsonify({'success': True})

#############################################################

######### Basvuru Dosyası silme, veri tabanına silindi diye bir ekleme yapar. ####################
@app.route('/basvuru_dosyasi_sil', methods=['POST'])
@login_required
def basvuru_dosyasi_sil():
    customer_id = request.form['customer_id'] 
    dosya_id = customer_id

    # Yeni alanın adı ve değeri
    new_field = {"silindi": 1}

    dosya_guncelleme_ekle(dosya_id, "Dosya Silindi.", "otomatik")

    # Belgeyi güncelle
    customers.update_one({"_id": ObjectId(customer_id)}, {"$set": new_field})   
    return jsonify({'success': True})

#############################################################


######## İSTATİSTİK VERİLER İÇİN SERVİSLER BAŞLANGIÇ ############
@app.route('/veriler', methods=['GET'])
@login_required
@yonetici_gerekli
def veriler():

    query = {"status": "Kullandırıldı", "silindi": {"$ne": 1}}
    projection = {"saha_personeli": 1, "komisyon_geliri": "$kullandirim_bilgileri.net_gelir", "tarih": "$created_time"}

    # Sorguyu çalıştırma ve sonuçları alın
    data = list(customers.find(query, projection))

    # Başlangıç tarihi ve bitiş tarihi belirleniyor
    start_date = date(2021, 1, 1)
    end_date = date.today()

    # Tarihlere ait ay-sayı-yıl formatı için string dönüşümü yapılıyor
    months_dict = OrderedDict()
    while start_date < end_date:
        date_str = start_date.strftime('%m-%Y')
        months_dict[date_str] = []
        # Bir sonraki ay için yeni bir tarih hesaplanıyor
        if start_date.month == 12:
            start_date = start_date.replace(year=start_date.year+1, month=1)
        else:
            start_date = start_date.replace(month=start_date.month+1)

    
    # gelirler
    for item in data:
        # print (item["tarih"])
        created_time = datetime.fromisoformat(str(item["tarih"]))
        tarih = created_time.strftime("%m-%Y")

        saha_sorumlusu = item['saha_personeli']

        if 'komisyon_geliri' in item and item['komisyon_geliri']:
            komisyon_geliri = item['komisyon_geliri']
            komisyon_geliri = komisyon_geliri.replace(".", "")  # Remove any existing dots
            komisyon_geliri = komisyon_geliri.replace(",", ".")  # Replace comma with dot
            komisyon_geliri = float(komisyon_geliri)  # Convert to a float
        else:
            komisyon_geliri = 0  # Set a default value

        months_dict[tarih].append({
            'saha_sorumlusu': saha_sorumlusu,
            'komisyon_geliri': komisyon_geliri,
            'harcama': 0
        })
    

    #giderler
    query = {}
    projection = {"saha_personeli": "$harcama_kisi_secimi", "harcama": "$tutar", "tarih": "$harcama_tarihi"}

    # Sorguyu çalıştırma ve sonuçları alın
    data2 = list(harcamalar_db.find(query, projection))
    
    for item in data2:
        # print (item["tarih"])
        dt = datetime.strptime(item["tarih"], "%d.%m.%Y")
        tarih = dt.strftime("%m-%Y")

        saha_sorumlusu = item['saha_personeli']
        
        months_dict[tarih].append({
            'saha_sorumlusu': saha_sorumlusu,
            'komisyon_geliri': 0,
            'harcama': int(item['harcama'])
        })

    # print(months_dict)
    # Verileri JSON formatına dönüştürün ve istemciye gönderin.
    json_data = json.dumps(months_dict)
    return json_data

@app.route('/api/veriler_banka', methods=['GET'])
@login_required
@yonetici_gerekli
def verilerBanka():

    result = customers.aggregate([
        { '$group': {
            '_id': {
                'durum': '$durum',
                'year_month': { '$dateToString': { 'format': '%m-%Y', 'date': '$created_time' } }
            },
            'count': { '$sum': 1 }
        }}
    ])

    output = {}
    for r in result:
        year_month = r['_id']['year_month']
        if 'durum' in r['_id']:
            durum_dict = r['_id']['durum']
            for k, v in durum_dict.items():
                if year_month not in output:
                    output[year_month] = {}
                if k not in output[year_month]:
                    output[year_month][k] = {'onay': 0, 'red': 0}
                output[year_month][k]['red'] += r['count'] if v == 'red' else 0
                output[year_month][k]['onay'] += r['count'] if v == 'onay' else 0

    json_output = json.dumps(output, indent=4)
    # print(json_output)
    return json_output

@app.route('/api/veriler_banka_v2', methods=['GET'])
@login_required
@yonetici_gerekli
def verilerBankaV2():

    
    result = customers.aggregate([
        { '$group': {
            '_id': {
                'durum': '$durum',
                'year_month': { '$dateToString': { 'format': '%m-%Y', 'date': '$created_time' } }
            },
            'count': { '$sum': 1 }
        }}
    ])

    output = {}
    for r in result:
        year_month = r['_id']['year_month']
        if 'durum' in r['_id']:
            durum_dict = r['_id']['durum']
            for k, v in durum_dict.items():
                if year_month not in output:
                    output[year_month] = {}
                if k not in output[year_month]:
                    output[year_month][k] = {'onay': 0, 'red': 0}
                output[year_month][k]['red'] += r['count'] if v == 'red' else 0
                output[year_month][k]['onay'] += r['count'] if v == 'onay' else 0

    
    

    # banka toplamlari hesapla
    # Sorgu
    pipeline = [
        {
            '$match': {'status': 'Kullandırıldı'}
        },
        {
            '$group': {
                '_id': {
                    'month': {'$dateToString': {'format': '%m', 'date': '$created_time'}},
                    'year': {'$dateToString': {'format': '%Y', 'date': '$created_time'}}
                },
                'bankalar': {
                    '$push': '$kullandirim_bilgileri.banka_kullandirim'
                }
            }
        },
        {
            '$unwind': '$bankalar'
        },
        {
            '$group': {
                '_id': {
                    'month': '$_id.month',
                    'year': '$_id.year',
                    'banka': '$bankalar'
                },
                'sayi': {'$sum': 1}
            }
        },
        {
            '$group': {
                '_id': {
                    'month': '$_id.month',
                    'year': '$_id.year'
                },
                'bankalar': {
                    '$push': {
                        'banka': '$_id.banka',
                        'sayi': '$sayi'
                    }
                }
            }
        },
        {
            '$project': {
                '_id': 0,
                'month': {'$concat': ['$_id.month', '-', '$_id.year']},
                'bankalar': 1
            }
        }
    ]

    results = list(customers.aggregate(pipeline))

    # Sonuçları formatlayarak istediğiniz şekilde görüntüleme
    formatted_result = {}
    for item in results:
        key = item['month']
        bankalar = {}
        for banka in item['bankalar']:
            banka_adi = banka['banka']
            sayi = banka['sayi']
            bankalar[banka_adi] = {'kullanim': sayi}
        formatted_result[key] = bankalar

    # print(formatted_result)
    # print('-------------------------------------')
    # print(output)

    # iki veriyi birlestir
    birlesik_veri = {}

    # İlk veri setini birleşik veriye ekleyelim
    for tarih, veri in output.items():
        if tarih not in birlesik_veri:
            birlesik_veri[tarih] = {}
        for banka, degerler in veri.items():
            if banka not in birlesik_veri[tarih]:
                birlesik_veri[tarih][banka] = {}
            birlesik_veri[tarih][banka].update(degerler)

    # İkinci veri setini birleşik veriye ekleyelim veya güncelleyelim
    for tarih, veri in formatted_result.items():
        if tarih not in birlesik_veri:
            birlesik_veri[tarih] = {}
        for banka, degerler in veri.items():
            if banka not in birlesik_veri[tarih]:
                birlesik_veri[tarih][banka] = {}
            if banka in birlesik_veri[tarih]:
                birlesik_veri[tarih][banka].update(degerler)
            else:
                birlesik_veri[tarih][banka] = degerler

    # İlgili fonksiyonu tanımlayalım
    def update_bank_values(veri):
        for tarih, veri_tarih in veri.items():
            for banka, degerler in veri_tarih.items():
                if 'onay' not in degerler:
                    veri_tarih[banka]['onay'] = 0
                if 'red' not in degerler:
                    veri_tarih[banka]['red'] = 0
                if 'kullanim' not in degerler:
                    veri_tarih[banka]['kullanim'] = 0

    # İlk veri setinde eksik değerleri güncelleyelim
    update_bank_values(birlesik_veri)


    # print(birlesik_veri)
    # json_output = json.dumps(output, indent=4)
    json_output = json.dumps(birlesik_veri, indent=4)
    
    # print(json_output)
    return json_output

@app.route('/api/arac_kullanim', methods=['GET'])
@login_required
@yonetici_gerekli
def aracKullanim():
    # Belge sorgusu
    query = {"status": "Kullandırıldı"}

    # Sadece "marka_adi" ve "tip_adi" alanlarını getirin
    projection = {"model_yili":1,"marka_adi": 1, "tip_adi": 1, "banka": "$kullandirim_bilgileri.banka_kullandirim" ,"dosya_numarasi":1 , "kredi_tutar": "$kullandirim_bilgileri.kredi" ,"_id": 0}

    # Belgeyi bulun ve projeksiyonu uygulayın
    documents = customers.find(query, projection)

    # Belge verilerini bir liste olarak toplayın
    result = []
    for document in documents:
        result.append(document)

    # Sonucu JSON olarak dönün
    return jsonify(result)


@app.route('/api/kullanicilar-istatistik')
def chart_data_kullanicilar():
    # Tüm dokümanları çek
    docs = users_collection.find()

    # Aylık değişim bilgileri için liste oluştur
    month_data = {}

    # Dokümanların her biri için işlem yap
    for doc in docs:
        # Yetki alanı
        yetki = doc['yetki']
            
        # _id alanının zaman damgası
        timestamp = int(doc['_id'].generation_time.timestamp())
            
        # Zaman damgasını tarih formatına dönüştür
        date = datetime.fromtimestamp(timestamp)
            
        # Tarihi aylık olarak yuvarla
        month_str = date.strftime('%m-%Y')
            
        # Aylık değişim bilgileri listesine ekle
        if month_str not in month_data:
            month_data[month_str] = {}
        if yetki not in month_data[month_str]:
            month_data[month_str][yetki] = 1
        else:
            month_data[month_str][yetki] += 1

    # Aylık değişim bilgilerini JSON formatında yazdır

    return json.dumps(month_data, indent=4)

    

######## İSTATİSTİK VERİLER İÇİN SERVİSLER SONUC ############



if __name__ == '__main__':
    app.run(debug=True)
