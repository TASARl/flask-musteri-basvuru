"use strict";

// Class definition
var KTModalCreateProjectSettings = (function () {
  // Variables
  var nextButton;
  var previousButton;
  var validator;
  var form;
  var stepper;

  // Private functions
  var initForm = function () {
    // Project logo
    // For more info about Dropzone plugin visit:  https://www.dropzonejs.com/#usage
    // var myDropzone = new Dropzone("#kt_modal_create_project_settings_logo", {
    //   url: "https://keenthemes.com/scripts/void.php", // Set the url for your upload script location
    //   paramName: "file", // The name that will be used to transfer the file
    //   maxFiles: 10,
    //   maxFilesize: 10, // MB
    //   addRemoveLinks: true,
    //   accept: function (file, done) {
    //     if (file.name == "justinbieber.jpg") {
    //       done("Naha, you don't.");
    //     } else {
    //       done();
    //     }
    //   },
    // });

    // Due date. For more info, please visit the official plugin site: https://flatpickr.js.org/
    var releaseDate = $(form.querySelector('[name="settings_release_date"]'));
    releaseDate.flatpickr({
      enableTime: true,
      dateFormat: "d, M Y, H:i",
    });

    // Expiry year. For more info, plase visit the official plugin site: https://select2.org/
    $(form.querySelector('[name="settings_customer"]')).on(
      "change",
      function () {
        // Revalidate the field when an option is chosen
        validator.revalidateField("settings_customer");
      }
    );
  };

  var initValidation = function () {
    // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
    validator = FormValidation.formValidation(form, {
      fields: {
        // settings_name: {
        //   validators: {
        //     notEmpty: {
        //       message: "Project name is required",
        //     },
        //   },
        // },
        kasko_bedeli: {
          validators: {
            notEmpty: {
              message: "Yukardaki tüm bilgileri doldurduğunuzdan emin olun",
            },
          },
        },
        // settings_description: {
        //   validators: {
        //     notEmpty: {
        //       message: "Description is required",
        //     },
        //   },
        // },
        // settings_release_date: {
        //   validators: {
        //     notEmpty: {
        //       message: "Release date is required",
        //     },
        //   },
        // },
        // "settings_notifications[]": {
        //   validators: {
        //     notEmpty: {
        //       message: "Notifications are required",
        //     },
        //   },
        // },
      },

      plugins: {
        trigger: new FormValidation.plugins.Trigger(),
        bootstrap: new FormValidation.plugins.Bootstrap5({
          rowSelector: ".fv-row",
          eleInvalidClass: "",
          eleValidClass: "",
        }),
      },
    });
  };

  var handleForm = function () {
    nextButton.addEventListener("click", function (e) {
      // Prevent default button action
      e.preventDefault();

      // Disable button to avoid multiple click
      nextButton.disabled = true;

      // Validate form before submit
      if (validator) {
        validator.validate().then(function (status) {
          console.log("validated!");

          if (status == "Valid") {
            // Show loading indication
            nextButton.setAttribute("data-kt-indicator", "on");

            // Simulate form submission
            setTimeout(function () {
              // Simulate form submission
              nextButton.removeAttribute("data-kt-indicator");

              // Enable button
              nextButton.disabled = false;

              // Go to next step
              stepper.goNext();
            }, 1500);
          } else {
            // Enable button
            nextButton.disabled = false;

            // Show popup warning. For more info check the plugin's official documentation: https://sweetalert2.github.io/
            Swal.fire({
              text: "Üzgünüm bazı eksik bilgiler var. Lütfen doldurup tekrar deneyin.",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Tamam",
              customClass: {
                confirmButton: "btn btn-primary",
              },
            });
          }
        });
      }
    });

    previousButton.addEventListener("click", function () {
      // Go to previous step
      stepper.goPrevious();
    });
  };

  return {
    // Public functions
    init: function () {
      form = KTModalCreateProject.getForm();
      stepper = KTModalCreateProject.getStepperObj();
      nextButton = KTModalCreateProject.getStepper().querySelector(
        '[data-kt-element="settings-next"]'
      );
      previousButton = KTModalCreateProject.getStepper().querySelector(
        '[data-kt-element="settings-previous"]'
      );

      initForm();
      initValidation();
      handleForm();
    },
  };
})();

// Webpack support
if (typeof module !== "undefined" && typeof module.exports !== "undefined") {
  window.KTModalCreateProjectSettings = module.exports =
    KTModalCreateProjectSettings;
}

