load_time_out = null
refresh_shop_data_tout = null
current_web_url = null

$(function() {
  $('div#shopsearch').bind('click', function() {
    initial_api_search()
    return false
  });
});

$(function() {
  $('.mr-sm-2').bind('blur', function() {
    initial_api_search()
  });
});

function initial_api_search(){
  sk = document.getElementsByName("search")[0].value
  if(!sk){
    return false;
  }
  // if(click_event){
  // 	$.ajaxSetup({async: false});
  // }
  sk_url = "/api/shop/search=" + encodeURIComponent(encodeURIComponent(sk));
  $.getJSON(sk_url,
      function(data) {
  });
  return false;
}

function shop_web_search(){
  sk = document.getElementsByName("search")[0].value
  if(!sk){
    alert("textbox is empty")
    return false;
  }
  $(".loading").show();
  load_search_progress_bar()
  set_search_time_out()

  return false
}
function load_shop_search(){
  sk = document.getElementsByName("search")[0].value
  web_search_url = "/websearch/shop/search=" + encodeURIComponent(encodeURIComponent(sk));
  // window.location.replace(web_search_url)
  $.get(web_search_url,
      function(data) {
        search_start = false
        current_web_url = web_search_url
        dynamic_content(data)
        clearTimeout(refresh_shop_data_tout)
        refresh_shop_data_tout = setTimeout(refresh_shop_data, 5000)
  });
  return false
}

function set_search_time_out(){
  if(load_time_out != null){
    clearTimeout(load_time_out)
  }
  load_time_out = setTimeout(load_shop_search, 10000)
  return false
}

function dynamic_content(data){
  var shopsearchelem = $(data).filter("#shopsearch")
  var reactelem = $(data).find("#resultreact")
  $("#shopsearch").replaceWith(shopsearchelem)
  $("#resultreact").replaceWith(reactelem)
  return false
}

function refresh_shop_data(){
  if(current_web_url != null){
    $.get(web_search_url,
        function(data) {
          dynamic_content(data)
        });
  }
  return false
}
function load_search_progress_bar() {
  var elem = document.getElementById("searchProgressBar");
  var width = 1;
  var id = setInterval(frame, 1000);
  function frame() {
    if (width >= 100) {
      clearInterval(id);
    } else {
      width++;
      elem.style.width = width + '%';
    }
  }
  return false
}
