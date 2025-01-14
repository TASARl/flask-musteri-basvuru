document.addEventListener("DOMContentLoaded", function () {
  $.ajax({
    url: "/api/gecici_guncellemeler/kullanici",
    type: "GET",
    success: function (response) {
      // Timeline divini seçme
      const timeline = $("#timeline_kullanici");

      // Her bir kayıt için timeline öğesi oluşturma
      $.each(response, function (index, item) {
        // Yeni bir timeline item öğesi oluşturma
        const timelineItem = $("<div>").addClass("timeline-item");

        // Timeline line öğesi oluşturma
        const timelineLine = $("<div>").addClass("timeline-line w-40px");
        timelineItem.append(timelineLine);

        // Timeline icon öğesi oluşturma
        const timelineIcon = $("<div>").addClass(
          "timeline-icon symbol symbol-circle symbol-40px"
        );
        timelineItem.append(timelineIcon);

        let basketType;
        if (item.status === "standart") {
          basketType = "ki-setting-4 text-success";
        } else if (item.status === "kullanici") {
          basketType = "ki-pencil text-warning";
        } else {
          basketType = "ki-abstract-10 text-primary";
        }

        // Icon içindeki simgeyi oluşturma
        const iconSymbol = $("<div>").addClass("symbol-label bg-light");
        const icon = $("<i>").addClass(`ki-duotone ${basketType} fs-2`);
        const paths = ["path1", "path2", "path3", "path4"];
        $.each(paths, function (index, path) {
          const span = $("<span>").addClass(path);
          icon.append(span);
        });
        iconSymbol.append(icon);
        timelineIcon.append(iconSymbol);

        // Timeline content öğesi oluşturma
        const timelineContent = $("<div>").addClass("timeline-content mt-n1");
        const timelineHeading = $("<div>").addClass("pe-3 mb-5");
        const title = $("<div>")
          .addClass("fs-5 fw-semibold mb-2")
          .html(
            `${item.galeri_adi} <br/> ${item.dosya_tarihi} tarihli ${item.gorunen_dosya_no} numaralı dosyada işlem yapıldı --- ${item.inputValue}`
          );
        timelineHeading.append(title);
        const currentDate = new Date(item.created_time.$date);
        const formattedDate = currentDate.toLocaleDateString();
        const formattedTime = currentDate.toLocaleTimeString();
        const info = $("<div>")
          .addClass("text-muted me-2 fs-7")
          .text(`${formattedDate} ${formattedTime} - ${item.isim_soyisim}`);
        timelineHeading.append(info);
        timelineContent.append(timelineHeading);
        timelineItem.append(timelineContent);

        // Timeline öğesini sayfaya ekleme
        timeline.append(timelineItem);
      });
    },
    error: function (error) {
      console.log(error);
    },
  });
});
