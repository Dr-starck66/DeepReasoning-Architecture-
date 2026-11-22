# ASTRA Ω — Certificat spectral indépendant (rang 10)

Ce module réutilise le modèle Q=3 / R=2 du dépôt ASTRA Math Research Engine.
Il apporte un **second chemin de vérification** qui ne calcule pas le rang
de I−M0 par élimination de Gauss. Python standard uniquement, coût nul.

## Énoncé mathématique **fini**

Sur trois paires de bits (a_i,d_i), S_i est la permutation des deux bits,
agissant sur un espace rationnel de dimension 4 par paire. Les trois S_i
commutent et vérifient S_i²=I. Posons

    M0 = S2*S3 + S1*S3 + S1*S2 - 2*S1*S2*S3.

Le certificat traite cette matrice exacte de dimension 64, et aucune famille
asymptotique. Pour chaque paire, l'opérateur swap possède trois vecteurs
propres indépendants de valeur propre +1 et un de valeur propre -1.
La matrice de passage locale entière B a déterminant -2. La base tensorielle
B⊗B⊗B est donc inversible sur Q; son déterminant vaut (-2)^48.

Si k facteurs ont la valeur propre -1, M0 a la valeur propre

    mu(k) = (-1)^k * (1-2k).

La valeur propre de I−M0 est 1−mu(k), avec multiplicité C(3,k)*3^(3-k).
Les quatre classes sont donc :

| k | valeur propre de I−M0 | multiplicité |
|---|---:|---:|
| 0 | 0 | 27 |
| 1 | 0 | 27 |
| 2 | 4 | 9 |
| 3 | -4 | 1 |

D'où, pour CETTE matrice, rang_Q(I−M0)=9+1=10.

## Audits exécutables

Depuis la racine du dépôt, sur cette branche :

    python3 -m unittest discover -s research/eth_repro -p 'test_spectral_certificate.py' -v
    python3 research/eth_repro/spectral_certificate.py --output /tmp/astra_spectral_receipt.json

Le moteur vérifie 64 vecteurs propres et 4096 équations entières.
Il compare aussi ses 4096 coefficients avec le module existant
math_research_engine.construct_matrix() si présent.
Les contrôles négatifs remplacent intentionnellement une entrée de matrice
et une valeur propre correcte par une valeur fausse ; ils doivent échouer.

## Discipline de preuve

- La décomposition fournit un argument mathématique exact dans ce modèle
  fini. Le programme en vérifie toutes les égalités composantes par composantes.
- Le test Python local ne constitue **pas** une certification du noyau Lean.
  Le champ formal_Lean_kernel_verification demeure UNVERIFIED.
- La comparaison avec le vrai module ASTRA demeure UNVERIFIED tant que
  les tests n'ont pas été exécutés dans un checkout complet.
- Aucune accélération algorithmique asymptotique, avantage quantique,
  découverte physique, théorème général de rang, brevetabilité ou déploiement
  n'est démontré.
- Aucun merge sur main ni déclenchement permanent n'est réalisé.

L'objectif de la branche est de rapprocher découverte symbolique, contrôle
numérique exact, falsification et traçabilité, sans remplacer le ProofGate
existant ni déclarer un PASS à partir d'un simple hash.
