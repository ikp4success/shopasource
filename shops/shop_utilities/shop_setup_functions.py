from shops.shop_utilities.shop_setup import ShopSetup
from shops.shop_utilities.extra_function import safe_grab

shop_configurations = ShopSetup().get_shop_configurations()


def find_shop_configuration(shop_key):
    for shop_setting in shop_configurations:
        for shop_name in shop_setting:
            if shop_name == shop_key:
                return safe_grab(shop_setting, [shop_key])

    return {}


def find_shop(shop_list):
    if shop_list is None:
        return False

    for shop in shop_list:
        if not find_shop_configuration(shop):
            return False
    return True


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
