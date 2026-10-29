# A Thousand Sails · website

The public website of **A Thousand Sails / 万里千帆** (Android, `com.mz.wlqf`): the home page and
the pages Google Play asks for. It is in English, 简体中文 and 日本語.

| Page | English | Used in Play Console for |
| --- | --- | --- |
| Home | `/` | Website, store listing |
| Privacy policy | `/privacy.html` | App content › Privacy policy; store listing |
| Terms of service | `/terms.html` | (linked from the home page) |
| Delete your data | `/delete-data.html` | Data safety › data deletion |

The Chinese pages are under `/zh/` and the Japanese ones under `/ja/`.

## Editing

The pages are made from `src/` by a small script. Python 3.10 or later, standard library only.

```
python build.py
```

* `src/site.json` holds the shared settings: contact email, developer name, site address, the
  policies' "last updated" date and the Play link.
* `src/i18n.json` holds the menu words of each language.
* `src/<lang>/<page>.html` holds a page's text: a front block (`title`, `description`), then the
  body. `{{name}}` is replaced from the two JSON files.
* `src/layout.html` and `src/style.css` are shared by every page.

The output goes to `docs/`, and `docs/` is committed: GitHub Pages serves it as is. Change `src/`,
run the build and commit both. Do not edit `docs/*.html` by hand.

When a policy changes, change all three languages and the `updated` date in `src/site.json`. The
English text is the one that governs.

## Hosting

GitHub Pages, from the `main` branch's `/docs` folder (Settings › Pages). The site is at
<https://minggamecn.github.io/sea-site/>. For a custom domain, set `domain` and `base_url` in
`src/site.json` and rebuild: the build writes `docs/CNAME`.
