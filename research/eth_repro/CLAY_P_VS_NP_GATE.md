# ASTRA Ω — Clay P versus NP : porte de validation 3-SAT

**Objet exact :** chercher une preuve admissible au [problème P versus NP du Clay Mathematics Institute](https://www.claymath.org/millennium/p-vs-np/), sans confondre une identité matricielle vérifiée avec un algorithme polynomial pour le problème NP-complet 3-SAT.

## Ce qui est certifié (PASS)

- La famille E_q de projecteurs construits avec les swaps, l'identité E_q=F_q pour tout q et la formule de rang dans Mathlib : [CI #45135520573](https://github.com/Dr-starck66/DeepReasoning-Architecture-/actions/runs/45135520573).
- Le rang vaut C(q,2)3^(q-2)+C(q,3)3^(q-3), mais **reste exponentiel en q** bien que son rapport à 4^q tende vers zéro.
- Le calcul explicite du produit matrice-vecteur par DP coûte O(q 4^q) et nécessite O(4^q) mémoire. Pour n=2q variables de SAT, cela représente O(n 2^n) opérations et O(2^n) mémoire — **pas** un algorithme polynomial.

## Contrôle négatif décisif (exécution : voir reçu CI)

Encodage naïf : représenter une formule F en 3-CNF de n=2q variables par son vecteur de vérité v_F, avec 4^q=2^n coefficients, puis calculer E_q v_F. Ce seul vecteur projeté ne suffit **pas** à décider 3-SAT.

Pour tout q≥2, trois formules de largeur ≤3 (clauses unitaires permises) :

1. F_sat=(x1) possède 2^(n-1) affectations satisfaisantes ;
2. F_unsat=(x1) ∧ (¬x1) possède zéro affectation satisfaisante ;
3. F_true=conjonction vide possède 2^n affectations satisfaisantes.

Pourtant E_q v_sat = E_q v_unsat = E_q v_true = 0.

**Pourquoi, pour tout q ?** E_q ne garde que les modes antisymétriques sur exactement deux ou trois swaps locaux. La table de vérité de x1 ne dépend que d'une variable : elle est symétrique sur les autres axes locaux, et contient au maximum un mode antisymétrique. Celle de la tautologie est symétrique sur **tous** les axes, et celle de la contradiction est nulle. Les trois sont donc projetées sur zéro. Un post-traitement qui n'utilise **que** E_q v ne peut pas distinguer satisfaisable et insatisfaisable. Il s'agit d'une obstruction à cet encodage, **pas** d'une preuve P≠NP ni d'une impossibilité pour un encodage plus riche.

**Contrôle positif :** F=(x1)∧(x2) possède un mode antisymétrique sur deux swaps, donc E_q v_F ≠ 0. L'expérience ne produit pas artificiellement zéro pour tout.

La batterie reproductible utilise les oracles indépendants de `eth_lab.py`, l'application exacte `apply_scaled_dp`, les dimensions q=2,3,4, des sommes de vérité et des empreintes SHA-256, avec tests de rejet.

Commande depuis la racine :

```bash
python3 -m unittest discover -s research/eth_repro -p 'test_clay_sat_bridge_gate.py' -v
python3 research/eth_repro/clay_sat_bridge_gate.py --output /tmp/astra_clay_gate.json
```

## Conditions pour revendiquer le prix

**Voie P=NP :** fournir un algorithme uniforme déterministe sur des 3-CNF de taille arbitraire, prouver la correction oui/non sur toutes les entrées, et borner les opérations en bits, y compris la construction de l'encodage, par un polynôme en la **taille de l'entrée** (variables et clauses). Un test sur un petit corpus ne suffit pas.

**Voie P≠NP :** établir une borne inférieure excluant *tous* les algorithmes déterministes polynomiaux pour un langage NP-complet ; prouver l'échec de notre seul projecteur ne suffit pas.

**Référence de comparaison :** le préprint [OpenAI — The Exponential Time Hypothesis is False (25 oct. 2026)](https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026) annonce un algorithme #SAT en temps sous-exponentiel : une telle borne reste asymptotiquement **supérieure à tout polynôme** et ne résout donc pas P versus NP. Toute extension ASTRA doit partir d'un mécanisme de compression calculable directement sur la formule, pas d'un tableau de vérité déjà exponentiel.

**Statut** : preuve du rang PASS, encodage SAT direct FAIL (contre-exemples), algorithme polynomial général UNVERIFIED, éligibilité au million FAIL à ce stade. Aucune revendication soumise à Clay, aucune publication et aucune dépense initiée.
