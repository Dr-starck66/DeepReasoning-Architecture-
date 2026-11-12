# ASTRA MATH LAB Ω — confrontation aux sources primaires (2026-11-01)

**Statut scientifique : PARTIAL.** Ce dépôt reste isolé en PR, non déployé dans l'application.

Sources inspectées :
- Manuscrit OpenAI, *The Exponential Time Hypothesis is False* (17 octobre, révisé 25 octobre 2026), source LaTeX : https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex
- Portée officielle Lean : https://github.com/openai/math/blob/main/lean/docs/378.md
- Énoncé à comparer : https://github.com/openai/math/blob/main/lean/ComparatorChallenges/SubexponentialSAT.lean

## Distinction source / reproduction

| Élément exact | Source | ASTRA | Preuve |
|---|---|---|---|
| Phi_e=1-prod(1-L) et #F=sum_x prod_e Phi_e | A direct polynomial for the count | Identité finie Python et Lean | Python PASS; Lean statut CI |
| Formes de remplacement **linéaires homogènes par occurrence** P_{e,v}(T), P(0)=e_v, deg H<=MR | A polynomial family with easier evaluation points | Exemple fini P_{e,v} de degré 2 | Python PASS |
| Décomposition sum_y prod_g sum_{u:C_gu=y_g} A_g | Separating the sum by fixing measurements | Exemple valide avec C_g=(1,1), t=1,2; rejet à t=0 | Python PASS |
| Reconstruction depuis coefficients de H(t+z) | Recovering the count from Taylor coefficients | Exacte sur Q, t=1,2, ordre 10, interpolation rectangulaire et contrôle négatif | Python PASS |
| Encodage du SAT.CNF Fin n de Lean (ensembles, littéraux ordonnés) | ComparatorChallenges/SubexponentialSAT.lean | Traduction côté Python avec dédoublonnage, test déterministe | Python PARTIAL : correspondance non vérifiée par Lean |
| Construction faible rang I-M0, expandeurs, parité, planification déterministe | Reste du manuscrit | **Non implémenté** | UNVERIFIED |
| Machine primitive, temps subexponentiel et espace poly | Lean exact_count_and_sat | **Non reproduit** | UNVERIFIED |
| Exposant plus serré du théorème papier | Texte vs note Lean 378 | **Non formalisé ici** | UNVERIFIED |

## Résultat expérimental (test Python local effectif)

Cas F=(x1 ∨ x3 ∨ x4)∧(¬x1 ∨ x2)∧(x2 ∨ ¬x3)∧(¬x2 ∨ x4), n=4.

H(T)=5−3T/2−4T²+3T³−T⁴/2 ; H(0)=5 satisfactions.

Majoration générale MR=18 (le degré effectif est 4). Les 10 premiers coefficients de Taylor en t=1 et t=2 déterminent et reconstruisent *exactement* H, et H(t) égale la somme factorisée par mesures aux deux points.

**Tests :** `python -m unittest discover -s research/eth_repro -p 'test_*.py' -v` : 18/18 tests PASS dans un conteneur temporaire ; 130 assertions internes PASS sur le corpus source (`seed=20261101, trials=60`). Aucun raccourci de complexité démontré.

**Correction importante :** le précédent prototype utilisait X_i(T)=x_i+T(1+x_{i+1}), **affine**, qui n'est *pas* la famille homogène de formes P_{e,v}(T) du manuscrit. La nouvelle construction respecte P(0)=e_v, varie par occurrence et impose la condition de row-space sur les groupes à deux points. La méthode de séparateur antérieure n'était qu'une analogie.

## Statut Lean

`PaperFinite.lean` formalise uniquement des identités finies et un témoin à quatre variables, sans `sorry`. La vérification réelle nécessite l'exécution de `lean research/eth_repro/PaperFinite.lean` sur Lean 4; le CI public isolé vise cette seule cible. Ni la compilation de ce fichier ni une CI verte ne prouvent le résultat ETH ni ne remplacent Comparator et la relecture humaine de la sémantique des énoncés.

Pas de frais supplémentaires ni de tâches planifiées.
