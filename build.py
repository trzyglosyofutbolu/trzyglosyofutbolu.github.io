#!/usr/bin/env python3
"""Buduje stronę "Trzy głosy o futbolu" z pliku data.tsv.

Wejście:  data.tsv (kolumny: date, authors, type, medium, title, url, summary), config.json
Wyjście:  public/index.html, public/data.json, public/feed.xml, public/feed-<autor>.xml
"""
import csv, json, html, pathlib, datetime, email.utils, hashlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "public"
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

AUTHORS = {"stec": "Stec", "zachodny": "Zachodny", "zelazny": "Żelazny"}
CATEGORY = {
    "Artykuł": "teksty", "Felieton": "teksty", "Newsletter": "teksty", "Wpis na blogu": "teksty",
    "Podcast": "podcasty", "Podcast (gość)": "podcasty", "Podcast (wideo)": "podcasty",
    "Analiza wideo": "wideo", "Wideo (studio)": "wideo", "Reportaż wideo": "wideo", "Program TV": "wideo",
    "Magazyn": "ksiazki", "Książka": "ksiazki",
}


def load():
    rows = []
    with open(ROOT / "data.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if not r.get("date"):
                continue
            keys = [k for k, name in AUTHORS.items() if name in r["authors"]]
            r["keys"] = keys
            r["cat"] = CATEGORY.get(r["type"], "teksty")
            r["id"] = hashlib.sha1(r["url"].encode() + r["title"].encode()).hexdigest()[:10]
            rows.append(r)
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def rss(items, title, link, self_url):
    def item(r):
        d = datetime.datetime.fromisoformat(r["date"]).replace(hour=12, tzinfo=datetime.timezone.utc)
        desc = f'{r["authors"]} · {r["medium"]} · {r["type"]}. {r["summary"]}'
        return (
            "<item>"
            f"<title>{html.escape(r['title'])}</title>"
            f"<link>{html.escape(r['url'])}</link>"
            f"<guid isPermaLink=\"false\">{r['id']}</guid>"
            f"<pubDate>{email.utils.format_datetime(d)}</pubDate>"
            f"<category>{html.escape(r['type'])}</category>"
            f"<description>{html.escape(desc)}</description>"
            "</item>"
        )
    now = email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f"<title>{html.escape(title)}</title><link>{html.escape(link)}</link>"
        f'<atom:link href="{html.escape(self_url)}" rel="self" type="application/rss+xml"/>'
        "<description>Nieoficjalny przegląd tekstów, podcastów i wideo Rafała Steca, Michała Zachodnego i Piotra Żelaznego.</description>"
        f"<language>pl</language><lastBuildDate>{now}</lastBuildDate>"
        + "".join(item(r) for r in items[:60])
        + "</channel></rss>\n"
    )


def main():
    rows = load()
    OUT.mkdir(exist_ok=True)
    public = [{k: r[k] for k in ("id", "date", "authors", "keys", "type", "cat", "medium", "title", "url", "summary")} for r in rows]
    (OUT / "data.json").write_text(json.dumps(public, ensure_ascii=False, indent=0), encoding="utf-8")

    base = cfg.get("site_url", "").rstrip("/")
    feeds = {"feed.xml": (rows, cfg["site_name"])}
    for k, name in AUTHORS.items():
        feeds[f"feed-{k}.xml"] = ([r for r in rows if k in r["keys"]], f'{cfg["site_name"]}: {name}')
    for fname, (items, title) in feeds.items():
        (OUT / fname).write_text(rss(items, title, base or "https://example.invalid/", f"{base}/{fname}"), encoding="utf-8")

    page = (ROOT / "template.html").read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/[]", json.dumps(public, ensure_ascii=False))
    page = page.replace("/*__CONFIG__*/{}", json.dumps({
        "subscribeFormAction": cfg.get("subscribe_form_action", ""),
        "subscribePageUrl": cfg.get("subscribe_page_url", ""),
        "siteUrl": base,
        "contactEmail": cfg.get("contact_email", ""),
        "built": datetime.date.today().isoformat(),
    }, ensure_ascii=False))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"OK: {len(rows)} pozycji, {len(feeds)} kanały RSS -> {OUT}")


if __name__ == "__main__":
    main()
