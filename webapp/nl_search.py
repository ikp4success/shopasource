from shops.shop_util.shop_setup_functions import get_shops
from support import get_logger
from webapp.llm_providers import extract_structured

logger = get_logger(__name__)

# ResultsFactory.match_sk() treats match_acc == 0 as "no filtering at all" - every
# scraped item from every shop passes, even ones with zero words in common with the
# search. Since a search now always spans every active shop rather than a
# user-picked subset, that means shops that don't carry the item at all (e.g.
# Fashion Nova for "wallet for men") still contribute their unrelated inventory,
# and the cheapest of those can end up junk-cheap and win "best price". A floor of
# 1 is enough to require at least one keyword actually appear in the item, without
# being so strict it drops genuine partial matches.
MIN_MATCH_ACCURACY = 1

_NL_QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "search_keyword": {
            "type": "string",
            "description": "The core product being searched for, stripped of price/sort/shop qualifiers.",
        },
        "shops": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Shop names explicitly mentioned by the user. Empty if none were named.",
        },
        "sort_high_to_low": {
            "type": "boolean",
            "description": (
                "True to sort most expensive first, false for cheapest/best-match "
                "first. Default false (best match first) when the user states no "
                "explicit price-sort preference - only set true if they actually "
                "asked for priciest/most expensive/premium options."
            ),
        },
        "match_accuracy": {
            "type": "integer",
            "description": "How strictly the keyword must match, 0 (loose) to 10 (exact). Default 0.",
        },
    },
    "required": ["search_keyword", "shops", "sort_high_to_low", "match_accuracy"],
    "additionalProperties": False,
}


def parse_nl_query(query_text, is_async=True, provider=None):
    """Turn a free-text shopping request into the params validate_params() expects.

    Runs against `provider` if given, else whichever LLM provider is configured -
    see webapp.llm_providers.
    """
    allowed_shops = get_shops(active=True)

    system = (
        "You convert a shopper's natural-language request into search parameters "
        "for a price-comparison tool. Valid shop names are: "
        f"{', '.join(allowed_shops)}. Only put names from that exact list into "
        "'shops' - drop any store the user names that isn't on the list. Leave "
        "'shops' empty if the user didn't name specific stores."
    )

    parsed = extract_structured(
        system=system,
        user_message=query_text,
        schema=_NL_QUERY_SCHEMA,
        provider=provider,
    )

    shops = [s for s in parsed.get("shops", []) if s in allowed_shops]
    if not shops:
        shops = allowed_shops

    high_to_low = parsed.get("sort_high_to_low", False)
    match_accuracy = max(int(parsed.get("match_accuracy") or 0), MIN_MATCH_ACCURACY)

    return {
        "sk": parsed["search_keyword"],
        "shops": ",".join(shops),
        "smatch": str(match_accuracy),
        "shl": "true" if high_to_low else "false",
        "slh": "false" if high_to_low else "true",
        "async": "1" if is_async else "0",
    }
