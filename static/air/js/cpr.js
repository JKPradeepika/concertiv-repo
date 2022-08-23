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

const iFrame_details = {
  clientId: "3a21d9c1-bd7a-4ff1-9ccf-0700e40a57f8",
  templateKey: "air",
  webhookKey: "air_webhook",
  userJwt: "",
  config: {
    blockImportIfErrors: true,
  },
};

let importer;

function launchOneSchema(token) {
  iFrame_details.userJwt = token;
  importer = oneschemaImporter(iFrame_details);
  importer.launch()

  importer.on("success", (data) => {
  })

  importer.on("cancel", () => {
    // TODO: handle cancel
  })

  importer.on("error", (message) => {
    // TODO: handle errors
  })
}

