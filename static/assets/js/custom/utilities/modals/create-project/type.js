"use strict";

// Class definition
var KTModalCreateProjectType = (function () {
  // Variables
  var nextButton;
  var validator;
  var form;
  var stepper;

  // Init form inputs
  var initForm = function () {
    // Init inputmask plugin --- For more info please refer to the official documentation here: https://github.com/RobinHerbots/Inputmask
    Inputmask({
      mask: "999 999 99 99",
    }).mask("#galeri_telefonu");
  };

  // Private functions
  var initValidation = function () {
    // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
    validator = FormValidation.formValidation(form, {
      fields: {
        galeri_telefonu: {
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
        project_type: {
          validators: {
            notEmpty: {
              message: "Project type is required",
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
          e.preventDefault();

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
              confirmButtonText: "Tamam",
              customClass: {
                confirmButton: "btn btn-primary",
              },
            });
          }
        });
      }
    });
  };

  return {
    // Public functions
    init: function () {
      form = KTModalCreateProject.getForm();
      stepper = KTModalCreateProject.getStepperObj();
      nextButton = KTModalCreateProject.getStepper().querySelector(
        '[data-kt-element="type-next"]'
      );

      initForm();
      initValidation();
      handleForm();
    },
  };
})();

// Webpack support
if (typeof module !== "undefined" && typeof module.exports !== "undefined") {
  window.KTModalCreateProjectType = module.exports = KTModalCreateProjectType;
}

// Kasko kodu degistiginde ajax sorgu yap ve ozet bilgi degistir
$(document).ready(function () {
  $("#galeri_telefonu").on("input", function () {
    var galeri_telefonu = $(this).val().replace(/[\s_]/g, "");

    $("#galeri_adi").val("");
    $("#galeri_ili").val("");
    $("#galeri_adi").prop("disabled", false);
    $("#galeri_ili").prop("disabled", false);

    if (galeri_telefonu.length < 10) {
      return;
    }

    $.ajax({
      url: "/galeri_sorgu", // buradaki URL'yi API URL'inizle değiştirin
      type: "GET",
      data: {
        galeri_telefonu: galeri_telefonu,
      },
      success: function (response) {
        $("#galeri_adi").val(response.galeri_adi);
        $("#galeri_ili").val(response.galeri_il);
        $("#galeri_adi").prop("disabled", true);
        $("#galeri_ili").prop("disabled", true);
      },
      error: function (xhr) {
        // hata durumunda burası çalışır
        // console.log(xhr.responseText);
      },
    });
  });
});
