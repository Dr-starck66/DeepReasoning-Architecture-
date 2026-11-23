# ASTRA MATH LAB Ω — no-go constructif pour les caractéristiques d'occurrence de 3-SAT

## Résultat mathématique exact (portée restreinte)

**Théorème.** Aucun classificateur déterministe de SAT qui ne reçoit **que** `n` (variables), `m` (clauses), et pour chaque variable le nombre d'occurrences positives/négatives, ne peut décider correctement la satisfaisabilité de toutes les formules 3-CNF strictes, même si chaque clause contient exactement trois variables distinctes et si les clauses ne sont pas répétées.

### Preuve constructive

Les deux formules explicites `UNSAT` et `SAT` sont intégralement listées dans `sat_feature_no_go.py`. Elles ont toutes deux **5 variables** et **13 clauses strictes distinctes**. Leurs caractéristiques signées sont strictement identiques :

| variable | positif | négatif |
|---|---:|---:|
| x1 | 5 | 4 |
| x2 | 5 | 6 |
| x3 | 6 | 7 |
| x4 | 2 | 2 |
| x5 | 0 | 2 |

**La formule UNSAT :** elle contient les huit clauses possibles obtenues en choisissant chaque signe de `x1, x2, x3`. Quelle que soit une affectation de ces trois variables, l'une de ces huit clauses est fausse ; la conjonction est donc contradictoire. Les cinq autres clauses ne peuvent restaurer la satisfaisabilité.

**La formule SAT :** l'affectation `x1=vrai, x2=faux, x3=faux, x4=faux, x5=faux` satisfait chacune de ses treize clauses. Vérification indépendante par `verify` et par l'oracle de vérité brute.

Un classificateur qui ne voit que le vecteur de caractéristiques ci-dessus reçoit exactement la même entrée pour les deux formules, mais les deux réponses correctes sont opposées. Il doit donc échouer sur au moins une des deux. **CQFD.**

Il s'agit d'une démonstration générale portant sur **cette classe précise de résumés** : un seul contre-exemple de collision suffit. Ce n'est **pas** une démonstration de P ≠ NP, car un algorithme polynomial peut exploiter des informations structurelles supplémentaires ou un autre encodage.

## Audit reproductible

```bash
cd research/math_lab
python3 -m unittest discover -p 'test*.py' -v
python3 sat_certificate.py
python3 sat_feature_no_go.py
```

- SAT/UNSAT : producteur de certificats DPLL exacts ; vérificateur indépendant de chaque arbre de réfutation ou témoin satisfaisant.
- 200 formules strictes 3-CNF aléatoires déterministes, de 3 à 7 variables, vérifiées contre l'oracle par table de vérité.
- Contrôles négatifs : corruption volontaire de témoin SAT, de feuilles/branches UNSAT, d'une polarité de littéral et suppression de clause.
- Résultats complets : `sat_baseline.json`, `sat_feature_no_go_baseline.json`.
- **Complexité : exponentielle dans le pire cas**, ne prétend pas atteindre le niveau de preuve requis par Clay.
- **Valeur scientifique revendiquée :** lemme exact de réfutation d'une famille de caractéristiques insuffisantes ; **originalité/nouveauté : UNVERIFIED**.

Les PR #15 à #17 demeurent inchangées. Ce travail est un **contrôle restrictif supplémentaire** du laboratoire, et n'efface pas les contre-exemples du projecteur de la PR #17.
