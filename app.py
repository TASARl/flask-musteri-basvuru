from flask import Flask, render_template, request
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

if __name__ == '__main__':
    app.run(debug=True)
