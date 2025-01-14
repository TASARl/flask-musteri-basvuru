// Dosya Guncellemeleri Bolumundeki verilerin yenilenmesi icin fonksiyon olarak cagirilabilir
// guncelemeler sayfasindaki timeline yenilemek ve getirmek icin. guncellemelr ıcınde yapılan her ıslemden sonra sayfa ıcerıgını yenılemesı ıcın cagırılır
const getDosyaGuncellemeleri = function (dosya_id) {
  $("#dosya_id_durum").val(dosya_id);
  $.ajax({
    url: "/api/dosya_no_getir",
    method: "GET",
    data: { dosya_id: dosya_id },
    success: function (response) {
      $("#dosyaNumarasi").text(response);
    },
  });

  $.ajax({
    url: "/dosya_guncellemeleri",
    method: "GET",
    data: { dosya_id: dosya_id },
    success: function (data) {
      // Veriyi parse et
      var json_data = JSON.parse(data);
      var oncekiDay = 0;
      var oncekiMonth = 0;

      // HTML kodunu oluştur
      var html = '<div class="timeline p-4 block mb-4">';
      for (var i = 0; i < json_data.length; i++) {
        // Tarihten sadece saat kısmını al
        var date = new Date(json_data[i].created_time.$date);
        // Saat, dakika ve saniyeyi al
        var hours = date.getUTCHours() + 3; // UTC saat diliminden Türkiye saat dilimine geçiş yap
        hours = ("0" + hours).slice(-2);
        var minutes = ("0" + date.getMinutes()).slice(-2);
        var seconds = date.getSeconds();

        var year = date.getFullYear();
        var month = ("0" + (date.getMonth() + 1)).slice(-2);
        var day = ("0" + date.getDate()).slice(-2);

        // eger onceki tarihle ayni degilse ekrana yazdir ve onceki degerlere ata
        if (day !== oncekiDay || month !== oncekiMonth) {
          oncekiDay = day;
          oncekiMonth = month;
          html += '<div class="tl-item">';
          html += '<div class="tl-dot b-white"></div>';
          html += '<div class="tl-content">';
          html +=
            '<div class="fw-bold text-gray-800 fs-6">' +
            day +
            "/" +
            month +
            "/" +
            year +
            "</div>";
          html += "</div></div>";
        }

        html += '<div class="tl-item ' + (i == 0 ? "active" : "") + '">';
        if (json_data[i].status == "kullanici") {
          html += '<div class="tl-dot b-warning"></div>';
        } else if (json_data[i].status == "otomatik") {
          html += '<div class="tl-dot b-primary"></div>';
        } else {
          html += '<div class="tl-dot b-success"></div>';
        }
        html += '<div class="tl-content">';
        html += '<div class="">' + json_data[i].inputValue + "</div>";
        html +=
          '<div class="tl-date text-muted mt-1">' +
          hours +
          ":" +
          minutes +
          "</div>";
        html +=
          '<div><small class="text-muted">Ekleyen: ' +
          json_data[i].isim_soyisim +
          "</small></div>";
        html += "</div>";
        html += "</div>";
      }
      html += "</div>";

      // HTML kodunu sayfaya ekle
      $("#eklenecekGuncellemeler").html(html);
    },

    error: function (xhr, status, error) {
      console.error(error);
    },
  });

  // "secim-yok" olan tüm radio butonlarını seçmek için
  $('input[value="secim-yok"]:radio').prop("checked", true);

  // AJAX isteği ile databseden seçili olan  Bankalar radio butonlarını getirip işaretlemek için banka yanlari
  $.ajax({
    url: `/radio-data`,
    method: "GET",
    data: { dosya_id: dosya_id },
    success: function (data) {
      // Dönen verileri kullanarak radyo düğmelerini işaretleyin
      for (let name in data) {
        const value = data[name];
        const radioBtn = $(`input[name=${name}][value=${value}]`);
        if (radioBtn.length > 0) {
          radioBtn.prop("checked", true);
        }
      }
    },
    error: function (xhr, status, error) {
      console.error(error);
    },
  });

  // ajax ile kullandirim bilgilerini cekip ilgili yerlere yaz bu bolum kredi kullandirim sonrasi doldurulan bilgiler
  $.ajax({
    url: `/kredi-kullandir`,
    method: "GET",
    data: { dosya_id: dosya_id },
    success: function (data) {
      $("#kredi").val(data.kredi);
      $("#bayi-odemesi").val(data.bayi_odemesi);
      $("#noter").val(data.noter);
      $("#saha-ekibi").val(data.saha_ekibi);
      $("#bayi").val(data.bayi);
      $("#kredi-primi").val(data.kredi_primi);
      $("#kullandirim").val(data.kullandirim);
      $("#banka_kullandirim").val(data.banka_kullandirim).trigger("change");
      $("#kullandirim_tarihi").val(data.kullandirim_tarihi).trigger("change");
      $("#net-gelir").val(data.net_gelir);
    },
    error: function (xhr, status, error) {
      console.error(error);
    },
  });

  // ajax ile dosyadurumu radyo butonlari secimi: kullandırıldı devam sonlandi
  $.ajax({
    url: `/dosya-durum-data`,
    method: "GET",
    data: { dosya_id: dosya_id },
    success: function (data) {
      // Tüm radyo butonlarını seçin
      var radyoButonlari = document.querySelectorAll(
        'input[name="dosya_durumu"]'
      );

      // Her bir radyo butonu için döngü oluşturun
      radyoButonlari.forEach(function (radyoButonu) {
        // Radyo butonunun parent label elementini alın
        var parentLabel = radyoButonu.parentNode;

        // Parent label elementinde "active" sınıfı varsa kaldırın
        if (parentLabel.classList.contains("active")) {
          parentLabel.classList.remove("active");
        }
      });

      // Seçili olan radyo butonunun parent label elementini bulun
      var seciliRadioParentLabel = document.querySelector(
        'input[name="dosya_durumu"][value="' + data + '"]'
      ).parentNode;

      // Parent label elementine "active" sınıfını ekleyin
      seciliRadioParentLabel.classList.add("active");

      // kullandıırldı seçili ise gizli olan ödemeler bölümünü göster gizle
      if (
        $('input[name="dosya_durumu"][value="Kullandırıldı"]')
          .parent()
          .hasClass("active")
      ) {
        $("#hiddenDiv").show();
      } else {
        $("#hiddenDiv").hide();
      }
    },
    error: function (xhr, status, error) {
      console.error(error);
    },
  });
};

