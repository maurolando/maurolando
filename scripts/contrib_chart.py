#!/usr/bin/env python3
"""Genera assets/contrib.svg: calendario de contribuciones con la paleta del perfil.

Se ejecuta desde .github/workflows/contrib.yml (diario). Necesita GITHUB_TOKEN
en el entorno; usa la GraphQL API porque el calendario no esta en la REST API.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime

USER = os.environ.get("GH_USER", "maurolando")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "contrib.svg")

# paleta: vacio -> mas contribuciones
LEVELS = ["#122a24", "#1c5e42", "#2f9e6b", "#52c98d", "#7be39b"]
BG, FG, MUTED, ACCENT = "#0d1117", "#e6edf3", "#8aa3a0", "#7be39b"

CELL, GAP, RADIUS = 11, 3, 2.5
PAD_L, PAD_T = 34, 46
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": "bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": "contrib-chart"},
    )
    payload = json.loads(urllib.request.urlopen(req, timeout=45).read())
    if "errors" in payload:
        raise SystemExit("GraphQL: " + json.dumps(payload["errors"]))
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(count, top):
    if count <= 0:
        return 0
    if top <= 0:
        return 1
    r = count / top
    return 1 if r <= 0.25 else 2 if r <= 0.5 else 3 if r <= 0.75 else 4


def build(cal):
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    top = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=0)

    width = PAD_L + len(weeks) * (CELL + GAP) + 14
    height = PAD_T + 7 * (CELL + GAP) + 36

    cells, months, seen = [], [], set()
    for wi, week in enumerate(weeks):
        x = PAD_L + wi * (CELL + GAP)
        for day in week["contributionDays"]:
            d = datetime.strptime(day["date"], "%Y-%m-%d")
            y = PAD_T + day["weekday"] * (CELL + GAP)
            n = day["contributionCount"]
            fill = LEVELS[level(n, top)]
            delay = round((wi * 7 + day["weekday"]) * 0.0035, 3)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{fill}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay}s" fill="freeze"/>'
                f'<title>{day["date"]}: {n} contribuciones</title></rect>')
            # etiqueta de mes en la primera semana que lo estrena
            key = (d.year, d.month)
            if d.day <= 7 and key not in seen:
                seen.add(key)
                months.append(f'<text x="{x}" y="{PAD_T - 8}" font-size="10" fill="{MUTED}">{MESES[d.month - 1]}</text>')

    dias = "".join(
        f'<text x="{PAD_L - 8}" y="{PAD_T + i * (CELL + GAP) + CELL - 1.5}" font-size="9.5" '
        f'fill="{MUTED}" text-anchor="end">{lbl}</text>'
        for i, lbl in ((1, "Lun"), (3, "Mie"), (5, "Vie")))

    leyenda_x = width - 150
    leyenda = "".join(
        f'<rect x="{leyenda_x + 34 + i * (CELL + 3)}" y="{height - 22}" width="{CELL}" height="{CELL}" '
        f'rx="{RADIUS}" fill="{c}"/>' for i, c in enumerate(LEVELS))

    font = "font-family=\"'Segoe UI', Ubuntu, Verdana, DejaVu Sans, sans-serif\""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Calendario de contribuciones de {USER}">
  <title>{total} contribuciones en el ultimo ano</title>
  <rect width="{width}" height="{height}" rx="10" fill="{BG}" stroke="#1c5e42" stroke-width="1"/>
  <g {font}>
    <text x="{PAD_L - 20}" y="26" font-size="14" font-weight="600" fill="{ACCENT}">{total} contribuciones</text>
    {"".join(months)}
    {dias}
    {"".join(cells)}
    <text x="{leyenda_x}" y="{height - 13}" font-size="9.5" fill="{MUTED}">menos</text>
    {leyenda}
    <text x="{leyenda_x + 34 + 5 * (CELL + 3) + 4}" y="{height - 13}" font-size="9.5" fill="{MUTED}">mas</text>
  </g>
</svg>
'''


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("falta GITHUB_TOKEN")
    svg = build(fetch(token))
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(svg)
    print("escrito %s (%d bytes)" % (os.path.normpath(OUT), len(svg)))


if __name__ == "__main__":
    main()
