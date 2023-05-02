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
      showDropdowns: true,
      minYear: 1901,
      maxYear: 2010,
      locale: {
        format: "DD.MM.YYYY",
      },
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
  // Load City Options
  $.get("/il_secimi", function (response) {
    const cityNames = JSON.parse(response);
    var select = $("#il_secimi_is");

    cityNames.forEach((city) => {
      select.append('<option value="' + city + '">' + city + "</option>");
    });
  });

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
