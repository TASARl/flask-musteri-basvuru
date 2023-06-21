jQuery(window).on("load", function () {
  "use strict";

  /*  ===================================
        Loading Timeout
     ====================================== */
  $(".loader-area").fadeOut(1000);
});

$("a").each(function () {
  var href = $(this).attr("href");
  if (!href.startsWith("#")) {
    $(this).on("click", function () {
      $(".loader-area").css("display", "block").delay(4000).fadeOut();
    });
  }
});
