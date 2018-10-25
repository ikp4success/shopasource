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
