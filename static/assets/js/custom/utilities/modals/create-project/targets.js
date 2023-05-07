"use strict";

// Müşteri Bilgileri
// Class definition
var KTModalCreateProjectTargets = (function () {
  // Variables
  var nextButton;
  var previousButton;
  var validator;
  var form;
  var stepper;

  // Private functions
  var initForm = function () {
    // // Tags. For more info, please visit the official plugin site: https://yaireo.github.io/tagify/
    // var tags = new Tagify(form.querySelector('[name="target_tags"]'), {
    //   whitelist: ["Important", "Urgent", "Highh", "Medium", "Low"],
    //   maxTags: 5,
    //   dropdown: {
    //     maxItems: 10, // <- mixumum allowed rendered suggestions
    //     enabled: 0, // <- show suggestions on focus
    //     closeOnSelect: false, // <- do not hide the suggestions dropdown once an item has been selected
    //   },
    // });
    // tags.on("change", function () {
    //   // Revalidate the field when an option is chosen
    //   validator.revalidateField("tags");
    // });

    // Due date. For more info, please visit the official plugin site: https://flatpickr.js.org/
    var dueDate = $(form.querySelector('[name="dogum_tarihi"]'));
    dueDate.daterangepicker({
      singleDatePicker: true,
      showDropdowns: false,
      autoApply: true,
      locale: {
        format: "DD.MM.YYYY",
      },
    });

    // Init inputmask plugin --- For more info please refer to the official documentation here: https://github.com/RobinHerbots/Inputmask
    Inputmask({
      mask: "999 999 99 99",
    }).mask("#musteri_cep_telefonu");

    Inputmask({
      regex: "^[1-9]{1}[0-9]{9}[0,2,4,6,8]{1}$",
    }).mask("#tc");

    // Expiry year. For more info, plase visit the official plugin site: https://select2.org/
    $(form.querySelector('[name="egitim_durumu"]')).on("change", function () {
      // Revalidate the field when an option is chosen
      validator.revalidateField("egitim_durumu");
    });

    // Expiry year. For more info, plase visit the official plugin site: https://select2.org/
    // $(form.querySelector('[name="target_assign"]')).on("change", function () {
    //   // Revalidate the field when an option is chosen
    //   validator.revalidateField("target_assign");
    // });
  };

  var initValidation = function () {
    // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
    validator = FormValidation.formValidation(form, {
      fields: {
        musteri_cep_telefonu: {
          validators: {
            regexp: {
              regexp: /^(5\d{2})\s?(\d{3})\s?(\d{2})\s?(\d{2})$/,
              message:
                "Cep telefonu 5 ile başlamalı ve 10 haneli olmalıdır (555 444 33 22)",
            },
            notEmpty: {
              message: "Cep telefonu gereklidir",
            },
          },
        },
        tc: {
          validators: {
            notEmpty: {
              message: "TC Kimlik No gereklidir",
            },
          },
        },
        kimlik_seri: {
          validators: {
            notEmpty: {
              message: "Kimlik Seri No Gereklidir",
            },
          },
        },
        dogum_tarihi: {
          validators: {
            notEmpty: {
              message: "Doğum tarihi gereklidir",
            },
          },
        },
        egitim_durumu: {
          validators: {
            notEmpty: {
              message: "Egitim Durumu gereklidir",
            },
          },
        },
        target_tags: {
          validators: {
            notEmpty: {
              message: "Target tags are required",
            },
          },
        },
        // target_allow: {
        //   validators: {
        //     notEmpty: {
        //       message: "Allowing target is required",
        //     },
        //   },
        // },
        "target_notifications[]": {
          validators: {
            notEmpty: {
              message: "Notifications are required",
            },
          },
        },
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

              // modal yukari kaydir
              $("#kt_modal_create_project .modal-body").animate(
                {
                  scrollTop: 0,
                },
                500
              );
              ////
            }, 500);
          } else {
            // Enable button
            nextButton.disabled = false;

            // Show popup warning. For more info check the plugin's official documentation: https://sweetalert2.github.io/
            Swal.fire({
              text: "Üzgünüm. Eksik kalan veriler var. Lütfen tamamlayın.",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Tamam!",
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
        '[data-kt-element="targets-next"]'
      );
      previousButton = KTModalCreateProject.getStepper().querySelector(
        '[data-kt-element="targets-previous"]'
      );

      initForm();
      initValidation();
      handleForm();
    },
  };
})();

// Webpack support
if (typeof module !== "undefined" && typeof module.exports !== "undefined") {
  window.KTModalCreateProjectTargets = module.exports =
    KTModalCreateProjectTargets;
}

$(document).ready(function () {
  // Load City Options
  $.get("/il_secimi", function (response) {
    const cityNames = JSON.parse(response);
    var select = $("#il_secimi_ev");

    cityNames.forEach((city) => {
      select.append('<option value="' + city + '">' + city + "</option>");
    });

    var select = $("#il_secimi_is");

    cityNames.forEach((city) => {
      select.append('<option value="' + city + '">' + city + "</option>");
    });

    var select = $("#vergi_dairesi_il");

    cityNames.forEach((city) => {
      select.append('<option value="' + city + '">' + city + "</option>");
    });

    var select = $("#galeri_ili");

    cityNames.forEach((city) => {
      select.append('<option value="' + city + '">' + city + "</option>");
    });
  });

  // Load District Options
  $("#il_secimi_ev").change(function () {
    $("#ilce_secimi_ev").empty();

    var il_secimi = $("#il_secimi_ev").val();
    console.log(il_secimi);
    $.ajax({
      url: "/ilce_secimi",
      method: "GET",
      data: {
        il_secimi: il_secimi,
      },
      success: function (response) {
        const ilceName = JSON.parse(response);
        var select = $("#ilce_secimi_ev");

        ilceName.forEach((ilce_isim) => {
          select.append(
            '<option value="' + ilce_isim + '">' + ilce_isim + "</option>"
          );
        });
      },
    });
  });
});

$(document).ready(function () {
  // Load District Options
  $("#il_secimi_is").change(function () {
    $("#ilce_secimi_is").empty();

    var il_secimi = $("#il_secimi_is").val();
    console.log(il_secimi);
    $.ajax({
      url: "/ilce_secimi",
      method: "GET",
      data: {
        il_secimi: il_secimi,
      },
      success: function (response) {
        const ilceName = JSON.parse(response);
        var select = $("#ilce_secimi_is");

        ilceName.forEach((ilce_isim) => {
          select.append(
            '<option value="' + ilce_isim + '">' + ilce_isim + "</option>"
          );
        });
      },
    });
  });
});

// vergi dairesi ilce menusu yukle
$(document).ready(function () {
  // Load District Options
  $("#vergi_dairesi_il").change(function () {
    $("#vergi_dairesi_ilce").val(null).trigger("change");

    var il_secimi = $("#vergi_dairesi_il").val();

    $.ajax({
      url: "/vergi_ilce_secimi",
      method: "GET",
      data: {
        il_secimi: il_secimi,
      },
      success: function (response) {
        const ilceName = JSON.parse(response);
        var select = $("#vergi_dairesi_ilce");

        ilceName.forEach((ilce_isim) => {
          select.append(
            '<option value="' + ilce_isim + '">' + ilce_isim + "</option>"
          );
        });
      },
    });
  });
});

// meslek grubu degısınce alttaki degerleri sıfırla ve gosterilecekleri göster
$(document).ready(function () {
  // Load District Options
  $("#meslek_gurubu").change(function () {
    $("#sosyal_guvenlik").val(null).trigger("change");
    $("#sektor").val(null).trigger("change");
    $("#calisma_suresi_yil").val(null).trigger("change");
    $("#calisma_suresi_ay").val(null).trigger("change");
    $("#vergi_dairesi_il").val(null).trigger("change");
    $("#vergi_dairesi_ilce").val(null).trigger("change");
    $("#vergi_no").val(null).trigger("change");

    var selectedValue = $(this).val();

    var calisma_detay_div = $("#calisma_detay_bilgi");

    if (
      [
        "ÇİFTÇİ",
        "EMEKLİ ÇALIŞAN",
        "KAMU SEKTÖR ÜCRETLİ",
        "ÖZEL SEKTÖR ÜCRETLİ",
        "SERBEST MESLEK SAHİBİ",
      ].includes(selectedValue)
    ) {
      calisma_detay_div.show();
    } else {
      calisma_detay_div.hide();
    }

    var vergi_dairesi_div = $("#vergi_dairesi_bilgi");

    if (selectedValue == "SERBEST MESLEK SAHİBİ") {
      vergi_dairesi_div.show();
    } else {
      vergi_dairesi_div.hide();
    }

    var is_adresi_div = $("#is_adresi_bilgi");
    if (
      [
        "ÇİFTÇİ",
        "EMEKLİ ÇALIŞAN",
        "KAMU SEKTÖR ÜCRETLİ",
        "ÖZEL SEKTÖR ÜCRETLİ",
        "SERBEST MESLEK SAHİBİ",
      ].includes(selectedValue)
    ) {
      is_adresi_div.show();
    } else {
      is_adresi_div.hide();
    }
  });
});

// kredi tutarı ve araç satış tutarı 3 er hane ayırma
const input_arac_satis_tutari = document.querySelector("#aylik_gelir");

input_arac_satis_tutari.addEventListener("keyup", function (event) {
  const value = event.target.value.replace(/\D/g, "");
  const formatedValue = parseInt(value).toLocaleString();
  event.target.value = formatedValue;
});

// numerik degerleri sinirlandir
$(document).ready(function () {
  $("#ikamet_sure_ev").on("input", function () {
    this.value = this.value.replace(/[^0-9]/g, "");
  });
  $("#calisma_suresi_ay").on("input", function () {
    this.value = this.value.replace(/[^0-9]/g, "");
  });
  $("#calisma_suresi_yil").on("input", function () {
    this.value = this.value.replace(/[^0-9]/g, "");
  });
});
