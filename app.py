from flask import Flask, render_template, request, jsonify
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime

import pymongo
from pymongo import DESCENDING
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from flask import redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import json

import os

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
customers = db.musteriler
users_collection = db['users']
selected_customers = db.selected_customers


# ENV degisken ekle
app = Flask(__name__)
app.secret_key = secret

# Index sayfasi
@app.route('/')
@login_required
def index():
    # index.html adlı template'i döndür
    return render_template('index.html')

# Basvuru Sayfasi
@app.route('/basvuru')
@login_required
def basvuru():
    # index.html adlı template'i döndür
    return render_template('basvuru.html', current_user=current_user.id)

@app.route('/form', methods=['POST'])
@login_required
def form():
    # Formdan gönderilen verileri al
    basvuruTuru = request.form.get('basvuruTuru')
    tc = request.form['tc']
    ad_soyad = request.form['ad_soyad']
    dogum_tarihi = request.form['dogum_tarihi']
    telefon = request.form['telefon']
    email = request.form['email']
    aylik_net_gelir = request.form['aylik_net_gelir']
    kredi_miktar = request.form['kredi_miktar']
    kredi_vadesi = request.form['kredi_vadesi']
    calisma_sekli = request.form['calisma_sekli']
    il_secimi = request.form['il_secimi']
    model_yili = request.form['model_yili']
    marka_adi = request.form['marka_adi']
    tip_adi = request.form['tip_adi']
    kasko_bedeli = request.form.get('kasko_bedeli', 0)
    kaskokodu = request.form.get('kaskokodu', 0)

    # tc = request.form.get('tc', 'boş')
    # ad_soyad = request.form.get('ad_soyad', 'boş')
    # dogum_tarihi = request.form.get('dogum_tarihi')
    # telefon = request.form.get('telefon', 'boş')
    # email = request.form.get('email', 'boş')
    # calisma_durumu = request.form.get('calisma_durumu', 'boş')
    # aylik_net_gelir = request.form.get('aylik_net_gelir', 'boş')
    # kredi_miktar = request.form.get('kredi_miktar', 'boş')
    # kredi_vadesi = request.form.get('kredi_vadesi', 'boş')
    # calisma_sekli = request.form.get('calisma_sekli', 'boş')

    # Dogum tarihi donustur
    if (dogum_tarihi):
        dogum_tarihi_str = dogum_tarihi 
        dogum_tarihi_obj = datetime.strptime(dogum_tarihi_str, '%Y-%m-%d')
        dogum_tarihi_formatted = dogum_tarihi_obj.strftime('%d.%m.%Y')
    else:
        dogum_tarihi_formatted= 0

    data = {
        'basvuruTuru': basvuruTuru,
        'tc': tc,
        'ad_soyad': ad_soyad,
        'dogum_tarihi': dogum_tarihi_formatted,
        'telefon': telefon,
        'email': email,
        'aylik_net_gelir': aylik_net_gelir,
        'calisma_sekli': calisma_sekli,
        'kredi_miktar': kredi_miktar,
        'kredi_vadesi': kredi_vadesi,
        'il_secimi': il_secimi,
        'arac':{'model_yili': model_yili,
        'marka_adi' : marka_adi,
        'tip_adi' : tip_adi,
        'kasko_bedeli': kasko_bedeli,
        'kaskokodu':kaskokodu},
        'timestamp': datetime.now()
    }


    result = customers.insert_one(data)

    document_id = result.inserted_id
    print(f"_id of inserted document {document_id}")


    # # Verileri bir TXT dosyasına yaz
    # dosya_adi = f"{tc}.txt"

    # with open(dosya_adi, "w") as f:
    #     f.write("")

    # with open(dosya_adi, "a") as f:
    #     f.write(f"TC Kimlik Numarası: {tc}\n")
    #     f.write(f"Ad Soyad: {ad_soyad}\n")
    #     f.write(f"Doğum Tarihi: {dogum_tarihi_formatted}\n")
    #     f.write(f"Telefon: {telefon}\n")
    #     f.write(f"E-posta: {email}\n")
    #     f.write(f"Çalışma Durumu: {calisma_durumu}\n")
    #     f.write(f"Aylık Net Gelir: {aylik_net_gelir}\n")
    #     f.write(f"Çalışma Şekli: {calisma_sekli}\n")
    #     f.write(f"Kredi Talep Edilen Miktar: {kredi_miktar}\n")
    #     f.write(f"Kredi Vadesi: {kredi_vadesi}\n")
    #     f.write(f"İl: {il_secimi}\n")

    # Başarılı bir şekilde kaydedildi sayfasını göster
    return render_template('kaydedildi.html', tc=tc, current_user=current_user.id)


