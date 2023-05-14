"use strict";

// Özet
// Class definition
var KTModalCreateProjectFiles = (function () {
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
    // var dueDate = $(form.querySelector('[name="dogum_tarihi"]'));
    // dueDate.flatpickr({
    //   enableTime: false,
    //   dateFormat: "d.m.Y",
    // });
  };

  var initValidation = function () {
    // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
    validator = FormValidation.formValidation(form, {
      fields: {
        // kimlik_seri: {
        //   validators: {
        //     notEmpty: {
        //       message: "Kimlik Seri No Gereklidir",
        //     },
        //   },
        // },
        // dogum_tarihi: {
        //   validators: {
        //     notEmpty: {
        //       message: "Doğum tarihi gereklidir",
        //     },
        //   },
        // },
        // target_tags: {
        //   validators: {
        //     notEmpty: {
        //       message: "Target tags are required",
        //     },
        //   },
        // },
        kvkk_onay: {
          validators: {
            notEmpty: {
              message: "Kvkk onayı gereklidir",
            },
          },
        },
        // "target_notifications[]": {
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
      const dugme_label =
        nextButton.querySelector(".indicator-label").textContent;

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
              const data = {
                dosya_id: $("#dosya_id").val(),
                dosya_numarasi: "",
                created_by: "",
                basvuruTuru: $('input[name="basvuruTuru"]').val(),
                galeri_telefonu: $('input[name="galeri_telefonu"]')
                  .val()
                  .replace(/\s/g, ""),
                galeri_adi: $('input[name="galeri_adi"]').val(),
                galeri_ili: $('select[name="galeri_ili"]').val(),
                model_yili: $('select[name="model_yili"]').val(),
                marka_adi: "",
                tip_adi: "",
                kaskokodu: $('input[name="kaskokodu"]').val(),
                kasko_bedeli: $('input[name="kasko_bedeli"]').val(),
                sasi_no: $('input[name="sasi_no"]').val(),
                motor_no: $('input[name="motor_no"]').val(),
                tescil_belge_no: $('input[name="tescil_belge_no"]').val(),
                arac_plakasi: $('input[name="arac_plakasi"]').val(),
                arac_satis_tutari: $('input[name="arac_satis_tutari"]').val(),
                kredi_tutari: $('input[name="kredi_tutari"]').val(),
                kredi_vadesi: $('input[name="kredi_vadesi"]').val(),
                musteri_cep_telefonu: $('input[name="musteri_cep_telefonu"]')
                  .val()
                  .replace(/\s/g, ""),
                tc: $('input[name="tc"]').val(),
                adi: $('input[name="adi"]').val(),
                soyadi: $('input[name="soyadi"]').val(),
                kimlik_seri: $('input[name="kimlik_seri"]').val(),
                dogum_tarihi: $('input[name="dogum_tarihi"]').val(),
                egitim_durumu: $('select[name="egitim_durumu"]').val(),
                meslek_gurubu: $('select[name="meslek_gurubu"]').val(),
                meslek: $('select[name="meslek"]').val(),
                aylik_gelir: $('input[name="aylik_gelir"]').val(),
                sosyal_guvenlik: $('select[name="sosyal_guvenlik"]').val(),
                sektor: $('select[name="sektor"]').val(),
                calisma_suresi_yil: $('input[name="calisma_suresi_yil"]').val(),
                acik_adres_ev: $('input[name="calisma_suresi_ay"]').val(),
                vergi_dairesi_il: $('select[name="vergi_dairesi_il"]').val(),
                vergi_dairesi_ilce: $(
                  'select[name="vergi_dairesi_ilce"]'
                ).val(),
                vergi_no: $('input[name="vergi_no"]').val(),
                ikamet_tipi: $('select[name="ikamet_tipi"]').val(),
                il_secimi_ev: $('select[name="il_secimi_ev"]').val(),
                ilce_secimi_ev: $('select[name="ilce_secimi_ev"]').val(),
                mahalle_ev: $('input[name="mahalle_ev"]').val(),
                ikamet_sure_ev: $('input[name="ikamet_sure_ev"]').val(),
                acik_adres_ev: $('textarea[name="acik_adres_ev"]').val(),
                isyeri_adi: $('input[name="isyeri_adi"]').val(),
                isyeri_telefonu: $('input[name="isyeri_telefonu"]').val(),
                il_secimi_is: $('select[name="il_secimi_is"]').val(),
                ilce_secimi_is: $('select[name="ilce_secimi_is"]').val(),
                mahalle_is: $('input[name="mahalle_is"]').val(),
                acik_adres_is: $('textarea[name="acik_adres_is"]').val(),
              };

              // Check axios library docs: https://axios-http.com/docs/intro
              axios
                .post("/form", data)
                .then(function (response) {
                  if (response) {
                    // Simulate form submission
                    nextButton.removeAttribute("data-kt-indicator");

                    // Enable button
                    nextButton.disabled = false;

                    if (dugme_label === "Kaydet") {
                      // edıt dosya bolumunde Dugmenın uzerinde Kaydet yazarç Kaydet e basıldıgında stepper aktıf olmasın bir swal pencede mesaj verılsın. stepper aktıf olunca yenı basıvuru formu hata verdı
                      //   const modal = new bootstrap.Modal(
                      //     document.getElementById("kt_modal_kaydedildi")
                      //   );
                      //   modal.show();
                      // Show popup confirmation
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

                      toastr.success(
                        "Dosyada yapılan değişiklikler kayıt edildi.",
                        "Kayıt edildi"
                      );
                    } else {
                      // Go to next step
                      // stepper.goNext();
                      stepper.goTo(7);

                      // edit ederken gizlenmis alanlari gozter
                      const elements = document.querySelectorAll(
                        ".edit_bolumu_icin_gizle"
                      );
                      elements.forEach((element) => {
                        element.style.setProperty("display", "", "important");
                      });

                      // modal yukari kaydir
                      $("#kt_modal_create_project .modal-body").animate(
                        {
                          scrollTop: 0,
                        },
                        500
                      );
                    }

                    ////
                  } else {
                    // Show error popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
                    Swal.fire({
                      text: "Bir sorun oluştu.",
                      icon: "error",
                      buttonsStyling: false,
                      confirmButtonText: "Tamam",
                      customClass: {
                        confirmButton: "btn btn-primary",
                      },
                    });
                  }
                })
                .catch(function (error) {
                  Swal.fire({
                    text: "Kayıt esnasında bir problem oluştu.",
                    icon: "error",
                    buttonsStyling: false,
                    confirmButtonText: "Tamam",
                    customClass: {
                      confirmButton: "btn btn-primary",
                    },
                  });
                });
            }, 1500);
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
        '[data-kt-element="files-next"]'
      );
      previousButton = KTModalCreateProject.getStepper().querySelector(
        '[data-kt-element="files-previous"]'
      );

      initForm();
      initValidation();
      handleForm();
    },
  };
})();

// Webpack support
if (typeof module !== "undefined" && typeof module.exports !== "undefined") {
  window.KTModalCreateProjectFiles = module.exports = KTModalCreateProjectFiles;
}
