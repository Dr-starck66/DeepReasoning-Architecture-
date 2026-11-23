# Complexité exacte d’une coordonnée des projecteurs de swaps

## Théorème

Soient \(E_q=4P_{(2)}-4P_{(3)}\) le filtre de la
[PR #17](https://github.com/Dr-starck66/DeepReasoning-Architecture-/pull/17) sur
\(q\) couples de bits, \(T_q=2^qE_q\) et \(v_F(a,d)=\mathbf 1[F(a)]\)
pour une 3-CNF \(F\) qui utilise seulement le registre \(a\). On étudie
\(C_q(F)=(T_qv_F)(0^q,1^q)\). La coordonnée est fixée dès que \(q\) est donné.
L’entrée représente les \(q\) variables explicitement ou fournit \(q\) en unaire.

**Pour toutes 3-CNF \(A,B\)**, une transformation déterministe en temps
polynomial construit un \(q\) pair et une 3-CNF \(G\) à exactement trois
variables distinctes par clause tels que
\[
                  C_q(G)=2q(\#A-\#B).
\]
L’évaluation entière est GapP-complète sous réductions métriques.
Le test de zéro est \(\mathrm C_{=}\mathrm P\)-complet, le test de non-zéro
est \(\mathrm{co}\text{-}\mathrm C_{=}\mathrm P\)-complet et le test de
positivité est PP-complet, sous réductions polynomiales many-one.
Ces conclusions valent déjà pour les 3-CNF strictes. En particulier,
une évaluation exacte en temps polynomial donnerait un algorithme
polynomial pour 3-SAT. C’est une classification de cette représentation
succincte. La réduction change la formule avant d’appliquer le filtre
et le contre-exemple à l’encodage brut de la PR #17 conserve sa portée.

## Preuve

### Coefficient d’un masque de swaps

À la coordonnée \((0^q,1^q)\), chaque masque de swaps donne une affectation
distincte \(z\in\{0,1\}^q\) dans le registre \(a\). Posons
\(s_i=(-1)^{z_i}\), \(s=\sum_i s_i\) et \(e_k=[X^k]\prod_i(1+s_iX)\).
Dans le terme du projecteur où les facteurs antisymétriques forment \(I\),
l’expansion de \((I-S_i)\) donne un signe \(s_i\) pour chaque \(i\in I\),
et \((I+S_i)\) donne un coefficient \(1\) ailleurs. Le facteur \(2^q\)
compense les dénominateurs. Ainsi le poids correspondant de \(T_q\) vaut
\(W_q(z)=4(e_2-e_3)\) et
\[
                 C_q(F)=\sum_z\mathbf 1[F(z)]W_q(z).
\]
Les identités de Newton, ou une induction sur le produit, donnent
\[
          2e_2=s^2-q,\qquad 6e_3=s^3-(3q-2)s.
\]
En effet \(s_i^2=1\) et \(s_i^3=s_i\). Pour \(s=0\), \(W_q=-2q\).
Pour \(s=2\), \(W_q=2q\). Les \(e_k\) sont les coefficients binaires de
Krawtchouk correspondants.

### Réduction à extensions uniques

1. Renommer les variables de \(A,B\) de façon disjointe et introduire un
   sélecteur \(b\). Pour \(b=0\), imposer \(A\) et fixer les variables de
   \(B\) à zéro. Pour \(b=1\), imposer \(B\) et fixer celles de \(A\) à zéro.
   On garde les clauses de \(A\) par \(b\) et celles de \(B\) par \(\neg b\).
   Pour une clause de largeur trois, une variable fraîche \(t\) reçoit
   la valeur \(t=\ell_1\lor\ell_2\), imposée par trois clauses.
   La clause gardée utilise le garde, \(t\) et \(\ell_3\). La valeur de
   \(t\) est unique même hors de la branche active. Les littéraux répétés
   et les tautologies peuvent être éliminés avant d’insérer les gardes.
   Les variables explicitement déclarées et libres restent comptées.
2. Introduire trois variables de remplissage contraintes à 000 en
   interdisant chacune des sept autres affectations par une clause de
   largeur trois. Compléter chaque clause courte avec des variables de
   remplissage distinctes et absentes, prises positivement. Ce
   remplissage préserve le nombre de solutions, y compris si une
   formule source contient la clause vide ou la conjonction vide.
3. Introduire \(c=0\). Pour chaque variable \(u\) autre que \(b,c\),
   imposer une copie complémentaire \(u'\) avec
   \((u\lor u')\land(\neg u\lor\neg u')\). Compléter les clauses courtes
   de ce gadget et de la fixation de \(c\) comme à l’étape précédente.

Chaque couple complémentaire contribue zéro à \(s\).
Les variables \(c,b\) donnent \(s=2\) lorsque \(b=0\), et \(s=0\) lorsque
\(b=1\). Il y a \(q=2r+2\) variables pour \(r\) couples. La projection sur
les variables actives est une bijection entre les modèles de chaque
branche et ceux de la formule source. La somme des deux contributions
donne l’identité. Pour \(n\) variables et \(m\) clauses sources de largeur
au plus trois, la sortie a \(O(n+m)\) variables et clauses. Sa taille en
bits est \(O((1+n+m)\log(2+n+m))\) après renumérotation.

### Appartenance et complétude

Chaque \(W_q(z)\) est calculable en temps polynomial et
\(\lvert W_q(z)\rvert\le4(\binom q2+\binom q3)\).
Pour construire une fonction #P, deviner \(z\) puis un entier \(j\)
sur suffisamment de bits. Accepter si \(F(z)\) et si
\(0\le j<\max(W_q(z),0)\). Avec \(\max(-W_q(z),0)\) on obtient une
deuxième fonction #P. Leur différence est \(C_q\), qui appartient donc à
GapP. Toute différence de deux fonctions #P se ramène à une différence
de comptes #3-SAT par deux réductions parcimonieuses. Pour cela, encoder
les vérificateurs par des circuits puis appliquer Tseitin avec extension
unique des valeurs des portes. La construction suivie de la division
entière par \(2q\) donne la réduction métrique. Le facteur \(2q>0\)
préserve le signe et le zéro. Les caractérisations de GapP donnent les
trois classifications décisionnelles. Le cas \(B=\bot\) donne
directement la réduction de 3-SAT.

## Algorithmes exacts à partir de la formule

**Élimination de variables.** Calcul dans
\(\mathbb Z[X]/(X^4)\) de
\(\sum_z\mathbf1[F(z)]\prod_i(1+(-1)^{z_i}X)\).
Chaque clause est un facteur local à valeurs 0 ou 1. Pour éliminer
\(z_i\), multiplier les facteurs de son seau, puis sommer les
spécialisations après multiplication par \(1\pm X\).
La distributivité justifie l’invariant sur les affectations partielles.
Chaque facteur créé est consommé une seule fois, donc les ensembles de
variables éliminées sont disjoints dans chaque produit. Les valeurs de
chaque coefficient intermédiaire sont bornées en valeur absolue par
\(2^q\sum_{j=0}^3\binom qj\), soit \(O(q+\log(q+1))\) bits.

Pour un ordre donné de largeur induite \(w\) du graphe primal, chaque seau
traite au plus \(2^{w+1}\) lignes. Il suffit de traiter \(O(q+m)\) facteurs
en comptant la création et la consommation de chaque facteur. Le calcul
des indices et l’arithmétique par ligne ont un coût polynomial en bits.
Temps et mémoire sont \(2^{w+1}\operatorname{poly}(q+m)\) en bits.
Si un ordre de largeur \(O(\log(q+m))\) est fourni ou calculable en temps
polynomial, le calcul est polynomial. Un graphe primal complet impose
\(2^q\) lignes parcourues au premier seau de cette implémentation, quel
que soit l’ordre. Cette borne concerne ce modèle d’élimination.

**Moments par comptage de modèles.** Développer
\(\prod_{i\in I}(1-2z_i)\) et grouper par \(J\subseteq I\). On obtient
\[
C_q(F)=4\sum_{j=0}^3(-2)^j
\left(\binom{q-j}{2-j}-\binom{q-j}{3-j}\right)
\sum_{|J|=j}\#\left(F\land\bigwedge_{i\in J}z_i\right).
\]
On omet \(j>q\) et les coefficients binomiaux hors plage sont nuls.
Il y a \(O(q^3)\) appels #SAT sur les mêmes \(q\) variables, avec au
plus trois unités de plus par formule. Les comptes et l’accumulateur
occupent \(O(q+\log(q+1))\) bits. Les cas à zéro ou un modèle
permettent un raccourci. Cette formule transporte les bornes de #3-SAT
à la coordonnée avec un facteur polynomial. La réduction inverse peut
ajouter \(O(n+m)\) variables et n’a pas ce caractère fin.

## Portée et comparaisons

- [Krawtchouk](https://dlmf.nist.gov/18.23) et les classes de
  [Fenner, Fortnow et Kurtz](https://doi.org/10.1006/jcss.1994.1026)
  fournissent les outils connus. Le résultat propre à ASTRA est la
  réduction à sa coordonnée fixe avec une 3-CNF stricte et une
  construction en taille quasi linéaire en incidences.
  La priorité bibliographique est **UNVERIFIED**.
- La méthode par largeur relève des mêmes techniques de décomposition
  que [Samer et Szeider](https://arxiv.org/abs/cs/0610174) pour #SAT et
  [Markov et Shi](https://arxiv.org/abs/quant-ph/0511069) pour les
  réseaux de tenseurs. Le benchmark compare des méthodes évaluant la
  même coordonnée à la même précision lorsqu’elles sont exécutées.
- Le calcul dans \(\mathbb Z[X]/(X^4)\) est un cas particulier du
  [comptage algébrique de modèles](https://arxiv.org/abs/1211.4475).
  [SOSA 2026](https://epubs.siam.org/doi/10.1137/1.9781611978964.19)
  donne une autre réduction, de #SAT vers #2-SAT pondéré par \(\pm1\),
  qui débouche sur une borne en largeur d’arbre d’incidence. La borne
  obtenue ici porte sur la largeur primale et sur cette sortie spectrale.
  La [compétition MC 2026](https://mccompetition.org/2026/mc_description)
  donne des références contemporaines pour les poids négatifs et
  l’AMC. Les mesures ASTRA ne comparent pas ces solveurs de compétition.
- Le [préprint du 25 octobre 2026](https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026)
  annonce pour #\(k\)-SAT à \(k\) fixé un temps
  \((n+m)^{O_k(1)}2^{n/(\log n)^{1/2+o(1)}}\) et un espace polynomial.
  La réduction par moments transfère la borne annoncée. Le préprint
  lui-même reste hors du périmètre de validation.
- Pour **P = NP**, un test polynomial de positivité sur les instances
  construites avec \(B=\bot\) suffirait. Une approximation avec erreur
  absolue certifiée \(<q\) sur \(C_q(G)\) suffirait aussi. Pour la
  coordonnée rationnelle de \(E_q\), cette précision devient \(<q/2^q\).
- Pour **P ≠ NP**, le premier seau de largeur maximale exclut un coût
  polynomial général pour cette implémentation. Une borne contre tous
  les algorithmes reste ouverte. [Baker, Gill et Solovay](https://doi.org/10.1137/0204037)
  exhibent les deux réponses dans des mondes relativisés.
  Les [preuves naturelles](https://doi.org/10.1006/jcss.1997.1494)
  délimitent certaines techniques de bornes de circuits sous hypothèse
  cryptographique. [Aaronson et Wigderson](https://www.scottaaronson.com/papers/alg.pdf)
  ajoutent la barrière d’algébrisation. Les bornes de
  [Williams pour ACC](https://doi.org/10.1145/2559903) concernent une
  classe de circuits restreinte. Les [travaux récents sur les méthodes
  de bornes algébriques](https://arxiv.org/abs/2610.33938) portent sur
  des énoncés distincts. Aucun contournement général de ces barrières
  n’est prouvé ici.

**Prix Clay, FAIL à ce stade.** [P versus NP](https://www.claymath.org/millennium/p-vs-np/)
reste ouvert. Le [règlement](https://www.claymath.org/millennium-problems/rules/)
exige une solution complète, une publication admissible, deux ans
écoulés depuis cette publication et l’acceptation générale de la
communauté mathématique. Aucune démarche de soumission n’a été engagée.

## Reproduction et journal

- **PASS** avec Lean 4.23.0 et Mathlib v4.23.0 (commit
  37df177aaa770670452312393d4e84aaad56e7b6).
  [SwapCoordinateMatrix.lean](clay_mathlib/SwapCoordinateMatrix.lean)
  établit pour tout \(q\) l’action de la matrice historique sur
  cette ligne et l’annulation hors de l’orbite.
  [SwapCoordinate.lean](clay_mathlib/SwapCoordinate.lean) établit les
  identités des moments, les poids des deux classes, la somme signée et
  les gadgets locaux. La bijection globale de la construction CNF et
  la classification GapP sont démontrées dans le texte.
- **PASS** 120 tests Python dont 8 nouveaux. Les nouveaux tests
  comprennent 240 CNF et ordres tirés avec graine fixe, 60 paires
  aléatoires pour la réduction, 60 comparaisons avec le projecteur
  historique, un contrôle exact d’annulation et un contrôle de largeur.
  Lors du premier essai, un signe erroné dans l’oracle binomial a produit
  un échec. Le croisement avec le projecteur existant a permis de corriger
  l’oracle. Le premier essai du raccord Lean a aussi échoué sur des
  obligations de réécriture et a été corrigé avant la validation finale.
- **PASS** 12 cas de [benchmark](clay_evidence/benchmark.json), dont trois
  instances SATLIB vérifiées indépendamment avec CaDiCaL 1.9.5
  (PySAT 1.8.dev24), par recherche puis blocage du premier modèle.
  AIM SAT (50 variables, un modèle) donne \(-420\) sur la formule brute,
  puis \(536=2\times268\) une fois réduite contre \(\bot\).
  AIM UNSAT et Dubois UNSAT donnent zéro après réduction. Les largeurs externes sont celles des ordres min-fill choisis. Les deux AIM déclenchent le plafond
  expérimental de largeur 12. Sur les chemins et cliques, un comptage
  combinatoire indépendant confirme la coordonnée jusqu’à 64 variables.
  La mémoire enregistrée est le pic des allocations Python, ce qui
  exclut les allocations natives de CaDiCaL.
- [Journal intégral](clay_evidence/verification.txt) et
  [script de reproduction](reproduce_clay_swaps.sh). Depuis la racine,
  préparer le projet Lake sous mathlib_rank comme le fait le
  workflow historique (lake update et lake exe cache get), puis
  exécuter bash research/eth_repro/reproduce_clay_swaps.sh.
  Le script accepte aussi le chemin d’un projet Mathlib v4.23.0
  déjà préparé. Les preuves précédentes restent des dépendances.
- Pour le benchmark, installer python-sat==1.8.dev24 dans un
  environnement jetable. Télécharger et extraire les fichiers
  aim-50-1_6-yes1-1.cnf, aim-50-1_6-no-1.cnf et dubois20.cnf depuis
  les archives [AIM](https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/AIM/aim.tar.gz)
  et [Dubois](https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/DUBOIS/dubois.tar.gz).
  Exécuter python3 research/eth_repro/benchmark_clay_swap_coordinate.py
  avec --dimacs suivi des trois chemins, puis --output suivi d’un chemin
  JSON. Les empreintes des instances figurent dans le résultat.
