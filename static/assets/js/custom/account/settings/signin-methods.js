"use strict";
var KTAccountSettingsSigninMethods = (function () {
  var t,
    e,
    n,
    o,
    i,
    s,
    r,
    a,
    l,
    d = function () {
      e.classList.toggle("d-none"),
        s.classList.toggle("d-none"),
        n.classList.toggle("d-none");
    },
    c = function () {
      o.classList.toggle("d-none"),
        a.classList.toggle("d-none"),
        i.classList.toggle("d-none");
    };
  return {
    init: function () {
      var m;
      (t = document.getElementById("kt_signin_change_email")),
        (e = document.getElementById("kt_signin_email")),
        (n = document.getElementById("kt_signin_email_edit")),
        (o = document.getElementById("kt_signin_password")),
        (i = document.getElementById("kt_signin_password_edit")),
        (s = document.getElementById("kt_signin_email_button")),
        (r = document.getElementById("kt_signin_cancel")),
        (a = document.getElementById("kt_signin_password_button")),
        (l = document.getElementById("kt_password_cancel")),
        e &&
          (s.querySelector("button").addEventListener("click", function () {
            d();
          }),
          r.addEventListener("click", function () {
            d();
          }),
          a.querySelector("button").addEventListener("click", function () {
            c();
          }),
          l.addEventListener("click", function () {
            c();
          })),
        t &&
          ((m = FormValidation.formValidation(t, {
            fields: {
              emailaddress: {
                validators: {
                  notEmpty: { message: "Email is required" },
                  emailAddress: {
                    message: "The value is not a valid email address",
                  },
                },
              },
              confirmemailpassword: {
                validators: { notEmpty: { message: "Password is required" } },
              },
            },
            plugins: {
              trigger: new FormValidation.plugins.Trigger(),
              bootstrap: new FormValidation.plugins.Bootstrap5({
                rowSelector: ".fv-row",
              }),
            },
          })),
          t
            .querySelector("#kt_signin_submit")
            .addEventListener("click", function (e) {
              e.preventDefault(),
                console.log("click"),
                m.validate().then(function (e) {
                  "Valid" == e
                    ? swal
                        .fire({
                          text: "Sent password reset. Please check your email",
                          icon: "success",
                          buttonsStyling: !1,
                          confirmButtonText: "Ok, got it!",
                          customClass: {
                            confirmButton:
                              "btn font-weight-bold btn-light-primary",
                          },
                        })
                        .then(function () {
                          t.reset(), m.resetForm(), d();
                        })
                    : swal.fire({
                        text: "Sorry, looks like there are some errors detected, please try again.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                          confirmButton:
                            "btn font-weight-bold btn-light-primary",
                        },
                      });
                });
            })),
        (function (t) {
          var e,
            n = document.getElementById("kt_signin_change_password");
          n &&
            ((e = FormValidation.formValidation(n, {
              fields: {
                currentpassword: {
                  validators: {
                    notEmpty: { message: "Şimdiki Parolanız gereklidir" },
                  },
                },
                newpassword: {
                  validators: {
                    notEmpty: { message: "Yeni Parola gereklidir" },
                  },
                },
                confirmpassword: {
                  validators: {
                    notEmpty: { message: "Parola Onayı gereklidir" },
                    identical: {
                      compare: function () {
                        return n.querySelector('[name="newpassword"]').value;
                      },
                      message: "Yeni Parola ve Yeni Parola Onayı eşleşmedi",
                    },
                  },
                },
              },
              plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap5({
                  rowSelector: ".fv-row",
                }),
              },
            })),
            n
              .querySelector("#kt_password_submit")
              .addEventListener("click", function (t) {
                t.preventDefault(),
                  console.log("click"),
                  e.validate().then(function (t) {
                    if ("Valid" == t) {
                      // Form verilerini alın
                      var username = $("#username").val();
                      var old_password = $("#currentpassword").val();
                      var new_password = $("#newpassword").val();

                      // AJAX isteği gönderin
                      $.ajax({
                        url: "/api/change-password",
                        method: "POST",
                        data: {
                          username: username,
                          old_password: old_password,
                          new_password: new_password,
                        },
                        success: function (response) {
                          // Başarılı bir şekilde yanıt alındığında ne yapılacağını belirleyin
                          if (response.success) {
                            swal
                              .fire({
                                text: "Parola başarıyla değiştirildi.",
                                icon: "success",
                                buttonsStyling: !1,
                                confirmButtonText: "Tamam",
                                customClass: {
                                  confirmButton:
                                    "btn font-weight-bold btn-light-primary",
                                },
                              })
                              .then(function () {
                                n.reset(), e.resetForm(), c();
                              });
                          } else {
                            swal.fire({
                              text: "Kayıt edilirken bir problem oldu. Hata Kodu: 11298",
                              icon: "error",
                              buttonsStyling: !1,
                              confirmButtonText: "Tamam",
                              customClass: {
                                confirmButton:
                                  "btn font-weight-bold btn-light-primary",
                              },
                            });
                          }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                          // Hata durumunda ne yapılacağını belirleyin
                          swal.fire({
                            text:
                              "Bir hata oluştu: " +
                              textStatus +
                              " - " +
                              errorThrown,
                            icon: "error",
                            buttonsStyling: !1,
                            confirmButtonText: "Tamam",
                            customClass: {
                              confirmButton:
                                "btn font-weight-bold btn-light-primary",
                            },
                          });
                        },
                      });
                    } else {
                      swal.fire({
                        text: "Lütfen form verilerini kontrol edip tekrar deneyin.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Tamam",
                        customClass: {
                          confirmButton:
                            "btn font-weight-bold btn-light-primary",
                        },
                      });
                    }
                  });
              }));
        })();
    },
  };
})();
KTUtil.onDOMContentLoaded(function () {
  KTAccountSettingsSigninMethods.init();
});
