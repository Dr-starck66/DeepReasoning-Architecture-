# BetGPT — evidence-based SEO pilot

At 2026-10-26T15:07:06.352Z, status: PARTIAL

Reference: MIT seo-audit guidance, commit 1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff. No third-party execution.

| Check | Result | Evidence |
| --- | --- | --- |
| endpoint:/ | PASS | HTTP 200 URL https://betgpt.live/ in 961ms |
| endpoint:/actualites | PASS | HTTP 200 URL https://betgpt.live/actualites in 6797ms |
| endpoint:/robots.txt | PASS | HTTP 200 URL https://betgpt.live/robots.txt in 735ms |
| endpoint:/sitemap.xml | PASS | HTTP 200 URL https://betgpt.live/sitemap.xml in 1367ms |
| endpoint:/news-sitemap.xml | PASS | HTTP 200 URL https://betgpt.live/news-sitemap.xml in 1459ms |
| endpoint:/sitemap-images.xml | PASS | HTTP 200 URL https://betgpt.live/sitemap-images.xml in 1608ms |
| robots-not-global-block | PASS | Global disallow |
| robots-sitemap | PASS | Sitemap reference |
| sitemap-xml | PASS | XML root |
| sitemap-nonempty | PASS | 1297 loc URLs |
| sitemap-same-origin | PASS | 0 foreign/malformed URLs; examples:  |
| sitemap-duplicates | PASS | 0 duplicates |
| news-fresh-dates | PASS | 8 dates, invalid 0, stale 0, future 0 |
| news-size | PASS | 8 URLs |
| canonical:/ | PASS | https://betgpt.live |
| noindex:/ | PASS | Static HTML meta scan |
| h1:/ | PASS | 1 static H1 |
| schema:/ | UNVERIFIED | Needs DOM rendering or Google Rich Results Test |
| canonical:/actualites | PASS | https://betgpt.live/actualites |
| noindex:/actualites | PASS | Static HTML meta scan |
| h1:/actualites | PASS | 1 static H1 |
| schema:/actualites | UNVERIFIED | Needs DOM rendering or Google Rich Results Test |

HTTP success does not prove Search Console indexing, News or Discover visibility, Core Web Vitals or rendered schema.
