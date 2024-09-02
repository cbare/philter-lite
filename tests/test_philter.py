import os
from typing import Any, Dict

import pytest

import philter_lite
from philter_lite import detect_phi, filters, load_filters


# create instance of callable filter builder with default config
filter_from_dict = filters.FilterBuilder()


def test_filter_from_dict():
    filter_dict: Dict[str, Any] = {
        "title": "test_city",
        "type": "regex",
        "keyword": "addresses.city",
        "exclude": "test_ex",
        "notes": "test_notes",
        "phi_type": "SOMETHING",
    }

    filter = filter_from_dict(filter_dict)

    assert filter.type == "regex"
    assert filter.title == "test_city"
    assert filter.data is not None
    assert filter.exclude == "test_ex"
    assert filter.phi_type == "SOMETHING"
    assert isinstance(filter, filters.RegexFilter)

    filter_dict = {
        "title": "Find Names 1",
        "type": "regex_context",
        "exclude": True,
        "context": "right",
        "context_filter": "Firstnames Blacklist",
        "keyword": "regex_context.names_regex_context1",
        "phi_type": "Something",
    }

    filter = filter_from_dict(filter_dict)

    assert filter.type == "regex_context"
    assert filter.title == "Find Names 1"
    assert filter.data is not None
    assert filter.exclude is True
    assert filter.context == "right"
    assert filter.context_filter == "Firstnames Blacklist"
    assert isinstance(filter, filters.RegexContextFilter)

    filter_dict = {
        "title": "Whitelist 1",
        "type": "set",
        "exclude": False,
        "keyword": "nonames",
        "pos": [],
        "phi_type": "Something",
    }

    filter = filter_from_dict(filter_dict)

    assert filter.type == "set"
    assert filter.title == "Whitelist 1"
    assert filter.data is not None
    assert filter.exclude is False
    assert filter.pos == set()
    assert isinstance(filter, filters.SetFilter)

    filter_dict = {
        "title": "POS MATCHER",
        "type": "pos_matcher",
        "exclude": False,
        "pos": ["CD"],
        "phi_type": "OTHER",
    }

    filter = filter_from_dict(filter_dict)

    assert filter.type == "pos_matcher"
    assert filter.title == "POS MATCHER"
    assert filter.exclude is False
    assert filter.pos == ["CD"]
    assert isinstance(filter, filters.PosFilter)


def test_filter_from_dict_missing_phi_type():
    filter_dict = {
        "title": "test_city",
        "type": "regex",
        "keyword": "addresses.city",
        "exclude": "test_ex",
        "notes": "test_notes",
    }

    filter = filter_from_dict(filter_dict)
    assert filter.phi_type == "OTHER"


def test_filter_from_dict_missing_keyword():
    filter_dict = {
        "type": "regex",
        "keyword": "non_existent_keyword_asdf",
    }

    with pytest.raises(Exception):  # noqa: B017
        filter_from_dict(filter_dict)


def test_default_config():
    filters = load_filters(os.path.join(os.path.dirname(philter_lite.__file__), "configs/philter_delta.toml"))
    assert len(filters) > 0


def test_non_existent_config():
    with pytest.raises(FileNotFoundError):
        load_filters("/doesnt/exist/bonko.toml")


def test_detect_phi():
    patterns = [
        filter_from_dict(
            {
                "title": "patient SSN",
                "type": "regex",
                "exclude": True,
                "keyword": "mrn_id.ssn",
                "notes": "",
                "phi_type": "MRN",
            }
        ),
        filter_from_dict(
            {
                "title": "dd_mm_yyyy",
                "type": "regex",
                "exclude": True,
                "keyword": "dates.dd_mm_yyyy",
                "notes": "This should remove anything with pattern dd_mm_yyyy",
                "phi_type": "DATE",
            }
        ),
    ]
    include_map, exclude_map, data_tracker = detect_phi(
        "The patients SSN is 123-45-6789. They were born on 01/01/1984.",
        patterns,
        ["MRN", "DATE"],
    )

    assert len(data_tracker.phi) == 2


def test_detect_phi_regex_interpolation():
    # At runtime, we compute the seasons value in the regex, by interpolating a variable name.
    patterns = [
        filter_from_dict(
            {
                "title": "season of yyyy",
                "type": "regex",
                "exclude": True,
                "notes": "",
                "phi_type": "DATE",
                "keyword": "dates.season_of_yyyy",
            }
        ),
    ]
    include_map, exclude_map, data_tracker = detect_phi(
        "They injured themselves in Fall of 2020.", patterns, ["MRN", "DATE"]
    )

    assert len(data_tracker.phi) == 1
    assert data_tracker.phi[0].start == 27
    assert data_tracker.phi[0].stop == 39
    assert data_tracker.phi[0].word == "Fall of 2020"
    assert data_tracker.phi[0].phi_type == "DATE"
