$(document).ready(function () {
  $("#example").DataTable({
    language: {
      lengthMenu: "_MENU_",
      zeroRecords: "Hiçbir şey bulunamadı",
      info: "",
      infoEmpty: "Kayıt yok",
      infoFiltered: "(filtered from _MAX_ total records)",
      search: "Ara",
      Previous: "",
      next: "",
    },
    ordering: false,
  });
});
