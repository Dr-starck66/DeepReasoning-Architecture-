# ASTRA MATH LAB Ω — ETH / #3-SAT — reproduction partielle

**Scope:** code original éducatif, sans dépendances payantes, qui vérifie sur de petites formules deux identités finies utilisées comme briques mathématiques dans *The Exponential Time Hypothesis is False* (OpenAI, 25 octobre 2026). **Ce projet ne reproduit ni le nouvel algorithme sous-exponentiel, ni ses bornes asymptotiques, ni sa preuve Lean.**

Source primaire: https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026 ; note de portée Lean: https://github.com/openai/math/blob/main/lean/docs/378.md.

## Ce qui est réellement implémenté

1. **Vérité terrain indépendante:** comptage exhaustif exact des affectations (`count_exhaustive`).
2. **Contrôle indépendant:** décomposition récursive de Shannon, avec cache (`count_dpll`).
3. **Identité polynomiale:** pour chaque clause, `Φ=1−∏(1−littéral)` ; `H(t)=Σ_x∏Φ(clause, X(t))`, avec `X_i(t)=x_i+t(1+x_{i+1})`, donc `H(0)=#F`. `interpolate_at_zero` reconstruit H(0) à partir de H(1), … H(D+1), `D=nombre total de littéraux`. Il s'agit d'une interpolation entière exacte sans accélération asymptotique.
4. **Séparation conditionnelle spéciale:** conditionner sur un petit ensemble de variables, puis factoriser les composantes indépendantes. C'est un exemple *élémentaire* de séparation après observation partagée, **pas** la construction par formes de remplacement du papier.
5. **Recherche de candidat reproductible:** `discover_cutset` essaie les séparateurs de 0 à 2 variables et classe les coûts approximatifs d'énumération, puis le vérificateur confirme le nombre de solutions avec l'oracle.
6. **Audit / falsification:** 6 propriétés métamorphiques par cas, tests aléatoires déterministes et deux contrôles négatifs obligatoires (OU remplacé par ET, interpolation avec échantillonnage insuffisant). Si un contrôle négatif n'est pas détecté, statut `FAIL`.

## Exécuter gratuitement, sur un Python déjà disponible

Depuis la racine du dépôt :

```bash
python -m unittest discover -s research/eth_repro -p 'test_*.py' -v
python research/eth_repro/eth_lab.py --cases 80 --seed 20261101 --nmax 7 --output eth_report.json
```

`eth_report.json` contient le statut, le corpus SHA-256 déterministe, le nombre de vérifications, le nombre d'échecs et la détection des deux contrôles négatifs. Le fichier de rapport n'est pas nécessaire au fonctionnement du code.

## Niveaux de preuve

- `PASS` des tests locaux : **uniquement** égalité des comptages finis et détection des falsifications, pour le périmètre exécuté.
- `PARTIAL` du programme de recherche : reproduction de mécanismes élémentaires, **aucune** preuve nouvelle et **aucune** démonstration d'ETH.
- `UNVERIFIED` : preuve Lean du papier non recompilée ici, généralisation asymptotique, déploiement/planification continue.

Le module peut être rattaché à un agent scientifique existant, mais il ne tourne pas tout seul une fois cette session terminée. Aucun nouveau cron, secret, API, service cloud ou infrastructure facturable.
