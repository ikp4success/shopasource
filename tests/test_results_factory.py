import threading
import time

import tasks.results_factory as results_factory_module
from tasks.results_factory import ResultsFactory


def _factory(search_keyword, match_acc, shop_names_list="AMAZON", **kwargs):
    return ResultsFactory(
        search_keyword=search_keyword,
        shop_names_list=shop_names_list,
        match_acc=match_acc,
        is_cache=True,
        is_async=True,
        **kwargs,
    )


def test_match_sk_zero_accuracy_matches_anything():
    rf = _factory("wallet for men", match_acc=0)
    assert rf.match_sk("Completely unrelated dress") is True


def test_match_sk_rejects_substring_false_positive():
    # "for" must not match merely because it's a substring of "force".
    rf = _factory("wallet for men", match_acc=1)
    assert rf.match_sk("Nike Icon Air Force 1") is False


def test_match_sk_ignores_stopword_only_matches():
    # Only the stopword "for" appears here - that alone shouldn't count as a match.
    rf = _factory("wallet for men", match_acc=1)
    assert rf.match_sk("Pnina Tornai for Naturalizer - Liebe") is False


def test_match_sk_matches_real_item():
    rf = _factory("wallet for men", match_acc=1)
    assert (
        rf.match_sk("Tipmile Wallet for Men Slim RFID Blocking Leather Wallet") is True
    )


def test_start_search_runs_shops_concurrently(monkeypatch):
    concurrency = {"current": 0, "max": 0}
    lock = threading.Lock()

    def fake_launch(shop_name, search_keyword, is_async, job_id):
        with lock:
            concurrency["current"] += 1
            concurrency["max"] = max(concurrency["max"], concurrency["current"])
        time.sleep(0.05)
        with lock:
            concurrency["current"] -= 1

    monkeypatch.setattr(results_factory_module, "launch_spiders", fake_launch)
    monkeypatch.setattr(
        results_factory_module, "_is_browser_fetch_shop", lambda name: False
    )

    rf = _factory(
        "test",
        match_acc=1,
        shop_names_list="AMAZON,TARGET,WALMART,NIKE,MACYS,ASOS",
    )
    rf.start_search()

    assert concurrency["max"] > 1


def test_start_search_caps_browser_fetch_concurrency(monkeypatch):
    concurrency = {"current": 0, "max": 0}
    lock = threading.Lock()

    def fake_launch(shop_name, search_keyword, is_async, job_id):
        with lock:
            concurrency["current"] += 1
            concurrency["max"] = max(concurrency["max"], concurrency["current"])
        time.sleep(0.05)
        with lock:
            concurrency["current"] -= 1

    monkeypatch.setattr(results_factory_module, "launch_spiders", fake_launch)
    monkeypatch.setattr(
        results_factory_module, "_is_browser_fetch_shop", lambda name: True
    )
    monkeypatch.setattr(
        results_factory_module, "_browser_fetch_semaphore", threading.Semaphore(2)
    )

    rf = _factory(
        "test",
        match_acc=1,
        shop_names_list="AMAZON,TARGET,WALMART,NIKE,MACYS,ASOS",
    )
    rf.start_search()

    assert concurrency["max"] <= 2


def test_start_search_continues_after_one_shop_fails(monkeypatch):
    launched = []
    errored_shops = []

    def fake_launch(shop_name, search_keyword, is_async, job_id):
        if shop_name == "TARGET":
            raise RuntimeError("boom")
        launched.append(shop_name)

    def fake_save_job(shop_name, job_id, status="done"):
        if status == "error":
            errored_shops.append(shop_name)

    monkeypatch.setattr(results_factory_module, "launch_spiders", fake_launch)
    monkeypatch.setattr(
        results_factory_module, "_is_browser_fetch_shop", lambda name: False
    )
    monkeypatch.setattr(results_factory_module, "save_job", fake_save_job)

    rf = _factory(
        "test",
        match_acc=1,
        shop_names_list="AMAZON,TARGET,WALMART",
        job_id="fake-job-id",
    )
    rf.start_search()

    assert set(launched) == {"AMAZON", "WALMART"}
    assert errored_shops == ["TARGET"]
