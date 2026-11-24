import csv

import pytest

from load_scores import load_scores


@pytest.fixture
def csv_file(tmp_path):
    return tmp_path / "scores.csv"


def test_valid_scores_and_original_file(csv_file):
    csv_file.write_text('name,score\n"최,네번", 100 \n김하나,0\n', encoding="utf-8-sig")
    original = csv_file.read_bytes()
    assert load_scores(csv_file) == ([("최,네번", 100), ("김하나", 0)], [])
    assert csv_file.read_bytes() == original


def test_header_only(csv_file):
    csv_file.write_text("name,score\n", encoding="utf-8")
    assert load_scores(csv_file) == ([], [])


def test_missing_file(csv_file):
    with pytest.raises(FileNotFoundError):
        load_scores(csv_file)


def test_wrong_header(csv_file):
    csv_file.write_text("score,name\n70,김하나\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_scores(csv_file)


def test_unclosed_quote(csv_file):
    csv_file.write_text('name,score\n"김하나,77\n', encoding="utf-8")
    with pytest.raises(csv.Error):
        load_scores(csv_file)


@pytest.mark.parametrize("row", [
    "김하나", "김하나,80,비고", ",90", "김하나,", "김하나,결석",
    "김하나,88.5", "김하나,-1", "김하나,101", "김하나,7_2",
])
def test_invalid_score_is_reported(csv_file, row):
    csv_file.write_text(f"name,score\n{row}\n윤보람,64\n", encoding="utf-8")
    kept, skipped = load_scores(csv_file)
    assert kept == [("윤보람", 64)]
    assert len(skipped) == 1
    line_no, reason = skipped[0]
    assert line_no == 2
    assert isinstance(reason, str) and reason.strip()


def test_keep_first_valid_score_for_each_name(csv_file):
    csv_file.write_text("name,score\n김하나,105\n김하나,88\n김하나,91\n", encoding="utf-8")
    kept, skipped = load_scores(csv_file)
    assert kept == [("김하나", 88)]
    assert [line_no for line_no, reason in skipped] == [2, 4]