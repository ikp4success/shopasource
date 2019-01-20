load_time_out = null
time_check_default = 0
current_web_url = null
current_sk = null
cancel_search = false
shop_searching = false

$(function() {
  $(document).on('click', 'div#shopsearch', function() {
    sk = get_sk_refined()
    initial_api_search(sk)
  });
});

$(function() {
  $(document).on('blur', '.mr-sm-2', function() {
    sk = get_sk_refined()
    initial_api_search(sk)
  });
});

$(function(){
  $(document).on("submit", "#search_form", function(e){
    shop_web_search()
    e.preventDefault();
    return false;
  });
});

function initial_api_search(sk){
  if(!sk || sk==null){
    return false
  }
  if(get_selected_checkboxes().length == 0){
    shops_url = "/websearch/shops.json";
    $.getJSON(shops_url,
        function(data) {
          data.sort(() => Math.random() - 0.5)
          var shop_index;
          for(shop_index in data){
            shop_name = data[shop_index]
            sk_url = "/api/shop/" + shop_name + "/search=" + sk;
            $.getJSON(sk_url,
                function(data) {
            });
          }
    });
  }else{
    gs_data = get_selected_checkboxes()
    gs_data.sort(() => Math.random() - 0.5)
    var shop_index;
    for(shop_index in gs_data){
      shop_name = gs_data[shop_index]
      sk_url = "/api/shop/" + shop_name + "/search=" + sk;
      $.getJSON(sk_url,
          function(gs_data) {
      });
    }
  }


  return false
}

function load_shops_cb(){
  shops_url = "/websearch/shops-active.json";
  $.getJSON(shops_url,
      function(data) {
        replace_shop_find(data)
  });
}

function replace_shop_find(data){
  var fill_html_cb = [];
  fill_html_cb.length = 0
  document.getElementById("shop_cb_place").innerHTML = ""
  var shop_index;
  data.sort();
  fill_html_cb.push("<div class=\"spx\">")
  div_count = 0
  for(shop_index in data){
    if(div_count == 5){
      div_count = 0
      fill_html_cb.push("</div>")
      fill_html_cb.push("<div class=\"spx\">")
    }
    shop_name = data[shop_index]
    fill_shop_cb = $("#shop_cb_default").html()
    fill_shop_cb = fill_shop_cb.replace(/{shop_id}/g, shop_name + "cb")
    fill_shop_cb = fill_shop_cb.replace("{shop_name}", shop_name)
    fill_html_cb.push(fill_shop_cb)
    div_count++
}
  $('#shop_cb_place').html(fill_html_cb.join(""));
}

function find_shop(){
  shop_search_name = document.getElementsByName("shop_search")[0].value
  if(shop_search_name == null){
    return
  }
  shops_url = "/websearch/shops-active.json";
  $.getJSON(shops_url,
      function(data) {
        shop_search_name = shop_search_name.toUpperCase()
        found_shop = []
        for(shop_index in data){
          shop_name = data[shop_index]
          if(shop_name.includes(shop_search_name)){
            found_shop.push(shop_name)
          }
        }
        if(found_shop.length > 0){
          replace_shop_find(found_shop)
        }
        else{
          $('#shop_cb_place').html("No Shop Found");
        }
  });

}

function get_selected_checkboxes(){
  var selected_checkboxes = [];
  $(document).ready(function() {
    $("input:checkbox[name=type]:checked").each(function() {
         selected_checkboxes.push($(this).val().toUpperCase());
    });
  });
  return selected_checkboxes
}

function shop_web_search(){
  sk = get_sk_refined()
  if(!sk){
    alert("textbox is empty")
    return false
  }
  cancel_search = !cancel_search
  if(cancel_search){
    shop_searching = true
    document.getElementById("searchButton").disabled = true;
    document.getElementById("searchbar").disabled = true;
    $("#searchButton").hide()
    $("#cancelSearchButton").show()
    time_check_default = 0
    $("#err_msg").hide()
    current_sk = sk
    $(".loading").show()
    restart_progress_bar()
    load_search_progress_bar()
    set_search_time_out()
  }else{
    shop_searching = false
    reset_controls()
  }

  return false
}

function reset_controls(){
  if(shop_searching){
    return
  }
  ini_reset_controls()
  return
}

function ini_reset_controls(){
  $(".loading").hide()
  restart_progress_bar()
  $("#searchButton").show()
  $("#cancelSearchButton").hide()
  document.getElementById("searchButton").disabled = false;
  document.getElementById("searchbar").disabled = false;
  refresh_time_out()
  cancel_search = false
  time_check_default = 0
  return
}

function load_shop_search(){
  sk = get_sk_refined()
  s_match = document.getElementById("rangeacc").value
  s_hl =  document.getElementById("highlow").checked
  s_lh =  document.getElementById("lowhigh").checked
  search_params = "sk=" + sk + "&smatch=" + s_match + "&shl=" + s_hl + "&slh=" + s_lh
  web_search_url = "/websearch/shop/search?" + search_params;
  $.get(web_search_url,
      function(data) {
        current_web_url = web_search_url
        dynamic_content(data, true)
  });
  return false
}

function get_sk_refined(){
  sk = document.getElementsByName("search")[0].value
  if(sk == null){
    return sk
  }
  if(sk.includes("/"))
    return encodeURIComponent(encodeURIComponent(sk))
  return encodeURIComponent(sk)
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
    sk = get_sk_refined()
  }

  obj_so = obj_so || 3000
  refresh_time_out()
  load_time_out = setTimeout(load_shop_search, obj_so)
  return
}

function dynamic_content(data, refresh_shop_search){
  if(!data.includes("{REACT_RESULT_ROW}")){
    if(refresh_shop_search){
      var shopsearchelem = $(data).filter("#shopsearch")
      $("#shopsearch").replaceWith(shopsearchelem)
    }
    var reactelem = $(data).find("#resultreact")
    $("#resultreact").replaceWith(reactelem)
    shop_searching = false
    reset_controls()
    load_time_out = setTimeout(refresh_shop_data, 3000)
  }else{
    if(time_check_default != 50){
      shop_searching = true
      time_check_default = time_check_default + 10
      set_search_time_out(5000, true)
    }else{
      var shopsearchelem = $(data).filter("#shopsearch")
      $("#shopsearch").replaceWith(shopsearchelem)
      var result = $(data).filter(".results")
      $(".results").replaceWith(result)
      $("#resultreact").hide()
      shop_searching = false
      reset_controls()
    }

  }

  return
}


function refresh_shop_data(){
  if(current_web_url != null){
    $.get(current_web_url,
        function(data) {
          if(shop_searching){
            return
          }
          dynamic_content(data)
        });
  }
  return false
}

function restart_progress_bar(){
  var container = document.getElementById("searchProgress");
  var content = container.innerHTML;
  container.innerHTML= content;
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
