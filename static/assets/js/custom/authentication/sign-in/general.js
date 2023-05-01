"use strict";

// Class definition
var KTSigninGeneral = (function () {
  // Elements
  var form;
  var submitButton;
  var validator;

  // Init form inputs
  var initForm = function () {
    // Init inputmask plugin --- For more info please refer to the official documentation here: https://github.com/RobinHerbots/Inputmask
    Inputmask({
      mask: "999 999 99 99",
    }).mask("#cep_tel");
  };

  // Handle form
  var handleValidation = function (e) {
    // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
    validator = FormValidation.formValidation(form, {
      fields: {
        cep_tel: {
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
        password: {
          validators: {
            notEmpty: {
              message: "Şifre gereklidir",
            },
          },
        },
      },
      plugins: {
        trigger: new FormValidation.plugins.Trigger(),
        bootstrap: new FormValidation.plugins.Bootstrap5({
          rowSelector: ".fv-row",
          eleInvalidClass: "", // comment to enable invalid state icons
          eleValidClass: "", // comment to enable valid state icons
        }),
      },
    });
  };

  var handleSubmitDemo = function (e) {
    // Handle form submit
    submitButton.addEventListener("click", function (e) {
      // Prevent button default action
      e.preventDefault();

      // Validate form
      validator.validate().then(function (status) {
        if (status == "Valid") {
          // Show loading indication
          submitButton.setAttribute("data-kt-indicator", "on");

          // Disable button to avoid multiple click
          submitButton.disabled = true;

          // Simulate ajax request
          setTimeout(function () {
            // Hide loading indication
            submitButton.removeAttribute("data-kt-indicator");

            // Enable button
            submitButton.disabled = false;

            // Show message popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
            Swal.fire({
              text: "You have successfully logged in!",
              icon: "success",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                confirmButton: "btn btn-primary",
              },
            }).then(function (result) {
              if (result.isConfirmed) {
                form.querySelector('[name="cep_tel"]').value = "";
                form.querySelector('[name="password"]').value = "";

                //form.submit(); // submit form
                var redirectUrl = form.getAttribute("data-kt-redirect-url");
                if (redirectUrl) {
                  location.href = redirectUrl;
                }
              }
            });
          }, 2000);
        } else {
          // Show error popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
          Swal.fire({
            text: "3 Giriş yaparken bir sorun oluştu. Lütfen cep telefonu numarası ve şifreyi kontrol ederek tekrar deneyin.",
            icon: "error",
            buttonsStyling: false,
            confirmButtonText: "Tamam",
            customClass: {
              confirmButton: "btn btn-primary",
            },
          });
        }
      });
    });
  };

  var handleSubmitAjax = function (e) {
    // Handle form submit
    submitButton.addEventListener("click", function (e) {
      // Prevent button default action
      e.preventDefault();

      // Show loading indication
      submitButton.setAttribute("data-kt-indicator", "on");

      setTimeout(() => {
        submitButton.removeAttribute("data-kt-indicator");
      }, 1500);

      // Validate form
      validator.validate().then(function (status) {
        if (status == "Valid") {
          // Enable button
          submitButton.disabled = false;

          // Check axios library docs: https://axios-http.com/docs/intro
          axios
            .post("/login", {
              username: form
                .querySelector('[name="cep_tel"]')
                .value.replace(/\s/g, ""),
              password: form.querySelector('[name="password"]').value,
            })
            .then(function (response) {
              if (response) {
                form.querySelector('[name="cep_tel"]').value = "";
                form.querySelector('[name="password"]').value = "";

                const redirectUrl = form.getAttribute("data-kt-redirect-url");

                if (redirectUrl) {
                  location.href = redirectUrl;
                }
              } else {
                // Show error popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
                Swal.fire({
                  text: "B.",
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                    confirmButton: "btn btn-primary",
                  },
                });
              }
            })
            .catch(function (error) {
              Swal.fire({
                text: "Giriş yaparken bir sorun oluştu. Lütfen cep telefonu numarası ve şifreyi kontrol ederek tekrar deneyin.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Tamam",
                customClass: {
                  confirmButton: "btn btn-primary",
                },
              });
            });
        } else {
          // Show error popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
          Swal.fire({
            text: "Cep telefonu hatalı görünüyor. Lütfen cep telefonu numarası ve şifreyi kontrol ederek tekrar deneyin.",
            icon: "error",
            buttonsStyling: false,
            confirmButtonText: "Tamam",
            customClass: {
              confirmButton: "btn btn-primary",
            },
          });
        }
      });
    });
  };

  // Public functions
  return {
    // Initialization
    init: function () {
      form = document.querySelector("#kt_sign_in_form");
      submitButton = document.querySelector("#kt_sign_in_submit");

      initForm();
      handleValidation();
      // handleSubmitDemo(); // used for demo purposes only, if you use the below ajax version you can uncomment this one
      handleSubmitAjax(); // use for ajax submit
    },
  };
})();

// On document ready
KTUtil.onDOMContentLoaded(function () {
  KTSigninGeneral.init();
});
