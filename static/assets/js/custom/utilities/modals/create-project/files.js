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

    // Expiry year. For more info, plase visit the official plugin site: https://select2.org/
    $(form.querySelector('[name="egitim_durumu"]')).on("change", function () {
      // Revalidate the field when an option is chosen
      validator.revalidateField("egitim_durumu");
    });
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