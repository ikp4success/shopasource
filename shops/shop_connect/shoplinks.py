import uuid


class ShopLinks(object):
    _amazonurl = "https://www.amazon.com/s/ref=sr_st_relevanceblender?url=search-alias%3Daps&field-keywords={keyword}"
    _bestbuyurl = "https://www.bestbuy.com/site/searchpage.jsp?st={keyword}&_dyncharset=UTF-8&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys"
    _ebayurl = "https://www.ebay.com/sch/i.html?_from=R40&_sacat=0&_nkw={keyword}&rt=nc&LH_PrefLoc=1&_ipg=25"
    _walmarturl = (
        "https://www.walmart.com/search/?page=1&query={keyword}&sort=price_low"
    )
    _tjmaxxurl = "https://tjmaxx.tjx.com/store/shop?Nr=AND%28OR%28product.catalogId%3Atjmaxx%29%2Cproduct.siteId%3Atjmaxx%2CisEarlyAccess%3Afalse%29&Ns=product.minListPrice%7C0%7C%7Cproduct.inventory%7C1&Ntt={keyword}&_dyncharset=utf-8&initSubmit=true&qfh_sch=Search&tag=srt"
    _googleurl = "https://www.google.com/search?q={keyword}&sa=X&tbas=0&biw=1920&bih=966&tbm=shop&tbs=p_ord:p"
    _targeturl = (
        "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1?key=ff457966e64d5e877fdbad070f276d18ecec4a01&count=20&offset=0&keyword={keyword}&sort_by=relevance&default_purchasability_filter=true&include_sponsored_search=false&platform=desktop&channel=WEB&page={keyword}&isBot=false&pricing_store_id=3229&visitor_id="
        + str(uuid.uuid1()).replace("-", "").upper()
    )
    _neweggurl = "https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&N=-1&IsNodeId=1&Description={keyword}&bop=And&Order=BESTSELLING&PageSize=1"
    _hmurl = "https://www2.hm.com/en_us/search-results.html?q={keyword}&department=1&sort=ascPrice&image-size=small&image=stillLife&offset=0&page-size=1"
    _microcenterurl = "https://www.microcenter.com/search/search_results.aspx?N=0&NTX=&NR=&filterProperty=&NTT={keyword}&NTK=all&page=1&sortby=match&SortNow=Go"
    _grouponurl = "https://www.groupon.com/browse/query={keyword}?sort=relevance"
    _fashionnovaurl = "https://ultimate-fnova-dot-acp-magento.appspot.com/full_text_search?page_num=1&q={keyword}&UUID={uuid}"
    _6pmurl = "https://www.6pm.com/{keyword}"
    _poshmarkurl = (
        "https://poshmark.com/search?query={keyword}&sort_by=added_desc&department=All"
    )
    _macysurl = "https://www.macys.com/shop/search?keyword={keyword}"
    _asosurl = "https://www.asos.com/us/search/?q={keyword}"
    _jcpenneyurl = "https://search-api.jcpenney.com/v1/search-service/s/{keyword}?productGridView=medium&Ntt={keyword}&responseType=organic"
    _kohlsurl = (
        "https://www.kohls.com/search.jsp?submit-search=web-regular&search={keyword}"
    )
    _footlockerurl = "https://www.footlocker.com/search?query={keyword}"
    _kmarturl = (
        "https://www.kmart.com/service/search/v2/productSearch?keyword={keyword}"
    )
    _biglotsurl = "https://www.biglots.com/search/?Ntt={keyword}"
    _burlingtonurl = "https://www.burlington.com/b/catalog/searchresults.aspx?filter=&search={keyword}"
    _mvmtwatchesurl = "https://www.mvmtwatches.com/search?type=product&q={keyword}"
    _boohoourl = "https://us.boohoo.com/search?q={keyword}"
    _cushineurl = "https://www.cushnie.com/solr/?q_search={keyword}"
    _forever21url = "https://brm-core-0.brsrvr.com/api/v1/core/?account_id=5079&auth_key=d1qiei07nwrrdicq&domain_key=forever21_us_com&request_id=7115648782864&_br_uid_2=uid%3D3032493086709%3Av%3D11.8%3Ats%3D1547329267979%3Ahc%3D1&url=https%3A%2F%2Fwww.forever21.com%2Fus%2Fshop%2FSearch%2F%23brm-search%3Frequest_type%3Dsearch%26search_type%3Dkeyword%26q%3D{keyword}%26l%3D{keyword}&ref_url=https%3A%2F%2Fwww.forever21.com%2Fus%2Fshop%2Fsearch%2F&request_type=search&rows=120&start=0&fl=pid%2Ctitle%2Cbrand%2Cprice%2Csale_price%2Cpromotions%2Cthumb_image%2Csku_thumb_images%2Csku_swatch_images%2Csku_color_group%2Curl%2Cflags&facet.range=sale_price%3A%5B30%20TO%20*%5D&facet.range=sale_price%3A%5B20%20TO%2030%5D&facet.range=sale_price%3A%5B10%20TO%2020%5D&facet.range=sale_price%3A%5B0%20TO%2010%5D&l={keyword}&q={keyword}&search_type=keyword"
    _stylerunnerurl = "https://www.stylerunner.com/search?keywords={keyword}&cur=USD&"
    _spiritualgangsterurl = "https://spiritualgangster.com/search?q={keyword}"
    _leviurl = "https://www.levi.com/US/en_US/search/{keyword}"
    _zaraurl = "https://api.empathybroker.com/search/v1/query/zara/search?o=json&m=24&q={keyword}&scope=default&t=*&lang=en_US&store=11719&start=0&rows=24&origin=default"
    _nordstormurl = (
        "https://shop.nordstrom.com/sr?origin=keywordsearch&keyword={keyword}"
    )
    _nordstormrackurl = "https://www.nordstromrack.com/api/search2/catalog/search?includeFlash=false&includePersistent=true&query={keyword}&sort=relevancy&limit=99"
    _hautelookurl = "https://www.hautelook.com/api/search2/catalog/search?includeFlash=true&includePersistent=false&limit=99&page=1&query={keyword}&sort=relevancy"
    _saksfifthavenueurl = "https://www.saksfifthavenue.com/search/EndecaSearch.jsp?bmArch=bmForm&bmForm=endeca_search_form_one&bmArch=bmIsForm&bmIsForm=true&bmHidden=submit-search&submit-search=&bmArch=bmSingle&bmSingle=N_Dim&bmHidden=N_Dim&N_Dim=0&bmArch=bmHidden&bmHidden=Ntk&bmHidden=Ntk&Ntk=Entire+Site&bmArch=bmHidden&bmHidden=Ntx&bmHidden=Ntx&Ntx=mode%2Bmatchpartialmax&bmHidden=PA&PA=TRUE&SearchString=+{keyword}"
    _expressurl = "https://search.unbxdapi.com/{api_key}/express_com-u1456154309768/search?&q={keyword}&rows=70&start=0&format=json&fields=unbxd_color_mapping,title,uniqueId,productUrl,displayPrice,selling_price,displaySalePrice,color,promoMessage,imageUrl,colorImageMap,imageMap,colorSwatch&facet.multiselect=true&indent=off&device-type=Desktop&unbxd-url=https%3A%2F%2Fwww.express.com%2Fexp%2Fsearch%3Fq%3Dwallet&unbxd-referrer=https%3A%2F%2Fwww.express.com%2F&user-type=new&api-key={api_key}"
    _charlotterusseurl = (
        "https://www.charlotterusse.com/search/?q={keyword}&lang=default"
    )
    _aldourl = "https://www.aldoshoes.com/us/en_US/search?q={keyword}"
    _bassourl = "https://basso.co/search?q={keyword}"
    _shopqueenurl = "https://www.shopqueen.com/search?q={keyword}*&type=product"
    _nikeurl = "https://store.nike.com/us/en_us/pw/n/1j7?sl={keyword}&vst={keyword}"
    _adidasurl = "https://www.adidas.com/api/search/query?sitePath=us&query={keyword}"
    _dicksportinggoodsurl = "https://www.dickssportinggoods.com/search/SearchDisplay?categoryId=&storeId=15108&catalogId=12301&langId=-1&sType=SimpleSearch&resultCatEntryType=2&showResultsPage=true&fromPage=Search&searchSource=Q&pageView=&beginIndex=0&DSGsearchType=Keyword&pageSize=48&nowcs=&searchTerm={keyword}&advsearch=true"
    _biinkurl = "https://biink.com/search?type=product&q={keyword}&submit=Search"
    _champsporturl = "https://www.champssports.com/api/products/search?products=&query={keyword}&pageSize=60&timestamp=6"
