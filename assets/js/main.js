// The Torch Leader — tiny front-end helpers. No dependencies.

// Fill in today's date in the utility bar, e.g. "Friday, October 30, 2026".
(function () {
  var el = document.getElementById("today-date");
  if (!el) return;
  try {
    el.textContent = new Date().toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch (e) {
    el.textContent = "";
  }
})();
