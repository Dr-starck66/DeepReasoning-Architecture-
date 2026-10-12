# UNIVERSAL SKILLS Ω — plan d'adoption exhaustif, projet par projet

Ce module vérifie **chaque dépôt GitHub public de Dr-starck66**, et en découvrira de nouveaux automatiquement, même s'ils ont été créés après l'installation initiale.

À chaque cycle :
1. Obtenir la liste paginée des dépôts **publics** depuis l'API GitHub (jusqu'à 1 000 entrées ou un échec explicite).
2. Associer une catégorie de compétences, en précisant que cette classification est heuristique et nécessite revue.
3. Interroger l'arbre Git de la branche par défaut de **chaque dépôt**. Enregistrer la preuve : SHA, arbre tronqué ou complet, nombre de fichiers, présence de tests, de workflows CI et de manifestes de build.
4. Présenter la **prochaine action par projet**. Ne jamais confondre « présence de test » et « test exécuté », « source présente » et « site déployé », « skill conseillé » et « skill adopté ».
5. Publier les résultats individuels dans [FLEET.md](./FLEET.md) et [reports/fleet.json](./reports/fleet.json).

Ce contrôle n'exécute aucun code provenant des dépôts audités, n'installe pas de dépendance tierce et n'impose aucun abonnement payant. Il utilise les minutes gratuites prévues par GitHub pour dépôts publics, sous réserve des limites d'usage du compte.

**Projets privés :** leur registre séparé existe sur `Dr-starck66/indexation` (PR #38), mais leurs GitHub Actions n'ont actuellement aucun runner. Aucun nom ni fichier privé ne doit être envoyé au catalogue public. Les initiatives sans GitHub (dont WINE ELSE) y restent inscrites et doivent être validées par preuves spécifiques à leur domaine (contacts réels, documents/logistique, accords, etc.). Aucune promesse d'exécution automatique sur leurs comptes externes non connectés.

**Projets passés :** les dépôts encore accessibles via GitHub sont couverts. Les anciens projets sans dépôt accessible ou intégration connectée restent à inventorier ; ils ne sont pas revendiqués comme audités.

**Projets futurs :** nouveau dépôt public = détection automatique au prochain passage programmé ; nouveau dépôt privé ou initiative non-code = ajout au registre privé sans divulgation.

Statuts : PASS = preuve du périmètre exact (arbre Git), PARTIAL = preuve tronquée, UNVERIFIED = preuve inaccessible, FAIL = contrôle effectivement échoué. Une recommandation reste REVIEW_REQUIRED jusqu'à audit de licence/sécurité et démonstration de valeur sur le projet.
