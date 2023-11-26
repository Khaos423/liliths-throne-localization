from pathlib import Path
from urllib import request
import requests
import os
import zipfile
import shutil

from const import *
from logger import logger


class Repo:
    def __init__(self, branch: str, paratranz_access_token: str) -> None:
        self.branch = branch
        self.source_dir: Path = Path(SOURCE_DIR)
        self.paratranz_access_token = paratranz_access_token
        self.latest_commit = ""

    def fetch_latest_version(self) -> None:
        if os.environ.get("USE_GITHUB_ACTION") is not None:
            download_url = ""
        else:
            download_url = PROXY_URL
        download_url += REPO_BASE_URL + f"/archive/refs/heads/{self.branch}.zip"

        api_url = REPO_API_URL + f"/commits"

        path = Path(DOWNLOAD_DIR)

        if not path.exists():
            path.mkdir()
        try:
            with requests.get(
                api_url,
                stream=True,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": GITHUB_PUBLIC_ACCESS_TOKEN,
                },
            ) as r:
                if r.status_code == 200 and len(r.content) > 0:
                    self.latest_commit = r.json()[0]["sha"]
                else:
                    self.latest_commit = "unknown"
        except:
            self.latest_commit = "unknown"

        file_path = path / f"repo-latest-{self.latest_commit}.zip"
        if not file_path.exists() and self.latest_commit != "unknown":
            for existing_file in path.glob("repo-latest-*.zip"):
                os.remove(existing_file)
            request.urlretrieve(
                download_url, path / f"repo-latest-{self.latest_commit}.zip"
            )

    def unzip_latest_version(self) -> None:
        zip_path = list(Path(DOWNLOAD_DIR).glob("**/repo-latest-*.zip"))[0]
        if self.latest_commit == "":
            self.latest_commit = zip_path.stem.split("-")[-1]
        extract_path = self.source_dir

        if extract_path.exists():
            shutil.rmtree(extract_path, ignore_errors=True)
        # extract_path.mkdir()

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path.parent)
        # os.rename("./liliths-throne-public-dev/", extract_path)

    def fetch_latest_dict(self) -> None:
        output_url = PARATRANZ_API_URL + "/artifacts"  # use post
        download_url = PARATRANZ_API_URL + "/artifacts/download"

        path = Path(DOWNLOAD_DIR)

        if not path.exists():
            path.mkdir()

        file_path = path / f"dict-latest.zip"
        if file_path.exists():
            os.remove(file_path)

        opener = request.build_opener()
        opener.addheaders = [("Authorization", self.paratranz_access_token)]
        request.install_opener(opener)

        request.urlretrieve(download_url, file_path)

    def unzip_latest_dict(self) -> None:
        zip_path = Path(DOWNLOAD_DIR) / f"dict-latest.zip"
        extract_path = Path(ROOT_DIR)
        old_dict_dir = Path(OLD_DICT_DIR)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        if old_dict_dir.exists():
            shutil.rmtree(old_dict_dir)

        shutil.move(extract_path / "utf8", old_dict_dir)
        shutil.rmtree(extract_path / "raw", ignore_errors=True)

    def updata_source_dict(self, dict_path: Path):
        pass


if __name__ == "__main__":
    repo = Repo("dev", "")

    repo.fetch_latest_dict()
    # repo.unzip_latest_dict()

    # repo.fetch_latest_version()
    # repo.unzip_latest_version()
