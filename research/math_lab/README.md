# ASTRA MATH LAB Ω — laboratoire de recherche v0.1

**Statut : prototype opérationnel et vérifiable hors ligne ; aucune solution de problème récompensé établie.**

Ce laboratoire est ajouté à `Dr-starck66/DeepReasoning-Architecture-` sur une branche scientifique séparée fondée sur la PR #17. Les preuves Lean/Mathlib des PR #15, #16, #17 et les résultats négatifs SAT sont préservés. Aucun nouveau service payant, clé API ou workflow GitHub Actions.

## Registre des prix

`registry.json` suit les sept prix Clay d'origine (dont Poincaré, déjà résolu) et le prix Beal indépendant de l'AMS, chacun annoncé à 1 million de dollars. Les annonces de 2026 sur Riemann et Navier–Stokes **ne sont pas des prix déjà attribués**. Vérifier régulièrement les sources primaires :

- Clay index : https://www.claymath.org/millennium-problems/
- Règles Clay : https://www.claymath.org/millennium-problems/rules/
- Annonce Clay Navier–Stokes du 11/09/2026 : https://www.claymath.org/news/navier-stokes-announcement/
- Prix Beal : https://www.bealbank.com/who-we-are/our-founder/the-beal-conjecture/

Clay n'accepte pas les solutions transmises directement : publication admissible, au moins deux ans, acceptation par la communauté. Un lemme prouvé ne constitue pas automatiquement une solution au problème général.

## Exécution sans frais (Python standard uniquement)

```bash
cd research/math_lab
python3 -m unittest -v test_lab.py
python3 lab.py audit
python3 lab.py beal --base 20 --exponent 6
```

### Contrôles et limites

Le moteur Beal parcourt exactement tous les entiers positifs A,B,C jusqu'à 20 et les exposants x,y,z de 3 à 6. Il calcule avec des **entiers exacts** (pas de nombres flottants), conserve les égalités avec facteur commun et signale tout contre-exemple dans le domaine **fini**. Six tests unitaires comportent un oracle exhaustif à six boucles indépendant du moteur optimisé, l'identité positive `3³ + 6³ = 3⁵`, un doublon de registre volontairement rejeté et le refus des faux statuts de prix. Aucun test fini ne prouve la conjecture de Beal.

Le rapport expérimental est dans `beal_baseline.json`.

## Axes scientifiques

1. **P vs NP** : réutiliser le pont SAT de PR #17, dont les collisions SAT/UNSAT sont démontrées. Ne pas le présenter comme un algorithme polynomial. Tout nouveau candidat doit démontrer un invariant distinguant les deux cas sur une représentation **polynomiale** et résister aux exemples négatifs.
2. **Beal** : construire des théorèmes modulaires vérifiables en plus de la ligne de base exhaustive. Les intervalles finis ne suffisent pas.
3. **Autres défis Clay** : énoncés officiels, littérature, hypothèses indépendantes, lemmes formalisables, vérification critique des revendications concurrentes.
4. **Audit des preuves** : énoncé précis → preuve ou algorithme → contrôle négatif → preuve formelle (Lean/Mathlib quand pertinent) → validation indépendante → publication scientifique → règles du prix.

**Convention de statut :** PASS = preuve d'exécution sur le périmètre indiqué ; PARTIAL = preuve incomplète ; FAIL = réfutation/échec conservé ; UNVERIFIED = non démontré.

**Réutilisation vérifiée dans les descriptions PR :** PR #15 rang 10 certifié par Lean ; PR #16 extensions spectrales ; PR #17 projecteurs uniformes vérifiés et pont SAT naïf réfuté. Aucun résultat P vs NP ou prix ne découle de ces preuves.

**Prochaine expérimentation mathématique :** rechercher des invariants SAT de taille polynomiale et tester leur séparation SAT/UNSAT avant de tenter toute généralisation.
