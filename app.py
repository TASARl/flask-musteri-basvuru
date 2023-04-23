from flask import Flask, render_template, request, jsonify
from bson import json_util
from datetime import datetime


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://user:6UUq1D9BDh7J38y4@clusterkredi.ryzdktr.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


app = Flask(__name__)

@app.route('/')
def anasayfa():
    # index.html adlı template'i döndür
    return render_template('index.html')

@app.route('/form', methods=['POST'])
def form():
    # Formdan gönderilen verileri al
    tc = request.form['tc']
    ad_soyad = request.form['ad_soyad']
    dogum_tarihi = request.form['dogum_tarihi']
    telefon = request.form['telefon']
    email = request.form['email']
    calisma_durumu = request.form['calisma_durumu']
    aylik_net_gelir = request.form['aylik_net_gelir']
    kredi_miktar = request.form['kredi_miktar']
    kredi_vadesi = request.form['kredi_vadesi']
    calisma_sekli = request.form['calisma_sekli']
    il_secimi = request.form['il_secimi']

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
        'tc': tc,
        'ad_soyad': ad_soyad,
        'dogum_tarihi': dogum_tarihi_formatted,
        'telefon': telefon,
        'email': email,
        'calisma_durumu': calisma_durumu,
        'aylik_net_gelir': aylik_net_gelir,
        'calisma_sekli': calisma_sekli,
        'kredi_miktar': kredi_miktar,
        'kredi_vadesi': kredi_vadesi,
        'il_secimi': il_secimi,
        'timestamp': datetime.now()
    }

    db = client.otovitrin
    musteri_collection = db.musteriler

    result = musteri_collection.insert_one(data)

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
    return render_template('kaydedildi.html', tc=tc)


# GET isteği ile müşterileri pagination ile getirme
@app.route('/customers', methods=['GET'])
def get_customers():
    db = client.otovitrin
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

    # JSON'a dönüştür ve döndür
    customer_json = json_util.dumps({'metadata': metadata, 'customers': customer_list})
    
    return render_template('customer.html', data=customer_list , metadata=metadata)

@app.route('/add_customer_selection', methods=['POST'])
def add_customer_selection():
    db = client.otovitrin
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


if __name__ == '__main__':
    app.run(debug=True)