(() => {
  // ustte cıkan kaydedıldı yada hata mesajlarının ayarları
  toastr.options = {
    closeButton: true,
    debug: false,
    newestOnTop: false,
    progressBar: true,
    positionClass: "toastr-top-center",
    preventDuplicates: false,
    onclick: null,
    showDuration: "300",
    hideDuration: "1000",
    timeOut: "5000",
    extendedTimeOut: "1000",
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut",
  };

  // Dosya Guncellemeleri bolumde aciklama ekleme butonuna basinca yapilacaklar
  $(document).ready(function () {
    $("#submitButtonGuncelle").on("click", function (event) {
      event.preventDefault(); // Prevent default form submission behavior

      // Get the input value
      const inputValue = $("#myInputGuncelle").val();
      const dosya_id_durum = $("#dosya_id_durum").val();

      // Check if input value is empty
      if (inputValue === "") {
        toastr.error("Açıklama boş olamaz.", "Hata");
        return; // Exit the function if input is empty
      }
      $(this).attr("data-kt-indicator", "on");

      // Make an AJAX request with the input value
      $.ajax({
        url: "/dosya_guncellemeleri",
        method: "POST",
        contentType: "application/json", // Set content type header
        data: JSON.stringify({ dosya_id: dosya_id_durum, inputValue }), // Convert data to JSON string
        success: function (response) {
          $("#myInputGuncelle").val(""); // Clear the input field after successful submission
          $("#submitButtonGuncelle").removeAttr("data-kt-indicator");

          toastr.success("Açıklama eklendi.", "Kayıt edildi");

          getDosyaGuncellemeleri(dosya_id_durum);
        },
        error: function (xhr, status, error) {
          console.log("hata var");
        },
      });
    });
  });

  // Kredi Dosyaları listesinde Dosya durumları guncelleme butonuna basınca
  const buttons_guncelle = $(".dosyaDurumButonu");
  buttons_guncelle.each(function () {
    $(this).click(function () {
      const dosya_id = $(this).data("customerid");
      getDosyaGuncellemeleri(dosya_id);
    });
  });

  // bankalarin yanindaki radi butonlarinin secip arka plana ajax ıle gondermek ıcın
  // Get all radio buttons with class 'form-check-input'
  const radioButtons = document.querySelectorAll(".form-check-input");

  // Loop through all radio buttons
  radioButtons.forEach((button) => {
    // Add a click event listener to each radio button
    button.addEventListener("click", () => {
      // Get the name and value of the clicked radio button
      const name = button.getAttribute("name");
      const value = button.getAttribute("value");
      var document_id = $("#dosya_id_durum").val(); // Değiştirilecek belgenin ID'si

      $.ajax({
        url: "/radio-data",
        method: "POST",
        contentType: "application/json", // Set content type header
        data: JSON.stringify({
          dosya_id: document_id,
          name: name,
          value: value,
        }), // Convert data to JSON string
        success: function (response) {
          toastr.success(
            "Banka dosya bilgi güncellemesi kayıt edildi.",
            "Kayıt edildi"
          );

          getDosyaGuncellemeleri(document_id);
        },
        error: function (xhr, status, error) {
          console.log("hata var");
        },
      });
    });
  });
})();

