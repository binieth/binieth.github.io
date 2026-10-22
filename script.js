// Keep the footer year current automatically — no manual edits each year.
document.addEventListener("DOMContentLoaded", function () {
  var el = document.getElementById("year");
  if (el) { el.textContent = new Date().getFullYear(); }
});
