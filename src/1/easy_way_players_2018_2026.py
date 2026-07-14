import pandas as pd

years = range(2018, 2027)

dfs = []

for year in years:
    print(f"Downloading {year}...")

    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"

    df = pd.read_html(url)[0]

    df = df[df.Player != "Player"]

    df["Season"] = year

    dfs.append(df)

players = pd.concat(dfs, ignore_index=True)

players.to_csv(
    "NBA_Players_2018_2026.csv",
    index=False,
    encoding="utf-8-sig"
)

print(players.head())
print("Done!")
