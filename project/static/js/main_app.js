load_time_out = null
refresh_shop_data_tout = null
current_web_url = null
current_sk = null

$(function() {
  $(document).on('click', 'div#shopsearch', function() {
    sk = document.getElementsByName("search")[0].value
    initial_api_search(sk)
  });
});

$(function() {
  $(document).on('blur', '.mr-sm-2', function() {
    sk = document.getElementsByName("search")[0].value
    initial_api_search(sk)
  });
});

$("#searchbar").keyup(function(event) {
    if (event.keyCode === 13) {
        $("#searchButton").click();
    }
});

function initial_api_search(sk){
  if(!sk){
    return false
  }
  // if(click_event){
  // 	$.ajaxSetup({async: false});
  // }
  sk_url = "/api/shop/search=" + encodeURIComponent(encodeURIComponent(sk));
  $.getJSON(sk_url,
      function(data) {
  });
  return false
}

function shop_web_search(){
  document.getElementById("searchButton").disabled = true;
  document.getElementById("searchbar").disabled = true;
  sk = document.getElementsByName("search")[0].value
  if(!sk){
    alert("textbox is empty")
    return false
  }
  current_sk = sk
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
        current_web_url = web_search_url
        dynamic_content(data, true)
        // clearTimeout(refresh_shop_data_tout)
  });
  return false
}

function refresh_time_out(){
  if(load_time_out != null){
    clearTimeout(load_time_out)
    load_time_out = null
  }
  return
}

function set_search_time_out(obj_so, refresh_api){
  if(refresh_api){
    sk = document.getElementsByName("search")[0].value
    initial_api_search(sk)
  }

  obj_so = obj_so || 10000
  refresh_time_out()
  load_time_out = setTimeout(load_shop_search, obj_so)
  return
}

function dynamic_content(data, refresh_shop_search){
  if(!data.includes("{REACT_RESULT_ROW}")){
    $(".loading").hide()
    document.getElementById("searchButton").disabled = false;
    document.getElementById("searchbar").disabled = false;
    if(refresh_shop_search){
      var shopsearchelem = $(data).filter("#shopsearch")
      $("#shopsearch").replaceWith(shopsearchelem)
    }
    var reactelem = $(data).find("#resultreact")
    $("#resultreact").replaceWith(reactelem)
    refresh_time_out()
    load_time_out = setTimeout(refresh_shop_data)
  }else{
    set_search_time_out(20000, true)
  }


  return
}

function refresh_shop_data(){
  initial_api_search(current_sk)
  if(current_web_url != null){
    $.get(current_web_url,
        function(data) {
          dynamic_content(data)
        });
  }
  return false
}
function load_search_progress_bar() {
  var elem = document.getElementById("searchProgressBar");
  var width = 1;
  var id = setInterval(frame, 4500);
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
