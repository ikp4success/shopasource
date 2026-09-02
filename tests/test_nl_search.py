from unittest.mock import patch

from shops.shop_util.shop_setup_functions import get_shops
from webapp.nl_search import MIN_MATCH_ACCURACY, parse_nl_query


def _stub_parsed(**overrides):
    parsed = {
        "search_keyword": "wallet",
        "shops": [],
        "sort_high_to_low": False,
        "match_accuracy": 0,
    }
    parsed.update(overrides)
    return parsed


@patch("webapp.nl_search.extract_structured")
def test_parse_nl_query_enforces_min_match_accuracy(mock_extract):
    mock_extract.return_value = _stub_parsed(match_accuracy=0)
    result = parse_nl_query("cheap wallet")
    assert result["smatch"] == str(MIN_MATCH_ACCURACY)


@patch("webapp.nl_search.extract_structured")
def test_parse_nl_query_respects_higher_match_accuracy(mock_extract):
    mock_extract.return_value = _stub_parsed(match_accuracy=5)
    result = parse_nl_query("exact match wallet")
    assert result["smatch"] == "5"


@patch("webapp.nl_search.extract_structured")
def test_parse_nl_query_filters_unknown_shops(mock_extract):
    mock_extract.return_value = _stub_parsed(shops=["AMAZON", "NOTASHOP"])
    result = parse_nl_query("wallet from amazon")
    shops = result["shops"].split(",")
    assert "AMAZON" in shops
    assert "NOTASHOP" not in shops


@patch("webapp.nl_search.extract_structured")
def test_parse_nl_query_defaults_to_all_shops_when_none_named(mock_extract):
    mock_extract.return_value = _stub_parsed(shops=[])
    result = parse_nl_query("wallet")
    assert result["shops"] == ",".join(get_shops(active=True))


@patch("webapp.nl_search.extract_structured")
def test_parse_nl_query_keeps_category_narrowed_subset(mock_extract):
    # A category-relevant subset the LLM picked (not every active shop, and not
    # a single explicitly-named one either) should be used as-is, not expanded
    # back out to every shop.
    mock_extract.return_value = _stub_parsed(shops=["AMAZON", "NEWEGG", "MICROCENTER"])
    result = parse_nl_query("gaming laptop")
    assert result["shops"] == "AMAZON,NEWEGG,MICROCENTER"


@patch("webapp.nl_search.extract_structured")
def test_parse_nl_query_system_prompt_includes_shop_domains(mock_extract):
    # The LLM needs each shop's domain to judge what it plausibly sells.
    mock_extract.return_value = _stub_parsed()
    parse_nl_query("wallet")
    system_prompt = mock_extract.call_args.kwargs["system"]
    assert "AMAZON (" in system_prompt
    assert "NEWEGG (" in system_prompt