/////////////////////////////////
// Araç kasko bilgileri için jquery kodlar
$(document).ready(function () {
  // Sayfa yüklendiğinde ilk verileri yükle
  updateData();

  // Dropdownlardan herhangi biri değiştiğinde verileri güncelle
  $(".arac_sec").change(function () {
    updateData();
  });

  $("#model_yili").change(function () {
    // Marka Seçeneklerini Yükle
    $("#marka_adi").empty();
    $("#tip_adi").empty();
    $("#kasko_bedeli").val("");
    $("#kaskokodu").val("");

    var model_yili = $("#model_yili").val();
    $.ajax({
      url: "/markalar",
      method: "GET",
      data: {
        model_yili: model_yili,
      },
      success: function (response) {
        var select = $("#marka_adi");
        select.append('<option value="----">----</option>');
        $.each(response, function (index, value) {
          select.append('<option value="' + value + '">' + value + "</option>");
        });
      },
    });
  });

  $("#marka_adi").change(function () {
    // Marka Seçeneklerini Yükle
    $("#tip_adi").empty();
    $("#kasko_bedeli").val("");
    $("#kaskokodu").val("");

    var model_yili = $("#model_yili").val();
    var marka_adi = $("#marka_adi").val();
    $.ajax({
      url: "/modeller",
      method: "GET",
      data: {
        model_yili: model_yili,
        marka_adi: marka_adi,
      },
      success: function (response) {
        var select = $("#tip_adi");
        select.append('<option value="----">----</option>');
        $.each(response, function (index, value) {
          select.append('<option value="' + value + '">' + value + "</option>");
        });
      },
    });
  });
});

// Model Yılı Seçeneklerini Yükle
$.get("/model_yili_secenekleri", function (response) {
  var select = $("#model_yili");
  $.each(response, function (index, value) {
    select.append('<option value="' + value + '">' + value + "</option>");
    console.log("calisti");
  });
});

function updateData() {
  $("#kaskobilgi").empty();
  var model_yili = $("#model_yili").val();
  var marka_adi = $("#marka_adi").val();
  var tip_adi = $("#tip_adi").val();

  $.ajax({
    url: "/fiyat",
    method: "GET",
    data: {
      model_yili: model_yili,
      marka_adi: marka_adi,
      tip_adi: tip_adi,
    },
    success: function (response) {
      $("#kasko_bedeli").val(response.kaskobedeli);
      $("#kaskokodu").val(response.kaskokodu);
      let bilgiler =
        "Kasko bedeli 2.000.000 TL üzerindeki araçlara kredi verilmemektedir.";
      if (response.kaskobedeli <= 400000) {
        bilgiler =
          "Seçili aracın kasko bedeli 0-400.000 TL aralığında olduğu için kasko tutarınin %70’ine kadar (" +
          parseFloat(response.kaskobedeli * 0.7).toLocaleString("tr-TR", {
            style: "currency",
            currency: "TRY",
          }) +
          ") ve maksimum 48 ay vade ile kredi çekilebilir.";
      }
      if (response.kaskobedeli > 400000 && response.kaskobedeli <= 800000) {
        bilgiler =
          "Seçili aracın kasko bedeli 400.000,01-800.000 TL aralığında olduğu için kasko tutarınin %50’sine kadar (" +
          parseFloat(response.kaskobedeli * 0.5).toLocaleString("tr-TR", {
            style: "currency",
            currency: "TRY",
          }) +
          ") ve maksimum 36 ay vade ile kredi çekilebilir.";
      }
      if (response.kaskobedeli > 800000 && response.kaskobedeli <= 1200000) {
        bilgiler =
          "Seçili aracın kasko bedeli 800.000,01-1.200.000 TL aralığında olduğu için kasko tutarınin %30’una kadar (" +
          parseFloat(response.kaskobedeli * 0.3).toLocaleString("tr-TR", {
            style: "currency",
            currency: "TRY",
          }) +
          ") ve maksimum 24 ay vade ile kredi çekilebilir.";
      }
      if (response.kaskobedeli > 1200000 && response.kaskobedeli <= 2000000) {
        bilgiler =
          "Seçili aracın kasko bedeli 1.200.000,01-2.000.000 TL aralığında olduğu için kasko tutarınin %20’sine kadar (" +
          parseFloat(response.kaskobedeli * 0.2).toLocaleString("tr-TR", {
            style: "currency",
            currency: "TRY",
          }) +
          ") ve maksimum 12 ay vade ile kredi çekilebilir.";
      }

      $("#kaskobilgi").text(bilgiler);
    },
  });
}

/////////////////////
// Kasko Kodu seçiminde ikifarklı sutundan hangisi aktif olacak

// Seçenekleri belirleyin
const secenek1 = document.querySelector(
  'input[name="aracSecimTipi"][value="1"]'
);
const secenek2 = document.querySelector(
  'input[name="aracSecimTipi"][value="2"]'
);

// Event listenerlarını ekle
secenek1.addEventListener("change", aracSecimiYapildi);
secenek2.addEventListener("change", aracSecimiYapildi);

function aracSecimiYapildi(e) {
  // Seçeneği belirleyin
  const secilenSecenek = e.target.value;

  // Div'leri gizle veya göster
  if (secilenSecenek === "1") {
    // Marka ve model div'i görüntülenecek
    const markaModelDiv = document.querySelector(".markaModelDiv");
    markaModelDiv.style.display = "block";

    // Model yılı ve kasko kodu div'i gizlenecek
    const modelKaskoDiv = document.querySelector(".modelKaskoDiv");
    modelKaskoDiv.style.display = "none";
  } else if (secilenSecenek === "2") {
    // Model yılı ve kasko kodu div'i görüntülenecek
    const modelKaskoDiv = document.querySelector(".modelKaskoDiv");
    modelKaskoDiv.style.display = "block";

    // Marka ve model div'i gizlenecek
    const markaModelDiv = document.querySelector(".markaModelDiv");
    markaModelDiv.style.display = "none";
  }
}
