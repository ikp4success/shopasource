import os


def printHtmlToFile(html, page_name=None):
        if page_name is None:
            page_name = "spider_test"
        filename = "scraped_sites/spidertest_" + page_name + ".html"
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
            file = open(filename, "w")
            file.write(html)
            file.close()
        else:
            file = open(filename, "w")
            file.write(html)
            file.close()


def printLogTrace(error, errorTag=None):
        if errorTag is None:
            errorTag = "ERROLOG"
        printHtmlToFile(error, errorTag)


def printStr(keyword, trace_str):
    print("DEBUG PRINT STR TRACE: %s : %s" % (keyword, trace_str))


def generateUUID():
    import uuid
    print("**UUID GENERATION**\n")
    print("32 - {}\n".format(uuid.uuid4()))
    print("64 - {}{}\n".format(str(uuid.uuid4()), str(uuid.uuid4())))
    print("32Hex - {}\n".format(uuid.uuid4().hex))
    print("64Hex - {}{}\n".format(uuid.uuid4().hex, uuid.uuid4().hex))


result_Sample = [
    {
        "image_url": "https://images-na.ssl-images-amazon.com/images/I/61SzASCwGjL._UL1020_.jpg",
        "shop_name": "AMAZON",
        "shop_link": "https://www.amazon.com/toraway-Stylish-Business-Leather-Windows/dp/B01A82JTJW?keywords=wallet&qid=1540670552&sr=8-1&ref=sr_1_1",
        "price": "$4.08",
        "numeric_price": "4.08",
        "title": "Wallet,toraway Luxury Men Stylish Bifold Business ...",
        "searched_keyword": "wallet",
        "content_description": "PU Leather100% brand new and high qualityDesigned to hold cash, cards and other little thingsSlim Bi-Fold flip wallet, easy to carry aroundAs a perfect gift for yourself or your friends.Inside Detail: Credit card inserts, window ID",
        "date_searched": "2018-10-27 16:02:36.170484"
    },
    {
        "image_url": "https://images-na.ssl-images-amazon.com/images/I/61SzASCwGjL._UL1020_.jpg",
        "shop_name": "BESTBUY",
        "shop_link": "https://www.amazon.com/toraway-Stylish-Business-Leather-Windows/dp/B01A82JTJW?keywords=wallet&qid=1540670552&sr=8-1&ref=sr_1_1",
        "price": "$10.08",
        "numeric_price": "10.08",
        "title": "Wallet,toraway Luxury Men Stylish Bifold Business ...",
        "searched_keyword": "wallet",
        "content_description": "PU Leather100% brand new and high qualityDesigned to hold cash, cards and other little thingsSlim Bi-Fold flip wallet, easy to carry aroundAs a perfect gift for yourself or your friends.Inside Detail: Credit card inserts, window ID",
        "date_searched": "2018-10-26 16:02:36.170484"
    }
]
