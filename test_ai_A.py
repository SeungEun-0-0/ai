import pytest

from load_scores import load_scores


@pytest.fixture
def csv_file(tmp_path):
    return tmp_path / "scores.csv"


def test_valid_rows(csv_file):
    csv_file.write_text(
        'name,score\n 김하나 ,70\n"최,네번",0\n김하나,100\n', encoding="utf-8-sig"
    )
    assert load_scores(csv_file) == ([("김하나", 70), ("최,네번", 0), ("김하나", 100)], [])


@pytest.mark.parametrize("row,reason", [
    ("김하나", "열 개수가 2가 아님"),
    ("김하나,80,비고", "열 개수가 2가 아님"),
    ("  ,90", "이름이 비어 있음"),
    ("김하나, ", "점수가 비어 있음"),
    ("김하나,결석", "점수가 정수가 아님"),
    ("김하나,88.5", "점수가 정수가 아님"),
    ("김하나,-1", "점수가 0~100 밖"),
    ("김하나,101", "점수가 0~100 밖"),
])
def test_skipped_row(csv_file, row, reason):
    csv_file.write_text(f"name,score\n\n{row}\n윤보람, 64 \n", encoding="utf-8")
    assert load_scores(csv_file) == ([("윤보람", 64)], [(3, row, reason)])


@pytest.mark.parametrize("contents", ["", "name,score\n", "name,score\n\n"])
def test_no_scores(csv_file, contents):
    csv_file.write_text(contents, encoding="utf-8")
    assert load_scores(csv_file) == ([], [])


def test_missing_file(csv_file):
    with pytest.raises(FileNotFoundError):
        load_scores(csv_file)