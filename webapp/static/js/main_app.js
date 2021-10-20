friend_name = {
  "SIXPM": "6PM",
  "HM": "H&M",
  "MVMTWATCHES": "MVMT WATCHES",
  "SPIRITUALGANGSTER": "SPIRITUAL GANGSTER",
  "MACYS": "MACY'S",
  "SAKSFIFTHAVENUE": "SAKS FIFTH AVENUE",
  "NORDSTROMRACK": "NORDSTROM RACK",
  "CHARLOTTERUSSE": "CHARLOTTE RUSSE",
  "SHOPQUEEN": "SHOP QUEEN",
  "DICKSSPORTINGGOODS": "DICKS SPORTING GOODS"
}
load_time_out = null
load_next_btn = false
time_check_default = 0
current_sk = null
cancel_search = false
shop_searching = false
var $api_request = null
var $shop_request = null
var $shop_active_request = null
var regx = /^[A-Za-z0-9 _.-\\'\\,\\-]+$/;
var shops_drop = null
var scraped_shops = []
shop_loaded_data = {}
shop_job_ids = []
shop_size = 0
shops_completed = 0
is_filter = false
item_size = 0
max_item_size = 30
current_count = 0
returned_item_size = max_item_size
width_prog_check = 2
public_api_key = null

$(function(){
  $(document).on("submit", "#search_form", function(e){
    shop_web_search()
    e.preventDefault();
    return false;
  });
});

$(function(){
  $(document).on("click", "input[type=checkbox]", function(e){
    if(get_selected_checkboxes().length > 0){
      if(scraped_shops.length > 0){
        disable_controls(false)
      }else if(get_selected_checkboxes().length == 1){
        disable_controls(false)
      }
      else{
        disable_controls()
      }
    }else{
      if(scraped_shops.length > 0){
        disable_controls(false)
      }else{
        disable_controls()
      }
    }
  });
});

function disable_controls(disabled=true){
  if(disabled){
    document.getElementById("highlow").disabled = disabled;
    document.getElementById("lowhigh").disabled = disabled;
  }
  document.getElementById("highlow").disabled = disabled;
  document.getElementById("lowhigh").disabled = disabled;
}


function exe_filter(){
  if (scraped_shops.length <= 0){
        item_size = 0
        max_item_size = 30
        returned_item_size = max_item_size
        $(".alert").html("<strong>No Data to filter</strong>, search and then filter.")
        $(".alert").show()
        radiobtn = document.getElementById("highlow");
        radiobtn.checked = true;
        $("#filterButton").hide()
        $("#cancelFilterButton").hide()
        if(get_selected_checkboxes().length > 0){
          disable_controls()
        }
        return
  }else{
    item_size = 0
    max_item_size = 30
    returned_item_size = max_item_size
    $("#load_next").hide()
    disable_controls(false)
    sshp = scraped_shops.join(",")
    if(get_selected_checkboxes().length > 0){
      n_sshp = []
      var shp_index;
      for(shp_index in get_selected_checkboxes()){
        sel_name = get_selected_checkboxes()[shp_index]
        if(scraped_shops.includes(sel_name)){
          n_sshp.push(sel_name)
        }
      }
      if(n_sshp.length > 0){
        sshp = n_sshp.join(",")
      }else{
        $(".alert").html("<strong>Sorry, no products found</strong>, refine search criteria.")
        $(".alert").show()
        return
      }

    }
      is_filter = true
      $("#filterButton").hide()
      $("#cancelFilterButton").show()
      c_match = document.getElementById("rangeacc").value
      c_hl =  document.getElementById("highlow").checked
      c_lh =  document.getElementById("lowhigh").checked
      shop_size = scraped_shops.length
      refresh_time_out()
      initial_api_search(current_sk, sshp, c_match, c_hl, c_lh)
      load_time_out = setTimeout(refresh_shop_data, 1000)
      $("#err_msg").hide()
      $(".loading").show()
      restart_progress_bar()
      load_search_progress_bar()
  }

}

function ini_filter_reset_controls(){
  $("#cancelFilterButton").hide()
  $("#filterButton").show()
  ini_reset_controls()
}


function initial_api_search(sk, fil_shop_name=null, c_match=null, c_hl=null, c_lh=null){
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

  $.ajaxSetup({
    async: true,
    headers: {
      'x-api-key': public_api_key,
    }
  });

  s_match = c_match || document.getElementById("rangeacc").value
  s_hl = document.getElementById("highlow").checked
  if(c_hl != null){
    s_hl = c_hl
  }

  s_lh = document.getElementById("lowhigh").checked
  if(c_lh != null){
    s_lh = c_lh
  }

  if(!s_lh && !s_hl){
    s_hl = true
  }

  gs_data = get_selected_checkboxes()
  shops_completed = 0

  if(fil_shop_name){
    search_params = "sk=" + sk + "&smatch=" + s_match + "&shl=" + s_hl + "&slh=" + s_lh + "&shops=" + fil_shop_name
    sk_url = "/api/shop/search?" + search_params + "&async=1";
    shop_loaded_data = clear_dict_obj(shop_loaded_data)
    api_request = $.getJSON(sk_url,
        function(data) {
          if(!data["error"]){
            shop_job_ids = []
            shop_job_ids.push(data)
            load_job([data], sk)
          }
          shops_completed = shop_size
    }).fail(
      function()
      {
        shops_completed = shop_size
      });
  }
  else if(gs_data.length == 0){
    shop_job_ids = []
    shops_url = "/api/shops-active.json";
    $shop_request = $.getJSON(shops_url,
        function(data) {
          shops_drop = data
          shop_size = data.length
          data.sort(() => Math.random() - 0.5)
          var shop_index;
          for(shop_index in data){
            shop_name = data[shop_index]
            search_params = "sk=" + sk + "&smatch=" + s_match + "&shl=" + s_hl + "&slh=" + s_lh + "&shops=" + shop_name
            sk_url = "/api/shop/search?" + search_params + "&async=1";

            $api_request = $.getJSON(sk_url,
                function(data) {
                  shop_job_ids.push(data)
            }).fail(
              function()
              {
                shops_completed++
              });
          }
    });
  }else{
    shop_job_ids = []
    shop_size = gs_data.length
    gs_data.sort(() => Math.random() - 0.5)
    var shop_index;
    for(shop_index in gs_data){
      shop_name = gs_data[shop_index]
      search_params = "sk=" + sk + "&smatch=" + s_match + "&shl=" + s_hl + "&slh=" + s_lh + "&shops=" +  shop_name
      sk_url = "/api/shop/search?" + search_params + "&async=1";

      $api_request = $.getJSON(sk_url,
          function(gs_data) {
            shop_job_ids.push(data)
      }).fail(
        function()
        {
          shops_completed++
        });
    }
  }
  return false
}

function load_public_api_key(){
  if($api_request != null){
    $api_request.abort()
    $api_request = null
  }

  if($shop_request != null) {
    $shop_request.abort()
    $shop_request = null
  }

  $.ajaxSetup({
    async: true
  });

  api_url = "/api/public_api_key";
  $api_request = $.getJSON(api_url,
      function(data) {
        public_api_key = data.public_api_key
        shop_web_search()

  }).fail(
    function(data)
    {
      res = data.responseJSON
      if(res.error){
        $(".alert").html(`<strong>API Error</strong> - ` + res.error)
        $(".alert").show()
      }
    });
}

function load_job(data, sk){
  if($api_request != null){
    $api_request.abort()
    $api_request = null
  }

  if($shop_request != null) {
    $shop_request.abort()
    $shop_request = null
  }

  $.ajaxSetup({
    async: true,
    headers: {
      'x-api-key': public_api_key,
    }
  });

  if (data == null){
    data = shop_job_ids
  }

  for (job_id_index in data){
    job_id = shop_job_ids[job_id_index]["job_id"]
    jb_url = "/api/get_result?job_id=" + job_id;
    $api_request = $.getJSON(jb_url,
        function(gs_data) {
          load_data_container(gs_data["data"], sk)
    })
  }
}


function load_data_container(data, sk){
  if(data==null){
    return
  }
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
  if(!data["error"]){
    d_shop_data = data
    if(d_shop_data || d_shop_data.length > 0){
      var shop_sk_index
      sk = decodeURIComponent(sk)
      sk = truncate_str(sk, 75)

      var shop_sk_index
      for(shop_sk_index in d_shop_data){
        dshjson = d_shop_data[shop_sk_index]
        l_s_name = dshjson["shop_name"]
        if(l_s_name){
          if(!scraped_shops.includes(l_s_name)){
            scraped_shops.push(l_s_name)
          }

          shop_loaded_data[l_s_name] = data
        }
      }

    }
  }
  shops_completed++
}

function load_shops_cb(){
  $(".alert").hide()
  $("#loading_shop").show()
  if(shops_drop){
    replace_shop_find(shops_drop)
    $("#loading_shop").hide()
    return
  }
  shops_url = "/api/shops-active.json";
  if($shop_active_request != null) {
    $shop_active_request.abort()
    $shop_active_request = null
  }
  $.ajaxSetup({
    async: true,
    headers: {
      'x-api-key': public_api_key,
    }
  });
  $shop_active_request = $.getJSON(shops_url,
      function(data) {
        shops_drop = data
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
    load_shops_cb()
    return
  }
  if(!validate_sk(shop_search_name)){
    $('#shop_cb_place').html("No Shop Found");
    $("#loading_shop").hide()
    return
  }
  if(shops_drop){
    exe_find_shop(shops_drop)
    return
  }
  shops_url = "/api/shops-active.json";
  if($shop_active_request != null) {
    $shop_active_request.abort()
    $shop_active_request = null
  }
  $.ajaxSetup({
    async: true,
    headers: {
      'x-api-key': public_api_key,
    }
  });
  $shop_active_request = $.getJSON(shops_url,
      function(data) {
        shops_drop = data
        exe_find_shop(data)
  });

}

function exe_find_shop(data){
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
  if (!public_api_key || public_api_key == null){
    load_public_api_key()
    return
  }

  cancel_search = !cancel_search
  shop_loaded_data = clear_dict_obj(shop_loaded_data)
  shop_job_ids = []
  if(cancel_search){
    item_size = 0
    max_item_size = 30
    current_count = 0
    returned_item_size = max_item_size
    $("#load_next").hide()
    $("#filterButton").hide()
    $("#cancelFilterButton").hide()
    disable_controls()
    is_filter = false
    scraped_shops = []
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
    set_search_time_out(20, true)
  }else{
    shop_searching = false
    reset_controls()
  }

  return false
}

function load_next(){
    if(shop_searching){
      $('#spin_shop').hide()
      return false
    }
    if(shop_size == 0){
      $('#spin_shop').hide()
      return false
    }
    if($('#spin_shop').css('display') == 'none'){
        $('#spin_shop').show()
    }
    item_size = 0
    max_item_size = max_item_size + 30
    $("#load_next").hide()
    load_next_btn = true
    refresh_time_out()
    load_time_out = setTimeout(refresh_shop_data, 1000)
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
  if($api_request != null){
    $api_request.abort()
    $api_request = null
  }

  if($shop_request != null) {
    $shop_request.abort()
    $shop_request = null
  }
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
    width_progress = document.getElementById("searchProgressBar").style.width
    if(parseInt(width_progress.replace("%", "")) > width_prog_check){
      width_prog_check = width_prog_check + 1
      kickstart_initial_api_search()
    }
  }

  obj_so = obj_so || 1500
  refresh_time_out()
  load_time_out = setTimeout(load_shop_search, obj_so)
  return
}

function count_returned_item(re_item){
  count = 0
  for (shop_index_k in shop_loaded_data){
    re_item = shop_loaded_data[shop_index_k]
    for(shop_each_index_k in re_item){
      try{
        shop_each_d_v = shop_loaded_data_v[shop_each_index_k]

        if(!shop_each_d_v){
          continue
        }

        count++
      }catch(err){
        count++
        continue
      }
    }
  }

  return count
}

function consume_l_data_child(shop_loaded_data_v, sk){
  res_react_bucket_child = []
  var shop_each_index_k;
  for(shop_each_index_k in shop_loaded_data_v){
    try{
      if(item_size == max_item_size){
        break;
      }

      shop_each_d_v = shop_loaded_data_v[shop_each_index_k]
      if(!shop_each_d_v){
        continue
      }

      res_react = $('#resultreact_default').html();
      res_react_html = document.createElement("div")
      res_react_html.innerHTML = res_react
      res_react_html.querySelectorAll("#p_link")[0].href = shop_each_d_v["shop_link"] || ""
      res_react_html.querySelector("#p_img_link").src = shop_each_d_v["image_url"] || ""
      res_react_html.querySelector("#p_img_link").alt = shop_each_d_v["title"] || ""
      res_react_html.querySelectorAll("#p_link")[1].href = shop_each_d_v["shop_link"] || ""
      res_react_html.querySelectorAll("#p_link")[1].innerText=(shop_each_d_v["title"] || "")
      res_react_html.querySelector("#p_description").innerText=(shop_each_d_v["content_description"] || "")
      res_react_html.querySelector("#p_price").innerText=("Price: " + shop_each_d_v["price"] || "")
      res_react_html.querySelector("#p_shopname").innerText=("Shop: " + shop_each_d_v["shop_name"] || "")
      if(res_react_bucket_child.includes($(res_react_html).html())){
        continue
      }
      item_size++
      res_react_bucket_child.push($(res_react_html).html())
    }catch(err){
      continue
    }
  }

  return res_react_bucket_child

}

function consume_l_data(){
  sk = current_sk
  res_react_bucket = []
  var shop_index_k;
  sld = shop_loaded_data
  for (shop_index_k in shop_loaded_data){
    shop_loaded_data_v = shop_loaded_data[shop_index_k]
    res_react_bucket.push.apply(res_react_bucket, consume_l_data_child(shop_loaded_data_v, sk))
  }

  if(res_react_bucket.length == 0){
    max_t_chk_def = 99999
    if(is_filter){
      if($('#spin_shop').css('display') != 'none'){
          max_t_chk_def = 80
      }else{
        max_t_chk_def = 30
      }
    }
    width_progress = document.getElementById("searchProgressBar").style.width
    if(width_progress != "100%"){
      shop_searching = true
      time_check_default = time_check_default + 1
      set_search_time_out(30, true)
    }else{
      $(".alert").html("<strong>Sorry, no products found</strong>, refine search criteria.")
      $(".alert").show()
      shop_searching = false
      ini_reset_controls(true)
      if(!is_filter){
        $("#filterButton").hide()
        $("#cancelFilterButton").hide()
      }else{
        $("#filterButton").show()
        $("#cancelFilterButton").hide()
      }
    }
    return
  }

  if(!is_filter){
    $("#filterButton").show()
    disable_controls(false)
    if($('#spin_shop').css('display') == 'none'){
      radiobtn = document.getElementById("highlow");
      radiobtn.checked = true;
    }
  }

  spin_shop_default_htm = $("#spin_shop_default").html()
  load_next_default_htm = $("#load_next_default").html()
  res_rock_spinner_next = res_react_bucket.join("") + spin_shop_default_htm + load_next_default_htm

  reactelem = $("<div class=\"row\">" + res_rock_spinner_next + "</div>")
  $('#resultreact').empty()
  $('#resultreact').html(reactelem)
  shop_searching = false
  reset_controls()
  if (shops_completed >= shop_size){
      returned_item_size = count_returned_item(sld)
      current_count = returned_item_size
      refresh_time_out()
      $("#spin_shop").hide()
      $(".loading").hide()
      $("#filterButton").show()
      $("#cancelFilterButton").hide()
      if (max_item_size > returned_item_size){
         $("#load_next").hide()
         load_next_btn = false
      }else{
        if(load_next_btn && current_count != returned_item_size){
          $("#load_next").hide()
          $("#spin_shop").show()
          item_size = 0
          refresh_time_out()
          load_time_out = setTimeout(refresh_shop_data, 3000)
        }else{
          $("#spin_shop").hide()
          $("#load_next").show()
        }

      }
  }else{
    if(!is_filter){
      $("#filterButton").hide()
      $("#cancelFilterButton").hide()
      $(".alert").html("<strong>filter not available at the moment<strong>, refine search if filter taking to long to show")
      $(".alert").show()
    }
    if(item_size < 30){
      item_size = 0
      refresh_time_out()
      load_time_out = setTimeout(refresh_shop_data, 3000)
   }else{
     if (max_item_size > returned_item_size && shops_completed >= shop_size){
        $("#load_next").hide()
     }
     else if (max_item_size >= returned_item_size){
        $("#load_next").show()
     }
      refresh_time_out()
    if(load_next_btn && current_count != returned_item_size){
      $("#load_next").hide()
      $("#spin_shop").show()
      item_size = 0
      refresh_time_out()
      load_time_out = setTimeout(refresh_shop_data, 3000)
      $(".loading").hide()
      return
    }else{
      $("#spin_shop").hide()
    }
     $(".loading").hide()
     $("#filterButton").show()
     $("#cancelFilterButton").hide()
     $(".alert").hide()
   }
  }
}

function kickstart_initial_api_search(){
  load_job(shop_job_ids, current_sk)
}

function refresh_shop_data(){
  if(shop_searching){
    return
  }
  consume_l_data()
  if(load_next_btn){
    kickstart_initial_api_search()
  }
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
