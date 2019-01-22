load_time_out = null
time_check_default = 0
// current_web_url = null
current_sk = null
cancel_search = false
shop_searching = false
var $api_request = null
var $shop_request = null
var $shop_active_request = null
var regx = /^[A-Za-z0-9 _.-]+$/;
shop_loaded_data = {}
shop_size = 0
shops_completed = 0

$(function(){
  $(document).on("submit", "#search_form", function(e){
    shop_web_search()
    e.preventDefault();
    return false;
  });
});

function initial_api_search(sk){
  if(!validate_sk(sk)){
    return false
  }

  if($api_request != null){
    $api_request.abort()
    $api_request = null
  }

  if($shop_request != null) {
    $shop_request.abort()
    $shop_request = null
  }

  s_match = document.getElementById("rangeacc").value
  s_hl =  document.getElementById("highlow").checked
  s_lh =  document.getElementById("lowhigh").checked

  gs_data = get_selected_checkboxes()
  if(gs_data.length == 0){
    shops_url = "/websearch/shops.json";
    $shop_request = $.getJSON(shops_url,
        function(data) {
          shops_completed = 0
          shop_size = data.length
          data.sort(() => Math.random() - 0.5)
          var shop_index;
          for(shop_index in data){
            shop_name = data[shop_index]
            search_params = "sk=" + sk + "&smatch=" + s_match + "&shl=" + s_hl + "&slh=" + s_lh + "&shops=" + shop_name
            sk_url = "/api/shop/search?" + search_params;
            api_request = $.getJSON(sk_url,
                function(data) {
                  shops_completed++
                  load_data_container(data, sk)
            });
          }
    });
  }else{
    shops_completed = 0
    shop_size = gs_data.length
    gs_data.sort(() => Math.random() - 0.5)
    var shop_index;
    for(shop_index in gs_data){
      shop_name = gs_data[shop_index]
      search_params = "sk=" + sk + "&smatch=" + s_match + "&shl=" + s_hl + "&slh=" + s_lh + "&shops=" + shop_name
      sk_url = "/api/shop/search?" + search_params;
      $api_request = $.getJSON(sk_url,
          function(gs_data) {
            shops_completed++
            load_data_container(gs_data, sk)
      });
    }
  }
  return false
}

function load_data_container(data, sk){
  if(current_sk != sk){
    if(time_check_default != 0){
      time_check_default = time_check_default - 10
    }
    if($api_request != null){
      $api_request.abort()
      $api_request = null
    }

    if($shop_request != null) {
      $shop_request.abort()
      $shop_request = null
    }
    shop_loaded_data = clear_dict_obj(shop_loaded_data)
    initial_api_search(current_sk)
    return false
  }
  if(!data["message"]){
    d_shop_data = JSON.parse(data[0])
    if(d_shop_data || d_shop_data.length > 0){
      sk = decodeURIComponent(sk)
      sk = truncate_str(sk, 75)
      l_s_name = d_shop_data[sk]["shop_name"]
      if(l_s_name){
        shop_loaded_data[l_s_name] = data
      }
    }
  }
}