# GET isteği ile müşterileri pagination ile getirme
@app.route('/customers', methods=['GET'])
@login_required
def get_customers():
    
    customers = db.musteriler

    # Sayfa numarasını al
    page = int(request.args.get('page', 1))
    # Her sayfada kaç müşteri gösterileceğini belirle
    per_page = int(request.args.get('per_page', 10))

    # Toplam müşteri sayısını al
    total_customers = customers.count_documents({})

    # Pagination hesaplamaları
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_customers)

    # Müşterileri veritabanından getir
    customer_list = list(customers.find({}, {'_id':1, 'tc':1, 'ad_soyad':1, 'dogum_tarihi':1, 'telefon':1, 'email':1, 'calisma_durumu':1, 'aylik_net_gelir':1, 'calisma_sekli':1, 'kredi_miktar':1, 'kredi_vadesi':1, 'il_secimi':1}).sort("_id", -1).skip(start_index).limit(per_page))


    # Pagination metadatasını oluştur
    metadata = {
        'page': page,
        'per_page': per_page,
        'total_customers': total_customers,
        'total_pages': int(total_customers / per_page) + 1
    }

    # Son seçilen müşterinin bilgilerini al
    latest_customer = selected_customers.find().sort([('selection_date', DESCENDING)]).limit(1)
    lstest_customer_id = latest_customer[0]['customer_id']

    # JSON'a dönüştür ve döndür
    customer_json = json_util.dumps({'metadata': metadata, 'customers': customer_list})
    
    return render_template('customer.html', data=customer_list , metadata=metadata, lstest_customer_id=lstest_customer_id)

@app.route('/add_customer_selection', methods=['POST'])
def add_customer_selection():
    
    selected_customers = db.selected_customers

    # İstekten gelen JSON verilerini al
    data = request.get_json()
    customer_id = data['customer_id']
    selection_date = datetime.now()

    # Seçilen müşteriyi selected_customers koleksiyonuna ekle
    result = selected_customers.insert_one({
        'customer_id': customer_id,
        'selection_date': selection_date
    })

    return jsonify(str(result.inserted_id))


@app.route('/secili_musteri', methods=['GET'])
def last_selected_customer():
    
    # Son seçilen müşterinin bilgilerini al
    latest_customer = selected_customers.find().sort([('selection_date', DESCENDING)]).limit(1)
    customer_id = latest_customer[0]['customer_id']

    # Müşteri bilgilerini veritabanından al
    customers = db.musteriler
    customer = customers.find_one({'_id': ObjectId(customer_id)})
    
    if customer is None:
        return jsonify({'message': 'Müşteri bulunamadı.', 'id': customer_id}, 404)


    
    # JSON formatında HTTP yanıtı oluştur
    response = {
        'tc': customer['tc'],
        'ad_soyad': customer['ad_soyad'],
        'dogum_tarihi': customer['dogum_tarihi'],
        'telefon': customer['telefon'],
        'email': customer['email'],
        'aylik_net_gelir': customer['aylik_net_gelir'],
        'calisma_sekli': customer['calisma_sekli'],
        'kredi_miktar': customer['kredi_miktar'],
        'kredi_vadesi': customer['kredi_vadesi'],
        'arac': {
        'model_yili': customer['arac']['model_yili'],
        'marka_adi': customer['arac']['marka_adi'],
        'tip_adi': customer['arac']['tip_adi'],
        'kasko_bedeli': customer['arac']['kasko_bedeli'],
        'kaskokodu': customer['arac']['kaskokodu']}
    }

    json_response = json.dumps(response, ensure_ascii=False)

    return json_response, 200


###### LOGIN BAS ##############

# Flask-Login'in başlatılması
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Kullanıcı model sınıfının oluşturulması
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

    def __repr__(self):
        return f'<User {self.id}>'


# Kullanıcıları veritabanından getirme
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'username': user_id})
    if not user:
        return None
    return User(user['username'], user['password'])


# Kayıt Olma İşlevi
@app.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    if request.method == 'POST':
        # Form verilerini alın
        username = request.form['username']
        password = request.form['password']

        # Kullanıcının mevcut olup olmadığını kontrol edin
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return 'Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.'

        # Şifreyi hashleyin, kullanıcıyı veritabanına kaydedin ve otomatik olarak giriş yapın
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        user = User(username, hashed_password)
        #login_user(user)
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
            user_obj = User(username, user['password'])
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

mydb = client["arabalar"]
modellerDb = mydb["modeller"]

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



if __name__ == '__main__':
    app.run(debug=True)