(() => {
  // kullandırım sonrası kar hesaplama
  const krediInput = document.querySelector("#kredi");
  const bayiOdemesiInput = document.querySelector("#bayi-odemesi");
  const noterInput = document.querySelector("#noter");
  const sahaEkibiInput = document.querySelector("#saha-ekibi");
  const bayiInput = document.querySelector("#bayi");
  const krediPrimiInput = document.querySelector("#kredi-primi");
  const kullandirimInput = document.querySelector("#kullandirim");
  const netGelirInput = document.querySelector("#net-gelir");

  function hesaplaNetGelir() {
    const kredi = parseFloat(krediInput.value) || 0;
    const bayiOdemesi = parseFloat(bayiOdemesiInput.value) || 0;
    const noter = parseFloat(noterInput.value) || 0;
    const sahaEkibi = parseFloat(sahaEkibiInput.value) || 0;
    const bayi = parseFloat(bayiInput.value) || 0;
    const krediPrimi = parseFloat(krediPrimiInput.value) || 0;
    const kullandirim = parseFloat(kullandirimInput.value) || 0;

    const netGelir =
      kredi - bayiOdemesi - noter - sahaEkibi - bayi - krediPrimi - kullandirim;

    netGelirInput.value = netGelir.toLocaleString("tr-TR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  krediInput.addEventListener("input", hesaplaNetGelir);
  bayiOdemesiInput.addEventListener("input", hesaplaNetGelir);
  noterInput.addEventListener("input", hesaplaNetGelir);
  sahaEkibiInput.addEventListener("input", hesaplaNetGelir);
  bayiInput.addEventListener("input", hesaplaNetGelir);
  krediPrimiInput.addEventListener("input", hesaplaNetGelir);
  kullandirimInput.addEventListener("input", hesaplaNetGelir);
})();

(() => {
  // dosya durumu 3 adet yanyana buton. beklemede, sonuçlandı, kullandırıldı. js ile seçim. secim ile etrafinin cizikli olmasi ve ajax ile veri arkaplana gonder
  const radioButtonsKullandirim = document.querySelectorAll(
    'input[name="dosya_durumu"]'
  );

  radioButtonsKullandirim.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons
      radioButtonsKullandirim.forEach((btn) => {
        btn.parentElement.classList.remove("active");
      });

      if (button.checked) {
        var document_id = $("#dosya_id_durum").val();
        // Add the active class
        button.parentElement.classList.add("active");
        // Log the value to console
        console.log(button.value);
        var dosya_durum_bilgisi = button.value;

        $.ajax({
          url: "/dosya-durum-data",
          method: "POST",
          contentType: "application/json", // Set content type header
          data: JSON.stringify({
            dosya_id: document_id,
            status: dosya_durum_bilgisi,
          }),
          success: function (response) {
            toastr.success("Dosya durumu güncellendi.", "Kayıt edildi");

            getDosyaGuncellemeleri(document_id);
          },
          error: function (error) {
            console.error(error);
          },
        });
      } else {
        // Remove the active class
        button.parentElement.classList.remove("active");
      }
    });
  });
})();

