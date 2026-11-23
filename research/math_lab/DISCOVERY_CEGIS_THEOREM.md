# ASTRA MATH LAB Ω — moteur de découverte CEGIS et théorème des marginales signées

**Date :** 23 novembre 2026. **Portée :** résultat exact pour une classe d'informations restreinte ; nouveauté scientifique **UNVERIFIED** ; P versus NP **UNVERIFIED** ; prix Clay **NON ÉLIGIBLE**.

## Découverte générée par recherche

`discovery_engine.py` n'encode pas au départ les deux formules gagnantes. Il énumère les 70 groupes possibles de quatre clauses signées parmi les huit clauses sur `x1,x2,x3`. Il classe les groupes par statistiques de cooccurrence signées d'ordre 1 et 2, trouve le premier couple de groupes distincts mais statistiquement indiscernables (à la 42e combinaison), construit une famille de gadgets forçant une affectation, puis recherche un couple SAT/UNSAT. Il vérifie avec un second calcul autonome des marginales, un oracle de vérité exhaustive et les certificats SAT/UNSAT de la PR #20.

## Théorème et preuve (indépendants de l'exécution Python)

Pour **tout n ≥ 5**, il existe deux formules 3-CNF strictes sur n variables, chacune avec **16 clauses distinctes de trois variables distinctes**, telles que :

1. pour tout littéral signé ℓ, son nombre d'occurrences est identique dans les deux formules ;
2. pour toute paire de littéraux signés portant sur deux variables distinctes (ℓ₁, ℓ₂), le nombre de clauses qui contiennent simultanément les deux littéraux est identique ;
3. exactement une de ces deux formules est satisfaisable.

**Construction.** Pour les variables x₁,x₂,x₃, considérons les huit clauses `(±x1 ∨ ±x2 ∨ ±x3)`. Partitionnons-les en deux familles de quatre, suivant la **parité du nombre de littéraux négatifs**. Pour une signature fixée sur une seule variable, chaque famille en contient exactement deux. Pour une signature fixée sur deux variables distinctes, chacune en contient exactement une, car le signe de la troisième variable est déterminé par la parité. Ainsi, les familles ont les mêmes statistiques d'ordre 1 et 2.

Choisissons une affectation cible t₁,t₂,t₃ et les trois littéraux Lᵢ vrais exactement lorsque xᵢ=tᵢ. Ajoutons aux deux familles les mêmes **douze clauses** `(Lᵢ ∨ ±x4 ∨ ±x5)` pour i=1,2,3 et pour les quatre signes de (x4,x5). Ces quatre clauses, pour chaque i, imposent Lᵢ vrai : si Lᵢ était faux, elles couvriraient toutes les quatre possibilités d'affectation de (x4,x5) et leur conjonction serait insatisfaisable ; si Lᵢ est vrai, elles sont toutes vraies.

Une fois x₁,x₂,x₃ fixés par ce gadget, **une seule** des huit clauses de départ est fausse (celle dont les trois littéraux sont faux). Elle appartient à exactement une des deux classes de parité. La formule de cette classe est donc insatisfaisable ; celle de l'autre classe est satisfaisable. Les deux reçoivent le même gadget, donc conservent la même signature signée d'ordre 1 et 2 ; les seize clauses sont toutes distinctes et de largeur trois.

Pour n>5, ajoutons n−5 variables inutilisées. Les propriétés subsistent et n apparaît explicitement parmi les caractéristiques utilisées. **CQFD.**

**Conséquence conditionnelle :** tout décideur de SAT qui reçoit *uniquement* (n,m) et les comptes de cooccurrence signée à un ou deux littéraux doit donner la même réponse sur les deux formules, donc se tromper sur au moins une.

**Frontière de portée :** les comptes d'ordre 3 sont différents et reconstituent les clauses exactes (dans cette classe 3-CNF). Il n'existe ici aucune borne sur les algorithmes prenant la formule entière en entrée ; aucune conclusion P=NP ou P≠NP.

## Commandes de reproduction

Depuis `research/math_lab` :

```sh
python3 discovery_engine.py --n 5 --output discovery_receipt.json
python3 -m unittest discover -p 'test*.py' -v
```

Le reçu généré contient les deux formules, un témoin SAT, un arbre de réfutation UNSAT, des empreintes SHA-256 et les vérifications croisées. Tests Python standard uniquement. Le script n'utilise aucun LLM, service cloud, token ni API payante. Le vérificateur rejette notamment les certificats falsifiés, l'altération d'une polarité et une falsification du texte de la revendication.

**Exécution locale 23/11/2026 :** 31/31 tests PASS ; n=5..8 vérifiés ; n≥5 établi par l'argument universel ci-dessus. Publication scientifique ou validation Lean de cette nouvelle construction : **UNVERIFIED**. Ne pas utiliser une exécution locale comme preuve de CI GitHub.
