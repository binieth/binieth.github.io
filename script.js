// Keep the footer year current automatically — no manual edits each year.
document.addEventListener("DOMContentLoaded", function () {
  var el = document.getElementById("year");
  if (el) { el.textContent = new Date().getFullYear(); }

  // Sidebar category filter (homepage only).
  var sel = document.getElementById("categoryFilter");
  if (sel) {
    sel.addEventListener("change", function () {
      var pick = sel.value;
      var rows = document.querySelectorAll(".post-row");
      rows.forEach(function (row) {
        var cat = row.getAttribute("data-category") || "all";
        row.style.display = (pick === "all" || cat === pick) ? "" : "none";
      });
    });
  }
});
