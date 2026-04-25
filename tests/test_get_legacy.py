import importlib.util
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "get_legacy.py"
SPEC = importlib.util.spec_from_file_location("get_legacy", SCRIPT_PATH)
get_legacy = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(get_legacy)


def test_build_cutout_urls() -> None:
    jpg_url = get_legacy.build_cutout_url(125.1885, 19.3626, "jpg")
    fits_url = get_legacy.build_cutout_url(125.1885, 19.3626, "fits")

    assert jpg_url == (
        "https://www.legacysurvey.org/viewer/cutout.jpg?"
        "ra=125.1885&dec=19.3626&layer=ls-dr9&pixscale=0.25"
    )
    assert fits_url == (
        "https://www.legacysurvey.org/viewer/cutout.fits?"
        "ra=125.1885&dec=19.3626&layer=ls-dr9&pixscale=0.25"
    )


def test_output_paths_use_default_coordinate_basename() -> None:
    jpg_path, fits_path = get_legacy.cutout_output_paths(125.1885, 19.3626)

    assert jpg_path == Path("cutout_125.1885_19.3626.jpg")
    assert fits_path == Path("cutout_125.1885_19.3626.fits")


def test_output_paths_replace_supplied_suffix() -> None:
    jpg_path, fits_path = get_legacy.cutout_output_paths(125.1885, 19.3626, "images/target.fits")

    assert jpg_path == Path("images/target.jpg")
    assert fits_path == Path("images/target.fits")


def test_existing_file_is_not_downloaded_without_overwrite(tmp_path, monkeypatch) -> None:
    output_path = tmp_path / "cutout.jpg"
    output_path.write_text("existing", encoding="utf-8")

    def fail_download(*args, **kwargs):
        raise AssertionError("urlretrieve should not be called")

    monkeypatch.setattr(get_legacy, "urlretrieve", fail_download)

    with pytest.warns(UserWarning, match="already exists"):
        downloaded = get_legacy.download_file("https://example.com/cutout.jpg", output_path)

    assert downloaded is False
    assert output_path.read_text(encoding="utf-8") == "existing"


def test_overwrite_downloads_existing_file(tmp_path, monkeypatch) -> None:
    output_path = tmp_path / "cutout.jpg"
    output_path.write_text("existing", encoding="utf-8")
    calls = []

    def fake_download(url, filename):
        calls.append((url, Path(filename)))
        Path(filename).write_text("new", encoding="utf-8")

    monkeypatch.setattr(get_legacy, "urlretrieve", fake_download)

    downloaded = get_legacy.download_file(
        "https://example.com/cutout.jpg",
        output_path,
        overwrite=True,
    )

    assert downloaded is True
    assert calls == [("https://example.com/cutout.jpg", output_path)]
    assert output_path.read_text(encoding="utf-8") == "new"


def test_download_cutouts_requests_jpg_and_fits(tmp_path, monkeypatch) -> None:
    calls = []

    def fake_download(url, output_path, overwrite=False):
        calls.append((url, output_path, overwrite))
        return True

    monkeypatch.setattr(get_legacy, "download_file", fake_download)

    jpg_path, fits_path = get_legacy.download_cutouts(
        125.1885,
        19.3626,
        output=str(tmp_path / "legacy_cutout"),
        overwrite=True,
    )

    assert jpg_path == tmp_path / "legacy_cutout.jpg"
    assert fits_path == tmp_path / "legacy_cutout.fits"
    assert calls == [
        (
            get_legacy.build_cutout_url(125.1885, 19.3626, "jpg"),
            jpg_path,
            True,
        ),
        (
            get_legacy.build_cutout_url(125.1885, 19.3626, "fits"),
            fits_path,
            True,
        ),
    ]