// kredi kullandirim sonrasi detaylarin kayit edilmesi
$("#kredi_kullandirildi_butonu").click(function () {
  // Activate indicator
  $(this).attr("data-kt-indicator", "on");

  var document_id = $("#dosya_id_durum").val(); // Değiştirilecek belgenin ID'si

  var kredi = $("#kredi").val();
  var bayiOdemesi = $("#bayi-odemesi").val();
  var noter = $("#noter").val();
  var sahaEkibi = $("#saha-ekibi").val();
  var bayi = $("#bayi").val();
  var krediPrimi = $("#kredi-primi").val();
  var kullandirim = $("#kullandirim").val();
  var bankaKullandirim = $("#banka_kullandirim").val();
  var kullandirim_tarihi = $("#kullandirim_tarihi").val();
  var netGelir = $("#net-gelir").val();

  $.ajax({
    url: "/kredi-kullandir",
    method: "POST",
    contentType: "application/json", // Set content type header
    data: JSON.stringify({
      document_id: document_id,
      kredi: kredi,
      bayi_odemesi: bayiOdemesi,
      noter: noter,
      saha_ekibi: sahaEkibi,
      bayi: bayi,
      kredi_primi: krediPrimi,
      kullandirim: kullandirim,
      banka_kullandirim: bankaKullandirim,
      kullandirim_tarihi: kullandirim_tarihi,
      net_gelir: netGelir,
    }),
    success: function (response) {
      console.log(response);

      toastr.success(
        "Kredi kullandırım bilgileri kayıt edildi.",
        "Kayıt edildi"
      );

      $("#kredi_kullandirildi_butonu").removeAttr("data-kt-indicator");

      getDosyaGuncellemeleri(document_id);
    },
    error: function (error) {
      $("#kredi_kullandirildi_butonu").removeAttr("data-kt-indicator");
      console.error(error);
    },
  });
});

// gizli olan kullandırıldı bolumunu butona tıklandıgında gosterip gizler
$(document).ready(function () {
  $('input[name="dosya_durumu"]').change(function () {
    if ($(this).val() == "Kullandırıldı") {
      $("#hiddenDiv").show();
      $("#kt_modal_durum_guncelle .modal-body").animate(
        {
          scrollTop:
            $("#kt_modal_durum_guncelle .modal-body").scrollTop() + 400,
        },
        500
      );
    } else {
      $("#hiddenDiv").hide();
    }
  });
});

