from pathlib import Path

from supplychain360.ingest import discover_files
from supplychain360.inspection import inspect_csv, sha256_file, write_json


def test_inspect_empty_file(tmp_path: Path):
    f = tmp_path / "empty.csv"
    f.write_text("", encoding="utf-8")
    result = inspect_csv(f)
    assert result["empty"] is True
    assert result["columns"] == []


def test_inspect_header_only(tmp_path: Path):
    f = tmp_path / "h.csv"
    f.write_text("a,b,c\n", encoding="utf-8")
    result = inspect_csv(f)
    assert result["sample_rows"] == 0
    assert result["column_count"] == 3


def test_inspect_counts_malformed_rows(tmp_path: Path):
    f = tmp_path / "m.csv"
    f.write_text("a,b\n1,2\n3\n4,5,6\n", encoding="utf-8")
    assert inspect_csv(f)["malformed_sample_rows"] == 2


def test_inspect_strips_utf8_bom(tmp_path: Path):
    f = tmp_path / "bom.csv"
    f.write_bytes(b"\xef\xbb\xbfid,name\n1,x\n")
    assert inspect_csv(f)["columns"] == ["id", "name"]


def test_inspect_does_not_crash_on_latin1(tmp_path: Path):
    f = tmp_path / "latin.csv"
    f.write_bytes("id,name\n1,Caf\u00e9\n".encode("latin-1"))
    assert inspect_csv(f)["sample_rows"] == 1


def test_inspect_is_bounded_by_sample_size(tmp_path: Path):
    f = tmp_path / "big.csv"
    f.write_text("x\n" + "1\n" * 50, encoding="utf-8")
    assert inspect_csv(f, sample_rows=10)["sample_rows"] == 10


def test_sha256_known_value(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_bytes(b"hello")
    assert sha256_file(f) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_write_json_creates_parent_dirs(tmp_path: Path):
    target = tmp_path / "a" / "b" / "out.json"
    write_json(target, {"k": 1})
    assert target.exists()


def test_discover_files_is_recursive_and_case_insensitive(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "A.CSV").write_text("x\n1\n")
    (tmp_path / "b.csv").write_text("x\n1\n")
    names = [p.name for p in discover_files(tmp_path, [".csv"])]
    assert names == ["A.CSV", "b.csv"] or sorted(names) == ["A.CSV", "b.csv"]


def test_discover_files_missing_dir_returns_empty(tmp_path: Path):
    assert discover_files(tmp_path / "nope", [".csv"]) == []
