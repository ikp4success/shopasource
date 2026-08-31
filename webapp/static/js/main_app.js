var regx = /^[A-Za-z0-9 _.-\\'\\,\\-]+$/;

var publicApiKey = null;
var loadingApiKey = false;
var apiKeyCallbacks = [];

var searching = false;
var currentSk = null;
var currentJobId = null;
var pollTimer = null;
var progressTimer = null;

var allResults = [];
var shownCount = 0;
var PAGE_SIZE = 30;
var POLL_INTERVAL_MS = 2000;
var minPriceFilter = null;
var maxPriceFilter = null;

var $searchRequest = null;
var $pollRequest = null;

$(function () {
  $(document).on("submit", "#search_form", function (e) {
    shop_web_search();
    e.preventDefault();
    return false;
  });
  $(document).on("input", "#minPrice, #maxPrice", function () {
    var minVal = document.getElementById("minPrice").value;
    var maxVal = document.getElementById("maxPrice").value;
    minPriceFilter = minVal === "" ? null : parseFloat(minVal);
    maxPriceFilter = maxVal === "" ? null : parseFloat(maxVal);
    $("#clearPriceFilter").toggle(minPriceFilter != null || maxPriceFilter != null);
    shownCount = 0;
    render_results();
  });
  $(document).on("click", "#clearPriceFilter", function () {
    document.getElementById("minPrice").value = "";
    document.getElementById("maxPrice").value = "";
    minPriceFilter = null;
    maxPriceFilter = null;
    $("#clearPriceFilter").hide();
    shownCount = 0;
    render_results();
  });
  ensure_public_api_key(populate_model_select);
});

// ---------- API key ----------

function ensure_public_api_key(cb) {
  if (publicApiKey != null) {
    cb();
    return;
  }
  apiKeyCallbacks.push(cb);
  if (loadingApiKey) {
    return;
  }
  loadingApiKey = true;
  $.getJSON("/api/public_api_key", function (data) {
    publicApiKey = data.public_api_key;
    $.ajaxSetup({ headers: { "x-api-key": publicApiKey } });
    loadingApiKey = false;
    var callbacks = apiKeyCallbacks;
    apiKeyCallbacks = [];
    callbacks.forEach(function (fn) {
      fn();
    });
  }).fail(function (xhr) {
    loadingApiKey = false;
    apiKeyCallbacks = [];
    handle_fail(xhr);
  });
}

// ---------- Model picker ----------

function populate_model_select() {
  var modelSelect = document.getElementById("modelSelect");
  if (!modelSelect) {
    return;
  }
  $.getJSON("/api/llm-providers.json", function (data) {
    modelSelect.innerHTML = "";
    if (!data || data.length === 0) {
      var opt = document.createElement("option");
      opt.textContent = "No model configured";
      modelSelect.appendChild(opt);
      modelSelect.disabled = true;
      return;
    }
    data.forEach(function (p) {
      var opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.label;
      modelSelect.appendChild(opt);
    });
  });
}

// ---------- Search ----------

function get_sk_refined() {
  var sk = document.getElementsByName("search")[0].value;
  if (sk == null) {
    return sk;
  }
  if (sk.includes("/")) {
    return encodeURIComponent(encodeURIComponent(sk));
  }
  return encodeURIComponent(sk);
}

function validate_sk(sk) {
  sk = decodeURIComponent(sk);
  if (!sk || sk == null || !sk.trim() || sk.length < 2 || !regx.test(sk)) {
    return false;
  }
  return true;
}

function shop_web_search() {
  $(".alert").hide();
  var sk = get_sk_refined();
  if (!validate_sk(sk)) {
    $(".alert").show();
    return false;
  }
  if (searching) {
    cancel_search();
    return false;
  }
  ensure_public_api_key(function () {
    start_search(sk);
  });
  return false;
}

function start_search(sk) {
  var shopsearch = document.getElementById("shopsearch");
  if (shopsearch) {
    shopsearch.className = "ResultSearch";
  }
  currentSk = sk;
  currentJobId = null;
  allResults = [];
  shownCount = 0;
  minPriceFilter = null;
  maxPriceFilter = null;
  searching = true;

  document.getElementById("minPrice").value = "";
  document.getElementById("maxPrice").value = "";
  $("#clearPriceFilter").hide();
  $("#priceFilter").hide();
  $("#resultreact").empty();
  $("#load_next").hide();
  $(".alert").hide();
  document.getElementById("searchButton").style.display = "none";
  document.getElementById("cancelSearchButton").style.display = "inline-block";
  document.getElementById("searchbar").disabled = true;

  restart_progress_bar();
  $("#searchProgress").show();
  load_search_progress_bar();

  var modelSelect = document.getElementById("modelSelect");
  var provider = modelSelect && modelSelect.value ? modelSelect.value : "";
  var url = "/api/shop/nl_search?q=" + sk + "&async=1";
  if (provider) {
    url += "&provider=" + encodeURIComponent(provider);
  }

  if ($searchRequest != null) {
    $searchRequest.abort();
  }
  $searchRequest = $.getJSON(url, function (data) {
    if (data.error) {
      show_error(data.error);
      finish_search();
      return;
    }
    currentJobId = data.job_id;
    poll_result();
  }).fail(function (xhr) {
    handle_fail(xhr);
  });
}

function poll_result() {
  if (!searching || !currentJobId) {
    return;
  }
  if ($pollRequest != null) {
    $pollRequest.abort();
  }
  $pollRequest = $.getJSON(
    "/api/get_result?job_id=" + currentJobId,
    function (res) {
      if (res.data && Object.prototype.toString.call(res.data) === "[object Array]") {
        allResults = res.data;
        render_results();
      }
      if (res.status === "done" || res.status === "job not found") {
        finish_search();
      } else if (searching) {
        pollTimer = setTimeout(poll_result, POLL_INTERVAL_MS);
      }
    }
  ).fail(function (xhr) {
    handle_fail(xhr);
  });
}

function cancel_search() {
  searching = false;
  if (pollTimer != null) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
  if ($searchRequest != null) {
    $searchRequest.abort();
    $searchRequest = null;
  }
  if ($pollRequest != null) {
    $pollRequest.abort();
    $pollRequest = null;
  }
  ini_reset_controls();
}

function ini_reset_controls() {
  searching = false;
  if (pollTimer != null) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
  $("#searchProgress").hide();
  document.getElementById("searchButton").style.display = "inline-block";
  document.getElementById("cancelSearchButton").style.display = "none";
  document.getElementById("searchbar").disabled = false;
}

function finish_search() {
  ini_reset_controls();
  if (allResults.length === 0) {
    show_error("Sorry, no products found - try a different search.");
  }
}

function show_error(msg) {
  $(".alert").html("<strong>" + msg + "</strong>");
  $(".alert").show();
}

function handle_fail(xhr) {
  var res = xhr.responseJSON;
  var msg =
    res && res.error ? res.error : "Something went wrong, please try again.";
  ini_reset_controls();
  show_error(msg);
}

// ---------- Results rendering ----------

function get_filtered_results() {
  if (minPriceFilter == null && maxPriceFilter == null) {
    return allResults;
  }
  return allResults.filter(function (item) {
    var p = parseFloat(item.numeric_price);
    if (isNaN(p)) {
      // keep items with no parseable price rather than hiding them outright
      return true;
    }
    if (minPriceFilter != null && p < minPriceFilter) {
      return false;
    }
    if (maxPriceFilter != null && p > maxPriceFilter) {
      return false;
    }
    return true;
  });
}

function compute_best_index(results) {
  var bestIdx = -1;
  var bestPrice = Infinity;
  for (var i = 0; i < results.length; i++) {
    var p = parseFloat(results[i].numeric_price);
    if (!isNaN(p) && p < bestPrice) {
      bestPrice = p;
      bestIdx = i;
    }
  }
  return bestIdx;
}

function render_results() {
  if (allResults.length > 0) {
    $("#priceFilter").show();
  }

  var results = get_filtered_results();
  var bestIdx = compute_best_index(results);

  if (shownCount === 0) {
    shownCount = Math.min(results.length, PAGE_SIZE);
  }

  if (results.length === 0) {
    $("#resultreact").empty();
    $("#load_next").hide();
    if (allResults.length > 0) {
      $("#resultreact").html(
        '<p class="no-results-note">No results in that price range.</p>'
      );
    }
    return;
  }

  var seenHtml = [];
  var bucket = [];
  for (var i = 0; i < Math.min(shownCount, results.length); i++) {
    var html = build_card_html(results[i], i === bestIdx);
    if (seenHtml.indexOf(html) !== -1) {
      continue;
    }
    seenHtml.push(html);
    bucket.push(html);
  }
  // The "load next" card has to be built into the row itself, not toggled after
  // the fact - it lives in a template outside #resultreact, whose own wrapper
  // stays display:none, so showing it in place would do nothing.
  var hasMore = results.length > shownCount;
  if (hasMore) {
    bucket.push($("#load_next_default").html());
  }
  var wrapper = $('<div class="row">' + bucket.join("") + "</div>");
  $("#resultreact").empty();
  $("#resultreact").html(wrapper);
  if (hasMore) {
    $("#load_next").show();
  }
}

function build_card_html(item, isBest) {
  var tpl = $("#resultreact_default").html();
  var el = document.createElement("div");
  el.innerHTML = tpl;
  var links = el.querySelectorAll("#p_link");
  links[0].href = item["shop_link"] || "";
  el.querySelector("#p_img_link").src = item["image_url"] || "";
  el.querySelector("#p_img_link").alt = item["title"] || "";
  links[1].href = item["shop_link"] || "";
  links[1].innerText = item["title"] || "";
  el.querySelector("#p_description").innerText = item["content_description"] || "";
  el.querySelector("#p_price").innerText = "Price: " + (item["price"] || "");
  el.querySelector("#p_shopname").innerText = "Shop: " + (item["shop_name"] || "");
  if (isBest) {
    var card = el.querySelector(".card");
    var badge = el.querySelector("#p_best");
    if (card) {
      card.classList.add("best-deal");
    }
    if (badge) {
      badge.style.display = "inline-block";
    }
  }
  return $(el).html();
}

function load_next() {
  var results = get_filtered_results();
  shownCount = Math.min(results.length, shownCount + PAGE_SIZE);
  render_results();
}

// ---------- Progress bar ----------

function restart_progress_bar() {
  if (progressTimer != null) {
    clearInterval(progressTimer);
    progressTimer = null;
  }
  var elem = document.getElementById("searchProgressBar");
  elem.style.width = "1%";
  elem.setAttribute("aria-valuenow", 1);
}

function load_search_progress_bar() {
  var elem = document.getElementById("searchProgressBar");
  var width = 1;
  progressTimer = setInterval(frame, 900);
  function frame() {
    if (!searching || width >= 95) {
      clearInterval(progressTimer);
      progressTimer = null;
    } else {
      width++;
      elem.style.width = width + "%";
      elem.setAttribute("aria-valuenow", width);
    }
  }
}
