$(document).ready(function() {
  $(document).on('click', '.dropdown-menu', function (e) {
    e.stopPropagation();
  });

  // make it as accordion for smaller screens
  if ($(window).width() < 992) {
    $('.dropdown-menu a').click(function(e){
      e.preventDefault();
        if($(this).next('.submenu').length){
          $(this).next('.submenu').toggle();
        }
        $('.dropdown').on('hide.bs.dropdown', function () {
       $(this).find('.submenu').hide();
    })
    });
}

});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const iFrame_details = {
  clientId: "3a21d9c1-bd7a-4ff1-9ccf-0700e40a57f8",
  templateKey: "",
  webhookKey: "",
  userJwt: "",
  config: {
    blockImportIfErrors: true,
  },
};

let importer;

function launchOneSchema(jwt_token, domain_name, travel_type) {
  iFrame_details.userJwt = jwt_token;
  console.log(iFrame_details);
  if (domain_name == "travel" && travel_type == "Air"){
    iFrame_details.templateKey = "air_file";
  }
  else if (domain_name == "travel" && travel_type == "Hotels"){
    iFrame_details.templateKey = "hotel_file";
  }
  else if (domain_name == "travel" && travel_type == "Cars"){
    iFrame_details.templateKey = "cars_file";
  }
  
  importer = oneschemaImporter(iFrame_details);
  console.log(importer);
  importer.launch()

  importer.on("success", (data) => {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'load_raw_data');
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8");
    xhr.setRequestHeader("Authorization", jwt_token);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        // console.log(xhr.status);
        // console.log(xhr.responseText);
        document.getElementById("container").hidden =  true;
        document.getElementById("loading_container").innerHTML =  xhr.responseText;
      }};
    let payload = JSON.stringify(data);
    xhr.send(payload);
  })

  importer.on("cancel", () => {
    // TODO: handle cancel
  })

  importer.on("error", (message) => {
    // TODO: handle errors
  })
}
