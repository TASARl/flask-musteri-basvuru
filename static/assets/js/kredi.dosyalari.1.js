(() => {
  // tarihi kisa goster
  const createdTimeElements = document.querySelectorAll(".createdTime");
  for (let i = 0; i < createdTimeElements.length; i++) {
    const date = new Date(createdTimeElements[i].textContent);
    const formattedDate = `${date.getDate().toString().padStart(2, "0")}/${(
      date.getMonth() + 1
    )
      .toString()
      .padStart(2, "0")}/${date.getFullYear().toString()}`;
    createdTimeElements[i].textContent = formattedDate;
  }
})();

//secili dosyayı degıstırme masaustu uygulamasi icin
const addSelectedCustomer = function (event, customerId) {
  event.preventDefault();
  $.ajax({
    url: "/add_customer_selection",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ customer_id: customerId }),
    success: function (response) {
      //alert("Müşteri seçimi kaydedildi!");
      $("tr[data-customer-id]").css("background-color", "");
      $('tr[data-customer-id="' + customerId + '"]').css(
        "background-color",
        "#daf3ff"
      );
      //   window.location.reload();
    },
    error: function (error) {
      alert("Hata oluştu!");
      console.log(error);
    },
  });
};

(() => {
  // Edit Modal içine dosya id si ve verileri gonderme
  const buttons = document.querySelectorAll(".dosyaButonu");
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      dosya_id = button.dataset.customerid;

      document
        .querySelector('[data-kt-element="files-next"]')
        .querySelector(".indicator-label").textContent = "Kaydet";

      dosya_numarasi = button.dataset.dosya_numarasi;
      document.getElementById("modal_dosya_baslik").innerHTML =
        '<h2 id="modal_dosya_baslik">' +
        dosya_numarasi +
        ' Numarali Kredi Dosyası Düzenle<small class="ms-2 fs-7 fw-normal opacity-50"></small></h2>';

      $.ajax({
        url: "/id_ile_dosya_bilgisi_getir", // buradaki URL'yi API URL'inizle değiştirin
        type: "GET",
        data: {
          dosya_id: dosya_id,
        },
        success: function (response) {
          var data = JSON.parse(response);
          $("#dosya_id").val(dosya_id);
          $('select[name="il_secimi_is"]')
            .val(data.il_secimi_is)
            .trigger("change");
          $('select[name="vergi_dairesi_il"]')
            .val(data.vergi_dairesi_il)
            .trigger("change");
          $('select[name="il_secimi_ev"]')
            .val(data.il_secimi_ev)
            .trigger("change");
          $('select[name="model_yili"]').val(data.model_yili).trigger("change");
          $('select[name="saha_personeli"]')
            .val(data.saha_personeli)
            .trigger("change");

          $('input[name="galeri_telefonu"]')
            .val(data.galeri_telefonu)
            .trigger("input");

          $('input[name="sasi_no"]').val(data.sasi_no);
          $('input[name="motor_no"]').val(data.motor_no);
          $('input[name="tescil_belge_no"]').val(data.tescil_belge_no);
          $('input[name="arac_plakasi"]').val(data.arac_plakasi);
          $('input[name="arac_satis_tutari"]').val(data.arac_satis_tutari);
          $('input[name="kredi_tutari"]').val(data.kredi_tutari);
          $('input[name="kredi_vadesi"]').val(data.kredi_vadesi);
          $('input[name="musteri_cep_telefonu"]').val(
            data.musteri_cep_telefonu
          );
          $('input[name="tc"]').val(data.tc);
          $('input[name="adi"]').val(data.adi);
          $('input[name="soyadi"]').val(data.soyadi);
          $('input[name="kimlik_seri"]').val(data.kimlik_seri);
          $('input[name="dogum_tarihi"]').val(data.dogum_tarihi);
          $('select[name="egitim_durumu"]')
            .val(data.egitim_durumu)
            .trigger("change");
          $('select[name="meslek_gurubu"]')
            .val(data.meslek_gurubu)
            .trigger("change");
          $('select[name="meslek"]').val(data.meslek).trigger("change");
          $('input[name="aylik_gelir"]').val(data.aylik_gelir);
          $('select[name="sosyal_guvenlik"]')
            .val(data.sosyal_guvenlik)
            .trigger("change");
          $('select[name="sektor"]').val(data.sektor).trigger("change");
          $('input[name="calisma_suresi_yil"]').val(data.calisma_suresi_yil);
          $('input[name="calisma_suresi_ay"]').val(data.calisma_suresi_ay);

          $('input[name="vergi_no"]').val(data.vergi_no);
          $('select[name="ikamet_tipi"]')
            .val(data.ikamet_tipi)
            .trigger("change");

          $('input[name="mahalle_ev"]').val(data.mahalle_ev);
          $('input[name="ikamet_sure_ev"]').val(data.ikamet_sure_ev);
          $('textarea[name="acik_adres_ev"]').val(data.acik_adres_ev);
          $('input[name="isyeri_adi"]').val(data.isyeri_adi);
          $('input[name="isyeri_telefonu"]').val(data.isyeri_telefonu);

          $('input[name="mahalle_is"]').val(data.mahalle_is);
          $('textarea[name="acik_adres_is"]').val(data.acik_adres_is);
          // digerlerinin degisimi ile ortayacikanlar
          $('input[name="kaskokodu"]').val(data.kaskokodu).trigger("input");
          $('select[name="vergi_dairesi_ilce"]')
            .val(data.vergi_dairesi_ilce)
            .trigger("change");
          $('select[name="ilce_secimi_ev"]')
            .val(data.ilce_secimi_ev)
            .trigger("change");
          $('select[name="ilce_secimi_is"]')
            .val(data.ilce_secimi_is)
            .trigger("change");

          // content classına sahip tüm divleri seçin
          const contentDivs = document.querySelectorAll(
            '[data-kt-stepper-element="content"]'
          );

          // Her bir div için döngü ile geçin
          for (let i = 0; i < contentDivs.length; i++) {
            // İlk div current sınıfına sahip olarak ayarlanır, diğerleri ise pending sınıfına sahip

            contentDivs[i].className = "current";
          }

          const elements = document.querySelectorAll(".edit_bolumu_icin_gizle");
          elements.forEach((element) => {
            element.style.setProperty("display", "none", "important");
          });

          document.querySelector(".dosya_tarihi_secimi_bolumu").style.display =
            "none";

          // saha personeli secilemez
          document.getElementById("saha_personeli").disabled = true;
        },
        error: function (xhr) {
          // hata durumunda burası çalışır
          // console.log(xhr.responseText);
        },
      });
    });
  });
})();
