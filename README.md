# Trzy głosy o futbolu

Nieoficjalny agregator tekstów, podcastów i wideo Rafała Steca, Michała Zachodnego i Piotra Żelaznego.

## Jak to działa

- `data.tsv`: wszystkie pozycje (data, autorzy, typ, medium, tytuł, link, krótki opis własnymi słowami).
- `config.json`: nazwa strony, adres strony i ustawienia zapisu na maile.
- `python3 build.py`: buduje katalog `public/` (strona `index.html`, `data.json`, kanały RSS: `feed.xml` oraz `feed-stec.xml`, `feed-zachodny.xml`, `feed-zelazny.xml`).
- Codzienne zadanie Claude dopisuje nowe pozycje do `data.tsv`, uruchamia `build.py` i wypycha zmiany do repozytorium.

## Publikacja na GitHub Pages

1. Załóż publiczne repozytorium, `trzyglosyofutbolu.github.io` (na koncie `trzyglosyofutbolu`), i wrzuć do niego zawartość tego folderu.
2. Settings, Pages: jako źródło wybierz „GitHub Actions”. Workflow `.github/workflows/pages.yml` sam zbuduje stronę po każdej zmianie w `main`.
3. Wpisz adres strony (`https://trzyglosyofutbolu.github.io`, już ustawiony) w `config.json` jako `site_url` i przebuduj.

## Zapis na maile

Strona nie przechowuje adresów. Zapisami i wysyłką zajmuje się usługa newsletterowa, która czyta `feed.xml`:

- **Buttondown** (płatny plan z RSS-to-email): w `config.json` wpisz `subscribe_form_action` = `https://buttondown.com/api/emails/embed-subscribe/TWOJA_NAZWA`, a w Buttondown włącz automatyzację RSS na adres `feed.xml`.
- **MailerLite** (kampanie RSS w planie płatnym): podaj link do formularza jako `subscribe_page_url`.
- Bez płatnej usługi: zostaw oba pola puste. Strona pokaże adres RSS, który czytelnik może podpiąć do czytnika albo darmowego serwisu typu Blogtrottr.

Usługa newsletterowa obsługuje potwierdzenie zapisu (double opt-in), wypisywanie i dane osobowe zgodnie z RODO. Jako administrator listy uzupełnij w niej klauzulę informacyjną.
