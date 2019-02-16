from shops.shop_connect.shoplinks import ShopLinks


class ShopSetup(ShopLinks):

    def get_shop_configurations(self):
        shop_configurations = [
            {
                "AMAZON": {
                    "active": True,
                    "name": "AMAZON"
                }

            },
            {
                "TARGET": {
                    "active": True,
                    "name": "TARGET"
                }

            },
            {
                "WALMART": {
                    "active": True,
                    "name": "WALMART"
                }

            },
            {
                "TJMAXX": {
                    "active": True,
                    "name": "TJMAXX"
                }

            },
            {
                "GOOGLE": {
                    "active": True,
                    "name": "GOOGLE"
                }

            },
            {
                "HM": {
                    "active": True,
                    "name": "HM"
                }

            },
            {
                "NEWEGG": {
                    "active": True,
                    "name": "NEWEGG"
                }

            },
            {
                "MICROCENTER": {
                    "active": True,
                    "name": "MICROCENTER"
                }

            },
            {
                "FASHIONNOVA": {
                    "active": True,
                    "name": "FASHIONNOVA"
                }

            },
            {
                "SIXPM": {
                    "active": True,
                    "name": "SIXPM"
                }

            },
            {
                "POSHMARK": {
                    "active": True,
                    "name": "POSHMARK"
                }

            },
            {
                "MACYS": {
                    "active": True,
                    "name": "MACYS"
                }

            },
            {
                "ASOS": {
                    "active": True,
                    "name": "ASOS"
                }

            },
            {
                "JCPENNEY": {
                    "active": True,
                    "name": "JCPENNEY"
                }

            },
            {
                "KOHLS": {
                    "active": False,
                    "name": "KOHLS"
                }

            },
            {
                "FOOTLOCKER": {
                    "active": False,
                    "name": "FOOTLOCKER"
                }

            },
            {
                "BESTBUY": {
                    "active": False,
                    "name": "BESTBUY"
                }

            },
            {
                "EBAY": {
                    "active": False,
                    "name": "EBAY"
                }

            },
            {
                "GROUPON": {
                    "active": False,
                    "name": "GROUPON"
                }

            },
            {
                "KMART": {
                    "active": True,
                    "name": "KMART"
                }

            },
            {
                "BIGLOTS": {
                    "active": True,
                    "name": "BIGLOTS"
                }

            },
            {
                "BURLINGTON": {
                    "active": True,
                    "name": "BURLINGTON"
                }

            },
            {
                "MVMTWATCHES": {
                    "active": True,
                    "name": "MVMTWATCHES"
                }

            },
            {
                "BOOHOO": {
                    "active": True,
                    "name": "BOOHOO"
                }

            },
            {
                "CUSHINE": {
                    "active": True,
                    "name": "CUSHINE"
                }

            },
            {
                "FOREVER21": {
                    "active": True,
                    "name": "FOREVER21"
                }
            },
            {
                "STYLERUNNER": {
                    "active": True,
                    "name": "STYLERUNNER"
                }
            },
            {
                "SPIRITUALGANGSTER": {
                    "active": True,
                    "name": "SPIRITUALGANGSTER"
                }
            },
            {
                "LEVI": {
                    "active": True,
                    "name": "LEVI"
                }
            },
            {
                "ZARA": {
                    "active": True,
                    "name": "ZARA"
                }
            },
            {
                "NORDSTROM": {
                    "active": True,
                    "name": "NORDSTROM"
                }
            },
            {
                "NORDSTROMRACK": {
                    "active": True,
                    "name": "NORDSTROMRACK"
                }
            },
            {
                "HAUTELOOK": {
                    "active": True,
                    "name": "HAUTELOOK"
                }
            },
            {
                "SAKSFIFTHAVENUE": {
                    "active": True,
                    "name": "SAKSFIFTHAVENUE"
                }
            },
            {
                "EXPRESS": {
                    "active": True,
                    "name": "EXPRESS"
                }
            },
            {
                "CHARLOTTERUSSE": {
                    "active": True,
                    "name": "CHARLOTTERUSSE"
                }
            },
            {
                "ALDO": {
                    "active": False,
                    "name": "ALDO"
                }
            },
            {
                "BASSO": {
                    "active": True,
                    "name": "BASSO"
                }
            },
            {
                "SHOPQUEEN": {
                    "active": True,
                    "name": "SHOPQUEEN"
                }
            },
            {
                "NIKE": {
                    "active": True,
                    "name": "NIKE"
                }
            },
            {
                "ADIDAS": {
                    "active": False,
                    "name": "ADIDAS"
                }
            },
            {
                "DICKSSPORTINGGOODS": {
                    "active": True,
                    "name": "DICKSSPORTINGGOODS"
                }
            },
            {
                "BINK": {
                    "active": True,
                    "name": "BINK"
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