$(function () {
  // bir sonraki kod icin sol cigideki renk siniflarini kaldirir
  const removeBackgroundClasses = function (element, yeniArkaplan) {
    if (element.classList.contains("bg-success")) {
      element.classList.remove("bg-success");
    }

    if (element.classList.contains("bg-primary")) {
      element.classList.remove("bg-primary");
    }

    if (element.classList.contains("bg-warning")) {
      element.classList.remove("bg-warning");
    }

    if (element.classList.contains("bg-danger")) {
      element.classList.remove("bg-danger");
    }

    element.classList.add(yeniArkaplan);
  };

  // sayfadaki guncellemelerde animasyonlu gecis ekler
  var fadeAnimasyonuIleHtmlDegistir = function (td, htmlCode) {
    // td öğesinin opacity değerini 0.5 yaparak eski içeriği bulanıklaştırın
    td.style.opacity = "0.5";

    // setTimeout fonksiyonu kullanarak eski içeriği silin ve yeni içeriği ekleme işlemini birkaç saniye geciktirin
    setTimeout(function () {
      td.innerHTML = "";
      td.insertAdjacentHTML("beforeend", htmlCode);

      // Yeni içeriği ekledikten sonra, td öğesinin opacity değerini 1'e kadar arttırarak animasyonlu bir şekilde görünür hale getirin
      var op = 0.5;
      var timer = setInterval(function () {
        if (op >= 1) {
          clearInterval(timer);
        }
        td.style.opacity = op.toString();
        op += 0.1;
      }, 50);
    }, 500); // 500ms'lik bir gecikme süresi belirleyerek eski içeriği silme ve yeni içeriği ekleme işlemine daha belirgin bir geçiş sağlayabilirsiniz
  };

  // durum guncellemeleri icin durum iclerindeki tum idleri ajax ile gonder yeni verileri al ekrana ekle

  const sayfaDosyaBilgileriGuncelleme = function () {
    var customerIds = [];
    $("td[data-customer-id]").each(function () {
      var customerId = $(this).data("customer-id");
      if (customerId) {
        customerIds.push(customerId);
      }
    });

    if (customerIds.length === 0) {
      return;
    }

    $.ajax({
      url: "/process_customer_ids",
      method: "POST",
      contentType: "application/json", // Set content type header
      data: JSON.stringify({ customerIds: customerIds }),
      success: function (data) {
        for (var i = 0; i < data.results.length; i++) {
          var dosya_id = data.results[i].dosya_id;
          var aciklama = data.results[i].aciklama;
          var bankalar = data.results[i].bankalar;
          var durum_dosya = data.results[i].durum;

          var htmlAciklama = "";
          if (
            aciklama &&
            aciklama.inputValue !== null &&
            aciklama.inputValue !== undefined
          ) {
            htmlAciklama = aciklama.inputValue;
          }

          // td öğesini bulun ve içeriğini güncelleyin
          var td = document.querySelector(
            'td[data-customer-id="' + dosya_id + '"]'
          );
          var solCizgi = document.querySelector(
            'div[data-customer-id="' + dosya_id + '"].solCizgi'
          );

          // Bankaları gösteren yeni bir liste oluşturun
          var banka_listesi = "";
          if (bankalar !== null) {
            for (var banka in bankalar) {
              if (bankalar.hasOwnProperty(banka)) {
                var durum = bankalar[banka];
                var banka_adi = banka.replace("-", " ").toUpperCase();
                if (durum === "basvuruldu") {
                  banka_listesi +=
                    '<span class="badge badge-light-warning">' +
                    banka_adi +
                    "</span>";
                }
                if (durum === "red") {
                  banka_listesi +=
                    '<span class="badge badge-light-danger">' +
                    banka_adi +
                    "</span>";
                }
                if (durum === "onay") {
                  banka_listesi +=
                    '<span class="badge badge-light-success">' +
                    banka_adi +
                    "</span>";
                }
              }
            }
          } else {
            banka_listesi +=
              '<span class="badge badge-secondary">Giriş Yapılmadı</span>';
          }

          let renk = "";
          if (durum_dosya === "Kullandırıldı") {
            renk = "success";
            removeBackgroundClasses(solCizgi, "bg-success");
          }
          if (durum_dosya === "Kullandırılacak") {
            renk = "primary";
            removeBackgroundClasses(solCizgi, "bg-primary");
          }
          if (durum_dosya === "Devam") {
            renk = "warning";
            removeBackgroundClasses(solCizgi, "bg-warning");
          }
          if (durum_dosya === "Sonlandı") {
            renk = "danger";
            removeBackgroundClasses(solCizgi, "bg-danger");
          }

          const htmlCode = `
                <div class="">
                    
                    <div class="d-flex flex-stack">
                        <div class=" d-block mb-1 fs-6">${banka_listesi}</div>
                        <div class="d-flex align-items-senter">
                            <span class="badge badge-${renk} badge-lg ">${durum_dosya}</span>
                        </div>
                    </div>

                    <div class="separator separator-dashed my-3"></div>

                    <div class="d-flex flex-stack">
                        
                        
                        <span class="class="fw-semibold fw-bold  mb-1  fs-7"">${htmlAciklama}</span>
                        </div>
                    </div>

                </div>
                `;

          // td.innerHTML = "";
          // td.insertAdjacentHTML('beforeend', htmlCode);
          fadeAnimasyonuIleHtmlDegistir(td, htmlCode);
        }
        startAnimation();
      },
      error: function (xhr, status, error) {
        console.log("Hata:", error);
      },
    });
  };

  sayfaDosyaBilgileriGuncelleme(); // Fonksiyon hemen çağrılır

  const intervalId = setInterval(sayfaDosyaBilgileriGuncelleme, 60000); // Her 60 saniyede bir fonksiyon yenilenir

  // sayfanin yenilendigini gostermek icin loading dairesi
  let progressElem = document.querySelector(".progress-elem");
  let progressElemSvg = document.querySelector(".progress-elem svg");
  let progressBar = document.querySelector(".progress-bar");
  let success = document.querySelector(".success");

  let interval;
  function startAnimation() {
    clearInterval(interval);

    success.style.display = "none";

    let initial = 251.3274;
    let increment = 251.3274 / 100;
    let incrementCount = 0;
    interval = setInterval(() => {
      if (incrementCount === 100) {
        initial = 0;
        progressBar.style.strokeDashoffset = initial;
        clearInterval(interval);
        setTimeout(() => {
          success.style.display = "";
        }, 100);
      } else {
        initial -= increment;
        progressBar.style.strokeDashoffset = initial;
        incrementCount += 1;
      }
    }, 600);
  }

  startAnimation();

  // donen tekere basinca verileri gunceller
  document
    .querySelector(".loading-buton-guncelleme")
    .addEventListener("click", function () {
      sayfaDosyaBilgileriGuncelleme();
      startAnimation();
    });
});

