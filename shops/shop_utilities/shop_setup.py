from enum import Enum
from shops.shop_utilities.extra_function import safe_grab


class TestShopNames(Enum):
    AMAZON = "AMAZON",
    TARGET = "TARGET",
    WALMART = "WALMART",
    TJMAXX = "TJMAXX",
    GOOGLE = "GOOGLE",
    NEWEGG = "NEWEGG",
    HM = "HM",
    MICROCENTER = "MICROCENTER",
    FASHIONNOVA = "FASHIONNOVA",
    SIXPM = "SIXPM",
    POSTMARK = "POSTMARK",
    MACYS = "MACYS",
    ASOS = "ASOS",
    JCPENNEY = "JCPENNEY",
    KOHLS = "KOHLS"
    FOOTLOCKER = "FOOTLOCKER",
    BESTBUY = "BESTBUY",
    EBAY = "EBAY",
    KMART = "KMART",
    BIGLOTS = "BIGLOTS",
    BURLINGTON = "BURLINGTON",
    MVMTWATCHES = "MVMTWATCHES",
    BOOHOO = "BOOHOO",
    FOREVER21 = "FOREVER21"


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
        "POSTMARK": {
            "active": True,
            "name": "POSTMARK"
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
    }
]


def find_shop_configuration(shop_key):
    for shop_setting in shop_configurations:
        for shop_name in shop_setting:
            if shop_name == shop_key:
                return safe_grab(shop_setting, [shop_key])

    return {}


def get_shops(active=None):
    shop_names_list = []
    for shop_setting in shop_configurations:
        for shop_name in shop_setting:
            if active is not None:
                if shop_setting[shop_name]["active"] == active:
                    shop_names_list.append(shop_name)
            else:
                shop_names_list.append(shop_name)
    return shop_names_list


def is_shop_active(shop_name):
    return shop_name in get_shops(active=True)
