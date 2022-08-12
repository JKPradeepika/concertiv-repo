function bootnavbar(options) {
  const defaultOption = {
    selector: "main_navbar",
    animation: true,
    animateIn: "animate__fadeIn",
  };

  const bnOptions = { ...defaultOption, ...options };

  init = function () {
    var dropdowns = document
      .getElementById(bnOptions.selector)
      .getElementsByClassName("dropdown");

    Array.prototype.forEach.call(dropdowns, (item) => {
      //add animation
      if (bnOptions.animation) {
        const element = item.querySelector(".dropdown-menu");
        element.classList.add("animate__animated");
        element.classList.add(bnOptions.animateIn);
      }

      //hover effects
      item.addEventListener("mouseover", function () {
        this.classList.add("show");
        const element = this.querySelector(".dropdown-menu");
        element.classList.add("show");
      });

      item.addEventListener("mouseout", function () {
        this.classList.remove("show");
        const element = this.querySelector(".dropdown-menu");
        element.classList.remove("show");
      });
    });
  };

  init();
}
const importer = oneschemaImporter({
  clientId: "3a21d9c1-bd7a-4ff1-9ccf-0700e40a57f8",
  templateKey: "air",
  webhookKey: "air_webhook",
  userJwt: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiPFVTRVJfSUQ-IiwiaXNzIjoiM2EyMWQ5YzEtYmQ3YS00ZmYxLTljY2YtMDcwMGU0MGE1N2Y4In0.RJyoCIsLaJ0DyMWWSxPJ-Se-Z2O0OQ-keMv-WQvEIdw",
  config: {
    blockImportIfErrors: true,
  },
})

function launchOneSchema() {
  importer.launch()

  importer.on("success", (data) => {
    // TODO: handle success
  })

  importer.on("cancel", () => {
    // TODO: handle cancel
  })

  importer.on("error", (message) => {
    // TODO: handle errors
  })
}

