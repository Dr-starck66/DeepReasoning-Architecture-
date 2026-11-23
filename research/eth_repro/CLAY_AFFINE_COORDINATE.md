# Comptage exact par quotient affine

Ce calcul évalue le nombre de modèles et la même coordonnée signée
\(C_q\) que dans la [PR #19](https://github.com/Dr-starck66/DeepReasoning-Architecture-/pull/19).
Il exploite des contraintes de parité présentes dans la 3-CNF.
Le coût exponentiel dépend du rang résiduel \(r\), même lorsque le
graphe primal de la formule est complet.

## Théorème et algorithme

Partitionner les clauses non tautologiques par support de variables.
Pour un support de taille \(k\le3\), chaque clause sur ce support
interdit exactement un mot de \(\{0,1\}^k\). Si tous les
\(2^{k-1}\) mots d’une parité sont interdits, remplacer ces
clauses par l’équation qui impose l’autre parité. Si les deux
classes sont entièrement couvertes, on obtient deux équations
contradictoires. Les clauses restantes forment \(R\).
Le remplacement préserve chaque modèle, car les clauses supprimées
sont conjointement équivalentes à l’équation ajoutée.

Par élimination de Gauss sur \(\mathbb F_2\), résoudre les équations
extraites. Une contradiction donne immédiatement zéro pour les deux
sorties. Sinon écrire chaque variable \(x_i=c_i+\ell_i(y)\)
avec \(y\in\mathbb F_2^d\) et \(d\) la dimension affine.
Cette paramétrisation est bijective. Soit \(L\colon
\mathbb F_2^d\to \mathbb F_2^r\) l’application dont les lignes
forment une base de l’espace engendré par les formes \(\ell_i\)
utilisées dans \(R\). Elle est surjective et \(R\) est constant sur
chaque fibre \(L(y)=z\). Pour tout \(z\), celle-ci a \(2^{d-r}\)
éléments. Par conséquent
\[
              \#F=2^{d-r}\sum_{z\in\mathbb F_2^r}\mathbf 1[R(z)].
\]

La formule de la PR #19 exprime le poids spectral comme
\[
 W(x)=4\!\!\sum_{|I|=2}(-1)^{\sum_{i\in I}x_i}
      -4\!\!\sum_{|I|=3}(-1)^{\sum_{i\in I}x_i}.
\]
Après substitution, un terme devient \(\pm4(-1)^{h(y)}\),
où \(h=\sum_{i\in I}\ell_i\), avec le signe ajusté par
\(\sum_{i\in I}c_i\). Si \(h\) n’est pas dans l’espace des lignes
de \(L\), il existe \(v\in\ker L\) tel que \(h(v)=1\).
En effet, une forme qui s’annule sur \(\ker L\) descend en une
forme linéaire sur \(\mathbb F_2^r\), et appartient donc à cet espace.
La translation par \(v\) conserve chaque fibre et retourne le signe,
donc la somme du terme sur la fibre vaut zéro. Si \(h=t\cdot L\),
le signe est constant sur la fibre et la somme vaut \(2^{d-r}\) fois
sa valeur pour \(z\). Les deux étapes de sommation sont contrôlées
en Lean dans [AffineFiber.lean](clay_mathlib/AffineFiber.lean).

Soit \(B_t\) la somme des coefficients des termes dont la forme
linéaire est \(t\cdot L\). Il suffit donc de calculer
\[
 C_q(F)=2^{d-r}\sum_z\mathbf 1[R(z)]
                         \sum_t B_t(-1)^{t\cdot z}.
\]
La somme intérieure sur tous les \(z\) s’obtient par transformée
de Walsh–Hadamard en \(O(r2^r)\) additions et soustractions.

La construction parcourt \(O(q^3)\) termes spectraux explicites.
Les coefficients de la transformée sont bornés par
\(4(\binom{q}{2}+\binom{q}{3})\) en valeur absolue. Le facteur
\(2^{d-r}\) et l’accumulation finale demandent \(O(q+\log(q+1))\)
bits. Au total, pour une entrée de longueur \(s\) avec univers
explicite, le temps et la mémoire en bits sont
\(2^r\operatorname{poly}(s)\), indépendamment de la largeur d’arbre.
En particulier, le calcul est polynomial pour \(r=O(\log s)\).
Quand aucune parité n’est détectée, \(r\) peut atteindre \(q\).
La limite expérimentale de 16 protège les allocations. Deux
instances AIM ont \(r=50\) avec ce prétraitement et ont été refusées.

## Contrôles indépendants

- **Clique primale de taille 127.** Une variable \(x_a\) représente
  chaque \(a\in\mathbb F_2^7\setminus\{0\}\). Pour chaque triple
  \(\{a,b,a+b\}\), imposer \(x_a+x_b+x_{a+b}=0\) par quatre
  clauses strictes. Toute paire de variables figure dans une telle
  contrainte. L’élimination par seaux hérite donc d’une largeur de 126
  quel que soit l’ordre. Les solutions sont exactement les 128
  formes linéaires sur \(\mathbb F_2^7\). En effet, prolonger \(x\)
  par \(x_0=0\) donne l’additivité sur toutes les paires, les cas
  avec un zéro ou deux arguments égaux étant automatiques.
  L’oracle indépendant calcule le poids via les coefficients binomiaux
  pour chaque forme. Le nouveau code traite un seul point du quotient.
  Avec trois clauses résiduelles, il traite 16 points et retrouve
  exactement 88 modèles parmi les 128 formes.
- **Entiers de grande taille.** Avec 70 variables libres ajoutées à un
  code plus petit et des clauses résiduelles, le calcul retourne
  \(22\cdot2^{70}=25\,973\,015\,655\,783\,048\,675\,328\)
  modèles. L’oracle utilise une somme binomiale indépendante pour
  les variables libres.
- **SATLIB dubois20.** Les 160 clauses se regroupent exactement en
  40 parités. Leur somme donne \(0=1\) dans \(\mathbb F_2\), ce
  qui fournit un certificat consultable dans le JSON. CaDiCaL
  confirme le verdict. Les deux cas AIM externes restent
  vérifiés par CaDiCaL et hors de la limite de cette méthode.
- **Contrôles négatifs.** Un quartet auquel on enlève une clause
  laisse cinq modèles au lieu de quatre et reste dans les clauses
  résiduelles. Inverser une parité du code crée une contradiction
  globale. Les oracles exhaustifs vérifient 420 formules de taille
  réduite, y compris des unités, des variables libres et la
  clause vide.

L’extraction XOR et Gauss sont des méthodes établies, notamment dans
[CryptoMiniSat](https://github.com/msoos/cryptominisat). L’annulation
des caractères sur les sous-espaces relève de
[l’analyse de Fourier booléenne](https://www.cs.cmu.edu/~odonnell/papers/Analysis-of-Boolean-Functions-by-Ryan-ODonnell.pdf).
Le résultat ici est leur combinaison calculée pour le poids du filtre
ASTRA et le rang des clauses résiduelles. La priorité
bibliographique de cette formulation reste **UNVERIFIED**.

## Exécution

[Journal de vérification](clay_evidence/affine-verification.txt) et
[mesures, verdicts et certificat SATLIB](clay_evidence/affine-benchmark.json).
Les métriques sont la médiane de cinq essais et le pic des
allocations Python lors d’un essai distinct.

Depuis la racine du dépôt, lancer
python3 -m unittest discover -s research/eth_repro -v.
Dans le projet Mathlib v4.23.0 préparé comme pour la PR #19,
lancer lake env lean avec le chemin absolu de
research/eth_repro/clay_mathlib/AffineFiber.lean.
Pour le benchmark, lancer python3 research/eth_repro/benchmark_clay_affine_coordinate.py
avec --output, et facultativement --dimacs suivi des fichiers SATLIB.
Le contrôle externe utilise PySAT 1.8.dev24 et reprend les fichiers
SATLIB et CaDiCaL de la PR #19.

Le statut de P versus NP reste **ouvert**. La preuve de complexité porte
sur une structure calculable de l’entrée et la borne dépend de son rang.
