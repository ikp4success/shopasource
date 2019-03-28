from shops.shop_connect.shoplinks import ShopLinks


SHOP_CACHE_MAX_EXPIRY_TIME = 30
SHOP_CACHE_LOOKUP_SET = True


class ShopSetup(ShopLinks):

    def get_shop_configurations(self):
        shop_configurations = [
            {
                "AMAZON": {
                    "active": True,
                    "name": "AMAZON",
                    "url": self._amazonurl
                }

            },
            {
                "TARGET": {
                    "active": True,
                    "name": "TARGET",
                    "url": self._targeturl
                }

            },
            {
                "WALMART": {
                    "active": True,
                    "name": "WALMART",
                    "url": self._walmarturl
                }

            },
            {
                "TJMAXX": {
                    "active": True,
                    "name": "TJMAXX",
                    "url": self._tjmaxxurl
                }

            },
            {
                "GOOGLE": {
                    "active": True,
                    "name": "GOOGLE",
                    "url": self._googleurl
                }

            },
            {
                "HM": {
                    "active": True,
                    "name": "HM",
                    "url": self._hmurl
                }

            },
            {
                "NEWEGG": {
                    "active": True,
                    "name": "NEWEGG",
                    "url": self._neweggurl
                }

            },
            {
                "MICROCENTER": {
                    "active": True,
                    "name": "MICROCENTER",
                    "url": self._microcenterurl
                }

            },
            {
                "FASHIONNOVA": {
                    "active": True,
                    "name": "FASHIONNOVA",
                    "url": self._fashionnovaurl
                }

            },
            {
                "SIXPM": {
                    "active": True,
                    "name": "SIXPM",
                    "url": self._6pmurl
                }

            },
            {
                "POSHMARK": {
                    "active": True,
                    "name": "POSHMARK",
                    "url": self._poshmarkurl
                }

            },
            {
                "MACYS": {
                    "active": True,
                    "name": "MACYS",
                    "url": self._macysurl
                }

            },
            {
                "ASOS": {
                    "active": True,
                    "name": "ASOS",
                    "url": self._asosurl
                }

            },
            {
                "JCPENNEY": {
                    "active": True,
                    "name": "JCPENNEY",
                    "url": self._jcpenneyurl
                }

            },
            {
                "KOHLS": {
                    "active": False,
                    "name": "KOHLS",
                    "url": self._kohlsurl
                }

            },
            {
                "FOOTLOCKER": {
                    "active": False,
                    "name": "FOOTLOCKER",
                    "url": self._footlockerurl
                }

            },
            {
                "BESTBUY": {
                    "active": False,
                    "name": "BESTBUY",
                    "url": self._bestbuyurl
                }

            },
            {
                "EBAY": {
                    "active": False,
                    "name": "EBAY",
                    "url": self._ebayurl
                }

            },
            {
                "GROUPON": {
                    "active": False,
                    "name": "GROUPON",
                    "url": self._grouponurl
                }

            },
            {
                "KMART": {
                    "active": True,
                    "name": "KMART",
                    "url": self._kmarturl
                }

            },
            {
                "BIGLOTS": {
                    "active": True,
                    "name": "BIGLOTS",
                    "url": self._biglotsurl
                }

            },
            {
                "BURLINGTON": {
                    "active": True,
                    "name": "BURLINGTON",
                    "url": self._burlingtonurl
                }

            },
            {
                "MVMTWATCHES": {
                    "active": True,
                    "name": "MVMTWATCHES",
                    "url": self._mvmtwatchesurl
                }

            },
            {
                "BOOHOO": {
                    "active": True,
                    "name": "BOOHOO",
                    "url": self._boohoourl
                }

            },
            {
                "CUSHINE": {
                    "active": True,
                    "name": "CUSHINE",
                    "url": self._cushineurl
                }

            },
            {
                "FOREVER21": {
                    "active": True,
                    "name": "FOREVER21",
                    "url": self._forever21url
                }
            },
            {
                "STYLERUNNER": {
                    "active": True,
                    "name": "STYLERUNNER",
                    "url": self._stylerunnerurl
                }
            },
            {
                "SPIRITUALGANGSTER": {
                    "active": True,
                    "name": "SPIRITUALGANGSTER",
                    "url": self._spiritualgangsterurl
                }
            },
            {
                "LEVI": {
                    "active": True,
                    "name": "LEVI",
                    "url": self._leviurl
                }
            },
            {
                "ZARA": {
                    "active": True,
                    "name": "ZARA",
                    "url": self._zaraurl
                }
            },
            {
                "NORDSTROM": {
                    "active": True,
                    "name": "NORDSTROM",
                    "url": self._nordstormurl
                }
            },
            {
                "NORDSTROMRACK": {
                    "active": True,
                    "name": "NORDSTROMRACK",
                    "url": self._nordstormrackurl
                }
            },
            {
                "HAUTELOOK": {
                    "active": True,
                    "name": "HAUTELOOK",
                    "url": self._hautelookurl
                }
            },
            {
                "SAKSFIFTHAVENUE": {
                    "active": True,
                    "name": "SAKSFIFTHAVENUE",
                    "url": self._saksfifthavenueurl
                }
            },
            {
                "EXPRESS": {
                    "active": True,
                    "name": "EXPRESS",
                    "url": self._expressurl
                }
            },
            {
                "CHARLOTTERUSSE": {
                    "active": True,
                    "name": "CHARLOTTERUSSE",
                    "url": self._charlotterusseurl
                }
            },
            {
                "ALDO": {
                    "active": False,
                    "name": "ALDO",
                    "url": self._aldourl
                }
            },
            {
                "BASSO": {
                    "active": True,
                    "name": "BASSO",
                    "url": self._bassourl
                }
            },
            {
                "SHOPQUEEN": {
                    "active": True,
                    "name": "SHOPQUEEN",
                    "url": self._shopqueenurl
                }
            },
            {
                "NIKE": {
                    "active": True,
                    "name": "NIKE",
                    "url": self._nikeurl
                }
            },
            {
                "ADIDAS": {
                    "active": False,
                    "name": "ADIDAS",
                    "url": self._adidasurl
                }
            },
            {
                "DICKSSPORTINGGOODS": {
                    "active": True,
                    "name": "DICKSSPORTINGGOODS",
                    "url": self._dicksportinggoodsurl
                }
            },
            {
                "BIINK": {
                    "active": True,
                    "name": "BIINK",
                    "url": self._biinkurl
                }
            },
            {
                "CHAMPSSPORTS": {
                    "active": True,
                    "name": "CHAMPSSPORTS",
                    "url": self._champsporturl
                }
            }
        ]

        return shop_configurations
