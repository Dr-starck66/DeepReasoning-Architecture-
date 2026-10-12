# UNIVERSAL SKILL INTELLIGENCE Ω — Premier pilote appliqué : SEO de BetGPT

**Amélioration réelle attendue** : détecter les défauts techniques bloquants des pages publiques, robots, sitemaps et métadonnées sans attendre qu'un audit manuel soit demandé.

- Méthodologie : `seo-audit` de `coreyhaines31/marketingskills`, commit immuable `1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff`, licence MIT. [Source](https://github.com/coreyhaines31/marketingskills/blob/1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff/skills/seo-audit/SKILL.md).
- Application : script d'audit HTTP **écrit localement**. Aucun code exécutable tiers, abonnement, connexion de compte, ou commande d'installation. Les conseils récupérés sont considérés comme données non fiables.
- Cibles HTTPS : `https://betgpt.live/`, `/actualites`, `/robots.txt`, `/sitemap.xml`, `/news-sitemap.xml`, `/sitemap-images.xml`.
- Mesures : codes HTTP, blocage global robots, sitemap, URLs étrangères/doublons, dates News récentes, indications canonicals et H1 **dans HTML statique**.
- Limites explicites : JSON-LD, canonical ou H1 générés dans le navigateur = UNVERIFIED, jamais de faux FAIL; pas de validation GSC / Discover / News / Core Web Vitals.
- CI : `.github/workflows/universal-skills-seo-pilot.yml`. Exécution sur chaque changement de ce pilote et chaque lundi (et à la demande). Artifacts datés JSON et Markdown, résultat FAIL en cas d'anomalie vérifiée.
- Critère de réussite : tests Node PASS + requêtes HTTPS réelles + rapport archivé. Prochain jalon : créer un correctif dans `Dr-starck66/betgpt-railway` **uniquement pour un défaut confirmé et reproductible**, sans déployer en force si ASTRA MASTER GATE est FAIL.

Status de ce document : conçu, pas encore audité par CI au moment du commit.