function load_shops_cb(){
  $(".alert").hide()
  $("#loading_shop").show()
  shops_url = "/websearch/shops-active.json";
  if($shop_active_request != null) {
    $shop_active_request.abort()
    $shop_active_request = null
  }
  $shop_active_request = $.getJSON(shops_url,
      function(data) {
        replace_shop_find(data)
        $("#loading_shop").hide()
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
    fill_shop_cb = fill_shop_cb.replace(/{shop_name}/g, shop_name)
    fill_shop_cb = fill_shop_cb.replace(/{shop_name_friend}/g, friendly_name_cb(shop_name))
    fill_html_cb.push(fill_shop_cb)
    div_count++
}
  $('#shop_cb_place').html(fill_html_cb.join(""));
}

function friendly_name_cb(shopnamecb){
  friend_name = {
    "SIXPM": "6PM",
    "HM": "H&M"
  }
  name_friend = friend_name[shopnamecb]
  if(name_friend){
      return name_friend
  }

  return shopnamecb
}

function truncate_str(str_val, ln_cnt){
  if(!str_val){
    return str_val
  }
  if(str_val.length > ln_cnt){
    return str_val.slice(0, ln_cnt) + "..."
  }

  return str_val
}

function find_shop(){
  $("#loading_shop").show()
  shop_search_name = document.getElementsByName("shop_search")[0].value
  if(!shop_search_name){
    $("#loading_shop").hide()
    return
  }
  if(!validate_sk(shop_search_name)){
    $('#shop_cb_place').html("No Shop Found");
    $("#loading_shop").hide()
    return
  }
  shops_url = "/websearch/shops-active.json";
  if($shop_active_request != null) {
    $shop_active_request.abort()
    $shop_active_request = null
  }
  $shop_active_request = $.getJSON(shops_url,
      function(data) {
        shop_search_name = shop_search_name.toUpperCase()
        found_shop = []
        for(shop_index in data){
          shop_name = data[shop_index]
          shop_name = friendly_name_cb(shop_name)
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
        $("#loading_shop").hide()
  });

}

function get_selected_checkboxes(){
  var selected_checkboxes = [];
  $("div.custom-checkbox input[type=checkbox]:checked").each(function() {
       selected_checkboxes.push($(this).attr("name").toUpperCase());
  });
  return selected_checkboxes
}

function shop_web_search(){
  $(".alert").hide()
  sk = get_sk_refined()
  if(!validate_sk(sk)){
    $(".alert").show()
    return false
  }

  cancel_search = !cancel_search
  shop_loaded_data = clear_dict_obj(shop_loaded_data)
  if(cancel_search){
    current_sk = sk
    initial_api_search(current_sk)
    shop_searching = true
    document.getElementById("searchButton").disabled = true;
    document.getElementById("searchbar").disabled = true;
    $("#searchButton").hide()
    $("#cancelSearchButton").show()
    time_check_default = 0
    $("#err_msg").hide()
    $(".loading").show()
    load_search_progress_bar()
    set_search_time_out()
  }else{
    shop_searching = false
    reset_controls()
  }

  return false
}

function clear_dict_obj(obj_dict){
  for (var objKey in obj_dict){
    if (obj_dict.hasOwnProperty(objKey)){
        delete obj_dict[objKey];
    }
}
  return {}
}

function validate_sk(sk){
  sk = decodeURIComponent(sk)
  if(!sk || sk == null || !sk.trim() || sk.length < 2 || !regx.test(sk)){
    return false
  }
  return true
}

function reset_controls(){
  if(shop_searching){
    return
  }
  ini_reset_controls()
  return
}

function ini_reset_controls(is_alert=false){
  if(!is_alert){
    $(".alert").hide()
  }

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
  consume_l_data()
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

  obj_so = obj_so || 1500
  refresh_time_out()
  load_time_out = setTimeout(load_shop_search, obj_so)
  return
}

function consume_l_data(){
  sk = current_sk
  res_react_bucket = []
  var shop_index_k;
  for (shop_index_k in shop_loaded_data){
    shop_loaded_data_v = shop_loaded_data[shop_index_k]
    var shop_each_index_k;
    for(shop_each_index_k in shop_loaded_data_v){
      shop_each_d_v = JSON.parse(shop_loaded_data_v[shop_each_index_k])
      if(!shop_each_d_v){
        continue
      }
      sk = decodeURIComponent(sk)
      sk = truncate_str(sk, 75)
      sk_shop_each_d_v = shop_each_d_v[sk]
      if (!sk_shop_each_d_v){
        continue
      }

      res_react = $('#resultreact_default').html();
      res_react_html = document.createElement("div")
      res_react_html.innerHTML = res_react
      res_react_html.querySelectorAll("#p_link")[0].href = sk_shop_each_d_v["shop_link"] || ""
      res_react_html.querySelector("#p_img_link").src = sk_shop_each_d_v["image_url"] || ""
      res_react_html.querySelector("#p_img_link").alt = sk_shop_each_d_v["title"] || ""
      res_react_html.querySelectorAll("#p_link")[1].href = sk_shop_each_d_v["shop_link"] || ""
      res_react_html.querySelectorAll("#p_link")[1].innerText=(sk_shop_each_d_v["title"] || "")
      res_react_html.querySelector("#p_description").innerText=(sk_shop_each_d_v["content_description"] || "")
      res_react_html.querySelector("#p_price").innerText=("Price: " + sk_shop_each_d_v["price"] || "")
      res_react_html.querySelector("#p_shopname").innerText=("Shop: " + sk_shop_each_d_v["shop_name"] || "")
      res_react_bucket.push($(res_react_html).html())
    }
  }
  if(res_react_bucket.length == 0){
    if(time_check_default != 100){
      shop_searching = true
      time_check_default = time_check_default + 10
      set_search_time_out(3000, true)
    }else{
      $(".alert").html("<strong>Sorry, no products found</strong>, refine search criteria.")
      $(".alert").show()
      shop_searching = false
      ini_reset_controls(true)
    }
    return
  }
  spin_shop_default_htm = $("#spin_shop_default").html()
  res_rock_spinner = res_react_bucket.join("") + spin_shop_default_htm
  reactelem = $("<div class=\"row\">" + res_rock_spinner + "</div>")
  $('#resultreact').html(reactelem)
  shop_searching = false
  reset_controls()
  if (shops_completed != shop_size){
    load_time_out = setTimeout(refresh_shop_data, 3000)
  }else{
    refresh_time_out()
    $("#spin_shop").hide()
  }
}


function refresh_shop_data(){
  if(shop_searching){
    return
  }
  consume_l_data()
  return false
}

function restart_progress_bar(){
  var container = document.getElementById("searchProgress");
  var content = container.innerHTML;
  container.innerHTML= content;
  var elem = document.getElementById("searchProgressBar");
  elem.style.width = 1 + '%';
}

function load_search_progress_bar() {
  var elem = document.getElementById("searchProgressBar");
  var width = 1;
  var id = setInterval(frame, 3000);
  function frame() {
    if (width >= 100) {
      clearInterval(id);
    } else {
      width++;
      elem.style.width = width + '%';
      elem.attributes["aria-valuenow"] = width
    }
  }
  return false
}
