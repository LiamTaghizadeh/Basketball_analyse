import os
import time
import random
import re
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


class BasketballDownloader:
    def __init__(self, output_dir="basketball_pages", chunk_size=3, start_from=0):
        self.output_dir = output_dir
        self.gamers_dir = os.path.join(output_dir, "gamers")
        self.clubs_dir = os.path.join(output_dir, "clubs")
        self.chunk_size = chunk_size
        self.start_from = start_from
        self.base_url = "https://www.basketball-reference.com"
        self._create_directories()

        self.driver_pool = queue.Queue()
        for _ in range(chunk_size):
            self.driver_pool.put(self._create_driver())

    def _create_directories(self):
        os.makedirs(self.gamers_dir, exist_ok=True)
        os.makedirs(self.clubs_dir, exist_ok=True)

    def _create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Linux NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def _cleanup_drivers(self):
        while not self.driver_pool.empty():
            try:
                driver = self.driver_pool.get_nowait()
                driver.quit()
            except queue.Empty:
                break

    def _safe_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', "_", name).strip() + ".html"

    def _download_page(self, url, filepath, retries=3):
        for attempt in range(retries):
            driver = None
            try:
                driver = self.driver_pool.get(timeout=30)
                driver.get(url)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(random.uniform(1.5, 3.5))
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                self.driver_pool.put(driver)
                return True
            except Exception:
                if driver:
                    driver.quit()
                    driver = self._create_driver()
                    self.driver_pool.put(driver)
                else:
                    self.driver_pool.put(self._create_driver())
                time.sleep(5 * (attempt + 1))
        return False

    def _fetch_soup(self, url):
        driver = self._create_driver()
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(random.uniform(1, 2))
            return BeautifulSoup(driver.page_source, "html.parser")
        finally:
            driver.quit()

    def _get_player_list(self, limit=None):
        players = []
        letters = "abcdefghijklmnopqrstuvwxyz"
        for letter in letters:
            url = f"{self.base_url}/players/{letter}/"
            try:
                soup = self._fetch_soup(url)
                table = soup.find("table", {"id": "players"})
                if not table:
                    continue
                rows = table.find("tbody").find_all("tr")
                for row in rows:
                    th = row.find("th")
                    if not th:
                        continue
                    link = th.find("a")
                    if not link:
                        continue
                    name = link.text.strip()
                    url = self.base_url + link.get("href")
                    players.append({"name": name, "url": url})
                    if limit and len(players) >= limit:
                        return players
            except Exception:
                continue
            time.sleep(random.uniform(0.5, 1.5))
        return players

    def _get_team_list(self, season="2026"):
        teams = []
        abbrs = [
            "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
            "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
            "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
        ]
        for abbr in abbrs:
            url = f"{self.base_url}/teams/{abbr}/{season}.html"
            teams.append({"name": abbr, "url": url})
        return teams

    def download_gamers(self, limit=None):
        print("Fetching player list from beginning to end...")
        all_players = self._get_player_list(limit)
        total = len(all_players)
        players = all_players[self.start_from:]
        print(f"Total players: {total} | Starting from record {self.start_from} -> {len(players)} players")
        if not players:
            print("No players to download.")
            return

        with ThreadPoolExecutor(max_workers=self.chunk_size) as executor:
            futures = {}
            for idx, player in enumerate(players, start=self.start_from + 1):
                filename = self._safe_filename(player["name"])
                filepath = os.path.join(self.gamers_dir, filename)

                if os.path.exists(filepath):
                    print(f"[{idx}/{total}] {player['name']}... found")
                    continue

                futures[executor.submit(self._download_page, player["url"], filepath)] = (idx, player["name"])

            for future in as_completed(futures):
                idx, name = futures[future]
                try:
                    success = future.result()
                    status = "OK" if success else "FAIL"
                except Exception:
                    status = "FAIL"
                print(f"[{idx}/{total}] {name}... {status}")

    def download_clubs(self, season="2026"):
        teams = self._get_team_list(season)
        total = len(teams)
        print(f"Total teams: {total}")
        if not teams:
            return

        with ThreadPoolExecutor(max_workers=self.chunk_size) as executor:
            futures = {}
            for idx, team in enumerate(teams, 1):
                filename = f"{team['name']}_{season}.html"
                filepath = os.path.join(self.clubs_dir, filename)

                if os.path.exists(filepath):
                    print(f"[{idx}/{total}] {team['name']}... found (already exists)")
                    continue

                futures[executor.submit(self._download_page, team["url"], filepath)] = (idx, team["name"])

            for future in as_completed(futures):
                idx, name = futures[future]
                try:
                    success = future.result()
                    status = "OK" if success else "FAIL"
                except Exception:
                    status = "FAIL"
                print(f"[{idx}/{total}] {name}... {status}")

    def run(self, player_limit=None, season="2026"):
        try:
            print("=" * 60)
            print("Starting concurrent download with Selenium")
            print(f"Concurrency: {self.chunk_size}")
            print(f"Starting from player number: {self.start_from}")
            print("=" * 60)
            self.download_gamers(player_limit)
            self.download_clubs(season)
        finally:
            self._cleanup_drivers()
            print("All drivers closed. :(((")
            print("=" * 60)
            print("Download completed.!!!!!")
            print("=" * 60)


def main():
    downloader = BasketballDownloader(
        output_dir="basketball_pages",
        chunk_size=3,
        start_from=0 # in barayeh start ke age moshkel khord az on ja shro kone
    )
    downloader.run(player_limit=None, season="2026")


if __name__ == "__main__":
    main()