(() => {
  $(document).ready(function () {
    // Select kutuları
    //sayfa yukelndığinde adres satırından parametreleri al ve selec boxlara ekle
    let url = new URL(window.location.href);
    let urlParams = new URLSearchParams(url.search);

    const adresSatirCity = urlParams.get("city") || "Tüm";
    $("#dosyalar_city_selector").val(adresSatirCity).trigger("change");

    const adresSatirDurum = urlParams.get("durum") || "Hepsi";
    $("#dosyalar_durum_selector").val(adresSatirDurum).trigger("change");

    const adresSatirPersonel = urlParams.get("personel") || "Hepsi";
    $("#dosyalar_saha_personel_selector")
      .val(adresSatirPersonel)
      .trigger("change");

    const adresSatirArama = urlParams.get("arama") || "";
    $("#search").val(adresSatirArama).trigger("change");

    const kilitDeger = 1;

    // dosyalar bolumunda sehir secildigindee adres satirinda varsa degerleri degistir yoksa yeni deger ekle
    $("#dosyalar_city_selector").change(function () {
      if (kilitDeger === 1) {
        // Seçilen değer
        var selectedValue = $("#dosyalar_city_selector").val();

        // Yeni URL oluşturulur
        //   var newUrl = window.location.href + "&city=" + selectedValue;

        url.searchParams.set("city", selectedValue);
        url.searchParams.set("page", "1");

        // Sayfa yeniden yüklenir
        window.location.href = url;
      }
    });

    // dosyalar bolumunda durum secildigindee adres satirinda varsa degerleri degistir yoksa yeni deger ekle
    $("#dosyalar_durum_selector").change(function () {
      // Seçilen değer
      var selectedValue = $("#dosyalar_durum_selector").val();

      // Yeni URL oluşturulur
      //   var newUrl = window.location.href + "&city=" + selectedValue;
      let url = new URL(window.location.href);
      url.searchParams.set("durum", selectedValue);
      url.searchParams.set("page", "1");

      // Sayfa yeniden yüklenir
      window.location.href = url;
    });

    // dosyalar bolumunda durum secildigindee adres satirinda varsa degerleri degistir yoksa yeni deger ekle
    $("#dosyalar_saha_personel_selector").change(function () {
      // Seçilen değer
      var selectedValue = $("#dosyalar_saha_personel_selector").val();

      // Yeni URL oluşturulur
      //   var newUrl = window.location.href + "&city=" + selectedValue;
      let url = new URL(window.location.href);
      url.searchParams.set("personel", selectedValue);
      url.searchParams.set("page", "1");

      // Sayfa yeniden yüklenir
      window.location.href = url;
    });

    $("#aramaYapButonu").click(function (event) {
      event.preventDefault();
      const searchValue = $("#search").val();
      const url = new URL(window.location.href);
      url.searchParams.set("arama", searchValue);
      url.searchParams.set("page", 1);
      window.location.href = url.toString();
    });
  });

  // kullandırım altındakı tarih secimi icin
  $("#kullandirim_tarihi").daterangepicker({
    singleDatePicker: true,
    showDropdowns: false,
    autoApply: true,
    locale: {
      format: "DD.MM.YYYY",
    },
  });

  // harcama sil butonu basıldıgında yapılacaklar
  $(document).ready(function () {
    $(".musteri_dosya_sil_butonu").click(function (event) {
      event.preventDefault();
      var customer_id = $(this).data("customer_id");

      // Uyarı penceresi göstermek için
      if (
        confirm(
          "Dosya silme islemini yapmak istediğinizden emin misiniz? Silme işlemi sonrası tüm dosya bilgileri veritababında tutulamaya devam edicek ancak kullanıcılar dosyayı goremeyecektir."
        )
      ) {
        $.ajax({
          type: "POST",
          url: "/basvuru_dosyasi_sil", // Silme işlemini yapacak PHP dosyasının adı ve yolunu buraya yazmalısınız.
          data: { customer_id: customer_id },
          success: function (response) {
            $('tr[data-customer-id="' + customer_id + '"]').remove();
          },
          error: function (xhr, status, error) {
            console.log(xhr.responseText);
          },
        });
      }
    });
  });
})();
