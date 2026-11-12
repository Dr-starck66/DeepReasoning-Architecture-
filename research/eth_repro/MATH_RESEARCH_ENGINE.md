# ASTRA MATH RESEARCH ENGINE Ω — vérification finie reproductible

Extension isolée de la PR #11 ASTRA MATH LAB Ω, sans frais, abonnement, serveur ni secret. **Ce n'est pas un solveur autonome de grands problèmes mathématiques.** La vérification porte sur une proposition FINIE et précise, extraite du programme ETH d'octobre 2026.

## Protocole

1. Énoncé explicitement borné : pour r=2, Q=3, R=2, A0=0, la matrice M0 de la construction par permutations a dimension 64 et rank_Q(I-M0)=10.
2. Reconstruction indépendante : le moteur reconstruit M0 par opérations sur bits, indépendamment de la représentation de l'ancien lowrank_exact.py.
3. Test exact : élimination rationnelle, plus deux éliminations sur les corps F_101 et F_103. Celles-ci vérifient la cohérence des résultats, **ne prouvent pas à elles seules l'égalité du rang sur Q**.
4. Falsification : altérer un coefficient de M0 donne rang(I-M0)=11 ; la fausse conjecture rank(M0)=10 est rejetée, car rank(M0)=64.
5. Réutilisation ASTRA : quand lowrank_exact.py existe à côté, chaque entrée des deux matrices (4096) est comparée en convertissant explicitement les étiquettes. Sinon : UNVERIFIED, jamais PASS d'intégration.
6. Lean : si Lean est installé, compilation locale du fichier LowRankExact.lean. **Ce fichier ne démontre pas formellement le théorème de rang global** ; statut global de preuve Lean conservé à UNVERIFIED.
7. Traçabilité : reçu JSON déterministe incluant limites, états, empreintes SHA-256 des matrices et du reçu. La signature du reçu n'est pas une attestation cryptographique tierce.

## Reproduire sans CI payante

À la racine du dépôt (branche de cette PR) :

    python3 -m unittest discover -s research/eth_repro -p 'test_math_research_engine.py' -v
    python3 research/eth_repro/math_research_engine.py --output /tmp/astra-math-receipt.json

Après exécution, vérifier dans le JSON : claim_status, integration_with_existing_astra.status et lean_source_check.status. Le premier PASS signifie validation expérimentale **sur ce cas fini**, pas découverte mathématique générale.

Pour auditer séparément les preuves CI et les blobs GitHub immuables, l'outil préexistant research/eth_repro/proof_gate.py reste la référence ; il exige une connexion réseau et des runs GitHub précis. Ce prototype ne prétend pas avoir obtenu une preuve CI pour son nouveau calcul.

## États et extensions

- PASS : calcul exact limité et contrôles de falsification exécutés en local.
- PARTIAL : pertinence pour les théorèmes du manuscrit, car la généralisation mathématique manque.
- UNVERIFIED : indépendance d'un second environnement tant qu'il n'a pas exécuté le code ; formalisation Lean du rang global ; extension à Yang–Mills ou au mass gap ; découverte automatisée ; fonctionnement permanent.
- FAIL : désaccord entre reconstructions, preuve Lean en échec, propriété fausse, ou contrôle négatif qui ne fonctionne pas.

Sources : dépôt ASTRA existant, sans copie du contenu d'OpenAI ; voir research/eth_repro/README.md. La PR est volontairement en brouillon, pour conserver une revue humaine avant tout merge.
