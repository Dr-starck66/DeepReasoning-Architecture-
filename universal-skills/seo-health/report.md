# BetGPT — evidence-based SEO pilot

At 2026-10-19T15:31:51.640Z, status: PARTIAL

Reference: MIT seo-audit guidance, commit 1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff. No third-party execution.

| Check | Result | Evidence |
| --- | --- | --- |
| endpoint:/ | PASS | HTTP 200 URL https://betgpt.live/ in 755ms |
| endpoint:/actualites | UNVERIFIED | HTTP 0 URL https://betgpt.live/actualites in 12001ms; The operation was aborted due to timeout |
| endpoint:/robots.txt | PASS | HTTP 200 URL https://betgpt.live/robots.txt in 2618ms |
| endpoint:/sitemap.xml | PASS | HTTP 200 URL https://betgpt.live/sitemap.xml in 4835ms |
| endpoint:/news-sitemap.xml | PASS | HTTP 200 URL https://betgpt.live/news-sitemap.xml in 4539ms |
| endpoint:/sitemap-images.xml | PASS | HTTP 200 URL https://betgpt.live/sitemap-images.xml in 4850ms |
| robots-not-global-block | PASS | Global disallow |
| robots-sitemap | PASS | Sitemap reference |
| sitemap-xml | PASS | XML root |
| sitemap-nonempty | PASS | 2405 loc URLs |
| sitemap-same-origin | PASS | 0 foreign/malformed URLs; examples:  |
| sitemap-duplicates | PASS | 0 duplicates |
| news-fresh-dates | PASS | 1 dates, invalid 0, stale 0, future 0 |
| news-size | PASS | 1 URLs |
| canonical:/ | PASS | https://betgpt.live |
| noindex:/ | PASS | Static HTML meta scan |
| h1:/ | PASS | 1 static H1 |
| schema:/ | UNVERIFIED | Needs DOM rendering or Google Rich Results Test |

HTTP success does not prove Search Console indexing, News or Discover visibility, Core Web Vitals or rendered schema.
