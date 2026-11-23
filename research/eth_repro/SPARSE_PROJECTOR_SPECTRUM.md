# ASTRA Ω — Projection spectrale à rang relatif asymptotiquement nul

**Objet :** prolonger la matrice exacte q=3 de la PR #15 sans réutiliser
l'extension q>=4 de la PR #16, qui devient presque de rang plein.

## Construction mathématique (déduite, pas revendiquée nouvelle)

Sur Q^(4^q), chaque swap S_i permute les bits a_i et d_i.
Les swaps S_i sont des involutions commutatives. Les projecteurs locaux

    P_i^+ = (I+S_i)/2
    P_i^- = (I-S_i)/2

sont idempotents et complémentaires. Les sous-espaces simultanés associés
à exactement k signes «−» ont dimension C(q,k) * 3^(q-k).
Notons P_(k) leur projecteur spectral global (somme des produits tensoriels
des P_i^-/P_j^+, avec exactement k facteurs P^-).

Définissons l'**autre famille**, explicitement différente de la PR #16 :

    E_q = 4 P_(2) - 4 P_(3)
    T_q = 2^q E_q.

Dans le calcul, T_q est un polynôme à coefficients **entiers** des
permutations S_mask. Aucune matrice rationnelle dense n'est nécessaire.
Sur une base propre commune, E_q vaut :

    k=2 : +4
    k=3 : -4
    sinon : 0.

Pour q=3, cette construction satisfait EXACTEMENT E_3 = I-M_3 du modèle
ASTRA historique, pas seulement une égalité des rangs. Le fichier Lean
ProjectorSpectrum.lean vérifie la version entière T_3 = 8(I-M_3)
sur les 4096 entrées (si le CI est PASS).

## Rang (dérivation analytique par diagonalisation tensorielle)

    r(q) = C(q,2)3^(q-2) + C(q,3)3^(q-3),

avec les termes de degré impossible omis. Le rapport

    r(q)/4^q = C(q,2)/16 * (3/4)^(q-2)
             + C(q,3)/64 * (3/4)^(q-3)

tend vers zéro lorsque q tend vers l'infini. Cette famille permet donc
de **préserver le cas q=3** tout en ayant un rang relatif asymptotiquement
faible, contrairement à A_q (PR #16), dont la fraction de rang tend vers 1.

| q | dimension 4^q | rang E_q | part du rang |
|---|---:|---:|---:|
| 1 | 4 | 0 | 0 % |
| 2 | 16 | 1 | 6.25 % |
| 3 | 64 | 10 | 15.625 % |
| 4 | 256 | 66 | 25.78125 % |
| 5 | 1024 | 360 | 35.15625 % |
| 6 | 4096 | 1755 | ~42.85 % |
| 9 | 262144 | 139968 | ~53.39 % |
| 10 | 1048576 | 557685 | ~53.18 % |
| 20 | 1099511627776 | 220829678730 | ~20.08 % |
| 30 | 1152921504606846976 | 40911330506955255 | ~3.55 % |
| 40 | 1208925819614629174706176 | 5502469329987987775860 | ~0.455 % |

**Contrôle négatif important :** la proportion de rang n'est pas
monotone pour les petites valeurs de q. Elle augmente jusqu'aux alentours
de q=9 ; une économie immédiate à q=4,5 ne doit pas être exagérée.

## Contrôles exacts, réutilisant la CI déjà installée

    python3 -m unittest discover -s research/eth_repro -p 'test_projected_spectrum.py' -v
    python3 research/eth_repro/projected_spectrum.py --output /tmp/astra_projector.json

Au sein du workflow existant .github/workflows/astra-spectral.yml :
- compilation Lean 4 des identités scalaires de projecteur pour des listes
  de signes de longueur arbitraire ;
- vérification Lean *indépendante* de T_3 = 8(I-M_3) sur 64×64 cases ;
- 69 904 équations entières des vecteurs propres q=1..4 ;
- rangs indépendants modulo 101 et 103 pour q=1..4 ;
- comparaison des 4096 coefficients avec le modèle ASTRA historique ;
- q=5, sondage de vecteurs propres seulement, non exhaustif ;
- refus des déclarations inventées de rang, de valeur propre, et
  d'identité entre l'ancien A_4 et le nouveau E_4 ;
- reçu JSON SHA-256 reproductible.

Les sorties CI font foi : le code écrit **ne** suffit **pas** à
obtenir PASS avant exécution réelle.

## Frontières scientifiques et risques

- **Non démontré par Lean uniformément :** le théorème Mathlib
  Matrix.rank(E_q)=r(q) pour tout q. Il faut formaliser la décomposition
  tensorielle et le comptage binomial général.
- **Non démontré :** accélération réelle d'un calcul. L'application naïve
  de T_q avec 2^q termes de permutation coûte O(8^q), contre O(q*4^q)
  pour la famille A_q originale. Un rang relatif faible ne signifie donc
  PAS qu'un calcul concret est plus rapide, ni qu'un stockage dense est évité.
  Une factorisation matricielle structurée et des benchmarks seraient requis.
- Cette construction est une manipulation classique de projecteurs
  d'involutions commutatives ; ne pas annoncer une invention ou un brevet.
- Aucune mesure de matériel quantique, aucun avantage algorithmique
  général, aucune généralisation à d'autres problèmes n'est prouvée.
- PR empilée, isolée de main ; pas de nouveau workflow, hébergement
  payant, promotion ni déploiement public.
