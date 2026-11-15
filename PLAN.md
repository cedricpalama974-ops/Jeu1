# Plan de production — Atlas 3D de l'anatomie du porc (version haute définition)

Statut : **proposition, en attente de validation**. Rien n'est produit avant votre accord.

---

## 0. Points bloquants à régler d'abord

| # | Point | Ce qu'il me faut |
|---|---|---|
| B1 | **Le dossier `src/` n'est pas dans le dépôt.** La branche ne contient que `index.html` et `README.md` du jeu Néo-Kairos. Aucun `engine.js`, `anatomy.js`, `render.js`, `app.js`, `template.html`, `build.py`. | Déposer `src/` dans le dépôt (ou me donner la branche où il se trouve). Sans lui, je ne peux reprendre ni l'interface, ni les 47 muscles, ni les textes. |
| B2 | **Réseau de la session limité** : seuls GitHub et les dépôts de paquets (PyPI, npm) répondent. Zenodo, MorphoSource, DigiMorph, Sketchfab, NCBI/PMC, CGTrader sont bloqués. | Accord pour que je demande l'ouverture de ces domaines précis (une fenêtre d'autorisation s'affichera, rien ne change sans vous). |
| B3 | **Choix de la source principale** (voir § 2 : gratuit fait main ou modèle payant à 200 $). | Votre décision. |

Blender est disponible (module Python `bpy` 5.x installable par PyPI) : la chaîne de production est réalisable dans ce conteneur.

---

## 1. Ce qui est réaliste, dit franchement

- **Sculpture.** Je travaille uniquement par scripts : pas de main sur une tablette graphique. Je peux produire des formes organiques (maillages de base sculptés par déformations guidées, subdivision, displacement, remesh voxel, lissage, retopologie), mais je ne peux pas atteindre seul le niveau d'un sculpteur anatomiste humain sur 250 pièces. La qualité dépendra surtout de la **qualité des données de départ** (scanners ou modèle existant).
- **Os.** Des scanners de porc existent en libre accès par os isolés (humérus, tibia, crâne…), rarement un squelette complet sous licence ouverte. Les 44 dents, 8 os du carpe, sutures et foramens : réalisables si la source est un scanner ou un modèle détaillé ; sinon modélisés à la main d'après planches, avec un niveau « manuel de dissection », pas « micro-scanner ».
- **Muscles.** Je n'ai trouvé **aucun jeu de données ouvert de muscles de porc segmentés individuellement**. Sans le modèle payant, les muscles seront construits par moi : chaque muscle comme volume entre ses insertions réelles sur les os, déformé pour respecter les sections anatomiques, avec carte de normales des fibres orientée selon leur direction. Résultat lisible et juste en topographie, mais moins fin qu'un modèle d'artiste.
- **Morceaux par booléens.** Réalisable : découpe du volume complet (peau + gras + muscles + os) par plans et volumes de coupe, faces de coupe texturées par projection (os scié, noix, gras intermusculaire, bardière, couenne).
- **25 Mo.** Tenable avec compression meshopt + textures KTX2 (Basis), 2K pour les pièces principales, atlas partagés pour les petites pièces. Les 2K partout dépasseraient le budget : je propose 2K pour peau, morceaux et grands muscles, 1K pour os et petits muscles, partagés par familles.

---

## 2. Sources

### Recherche faite à ce jour (moteur de recherche seulement, pages non ouvertes faute de réseau)

| Source | Contenu | Licence | Verdict provisoire |
|---|---|---|---|
| [DigiMorph — Sus scrofa crâne](http://www.digimorph.org/specimens/Sus_scrofa/skull/) | Crâne de sanglier, scanner CT | À vérifier (usage éducatif généralement autorisé avec citation) | Référence de forme du crâne ; réutilisation directe seulement si licence claire |
| [DigiMorph — Sus scrofa genou](http://www.digimorph.org/specimens/Sus_scrofa/knee/) | Genou, CT + IRM, os du membre pelvien segmentés | À vérifier | Idem |
| [Sketchfab — tibia de porc](https://sketchfab.com/3d-models/pig-tibia-eoa2022903-8eacf4497825434a8260701a35596a46) | Un os, photogrammétrie | CC BY (annoncé) | Utilisable après vérification |
| [Sketchfab — humérus](https://sketchfab.com/3d-models/pig-humerus-vcu-3d-2787-0b547fc87b67488fa59040204c6335af), [métacarpien III](https://www.sketchfab.com/3d-models/pig-metacarpal-3-vcu-3d-2744-5914407319c8487e9caa4f27e0f7a9fe) (VCU) | Os isolés | CC BY-NC-ND | **Exclu** (pas de modification autorisée) — référence visuelle seulement |
| [Sketchfab — pig carcass](https://sketchfab.com/3d-models/pig-carcass-5c73c8653a584dee9ebb6d2956416afe) | Carcasse de boucherie | CC BY (annoncé) | Référence de silhouette de carcasse, à vérifier |
| [Article : identification automatique des os et articulations sur CT corps entier de porcs](https://www.researchgate.net/publication/399060483_Automated_identification_of_bones_and_joints_in_whole-body_CT-scan_images_of_pigs) | 201 porcs scannés, segmentation os/muscles/organes | Annoncé CC BY-NC 4.0 ; lien de données ambigu dans les résultats | Piste la plus prometteuse pour le squelette entier. **NC = non commercial** : acceptable pour une formation gratuite, pas si vous vendez l'outil ou la formation. À vérifier. |
| MorphoSource | Collections CT de mammifères | Licence par fiche | À explorer une fois le réseau ouvert |
| Atlas de référence (textes, non réutilisés en 3D) | Barone *Anatomie comparée des mammifères domestiques* ; Popesko ; Nickel-Schummer-Seiferle ; Sisson & Grossman ; Nomina Anatomica Veterinaria (NAV, ICVGAN, libre) ; IFIP (découpe française) ; Norma de calidad del cerdo ibérico (RD 4/2014) | Citées comme sources, pas copiées | Pour vérifier les correspondances morceau ↔ muscle ↔ os |

### Option payante (aucun achat sans votre accord)

| Modèle | Prix | Contenu annoncé | Licence | Mon avis |
|---|---|---|---|---|
| [CGTrader — *Full Male Pig Anatomy System*](https://www.cgtrader.com/3d-models/character/human-anatomy/full-male-pig-anatomy-system) | **200 $** | Squelette, muscles, organes, vaisseaux, nerfs ; textures squelette 4K | Licence royalty-free CGTrader standard (à confirmer sur la fiche) : utilisation dans un produit autorisée, **revente ou mise à disposition des fichiers bruts interdite**. Un site web qui sert des GLB est en zone grise : il faut une protection minimale (fichiers optimisés, non reconstructibles en source) — à vérifier sur la fiche avant achat. | **Nettement meilleur** que ce que je peux modéliser seul pour les muscles. C'est l'option qui garantit le critère « un boucher reconnaît chaque muscle ». Je n'ai pas pu ouvrir la fiche (réseau) : nombre de muscles séparés, polygones, formats à confirmer. |
| [TurboSquid — *Pig (Animated)*](https://www.turbosquid.com/3d-models/pig-animated-1850875) | 999 $ | Squelette et muscles riggés | Licence standard TurboSquid | Trop cher pour le gain ; déconseillé. |

**Ma recommandation :** ouvrir le réseau, vérifier la fiche CGTrader et le jeu CT. Si le modèle à 200 $ a bien des muscles séparés et une licence compatible web, c'est le meilleur rapport qualité/coût. Sinon, chaîne entièrement libre (CT pour les os quand disponible + modélisation guidée pour le reste), en acceptant un niveau de muscles plus « planche de manuel ».

Tout ce qui est retenu sera consigné dans `SOURCES.md` (URL, auteur, licence, date de vérification, modifications faites).

---

## 3. Chaîne de production

```
sources (CT .nrrd/.stl, modèles .glb/.fbx, ou maillages de base)
   │  tools/import/        nettoyage, remise au repère X→groin, Y→haut, Z→gauche, cm
   ▼
Blender headless (bpy)  tools/blender/*.py
   │  1. remesh voxel → sculpture procédurale (déformations guidées par repères anatomiques)
   │  2. retopologie quad (QuadriFlow) → maillage bas (LOD1) et moyen (LOD0)
   │  3. dépliage UV, cuisson normal map + AO depuis le haut-poly, textures albédo/rugosité
   │  4. booléens de découpe → morceaux + faces de coupe texturées
   │  5. rendus de contrôle (Cycles/EEVEE, 6 angles) → docs/controle/etape-N/
   ▼
export glTF  →  gltfpack (meshopt + KTX2)  →  public/models/{lod-bas,lod-haut}/*.glb
   ▼
build.py (repris)  →  site statique three.js + service worker (hors ligne)
```

- **Moteur :** three.js r16x (versions figées), `GLTFLoader` + `MeshoptDecoder` + `KTX2Loader`, ombres douces (PCFSoft), SSAO léger désactivé automatiquement sur téléphone faible.
- **Chargement progressif :** un GLB « silhouette » < 1,5 Mo affiché tout de suite, puis chargement par couche et par mode (on ne charge pas les morceaux si l'utilisateur reste en mode Os).
- **Données :** `anatomy.js` reste la source des textes ; chaque pièce 3D porte un identifiant (`os.femur.g`, `m.longissimus`, `fr.jambon.noix`, `ib.presa`) relié à sa fiche.
- **Validation :** script de contrôle automatique (toutes les fiches ont un maillage et inversement, comptage vertèbres/côtes/dents, poids total < 25 Mo).

---

## 4. Étapes livrables

| Étape | Contenu | Livrable de contrôle |
|---|---|---|
| **0. Reprise** | Récupérer `src/`, faire tourner la maquette actuelle, brancher le chargeur glTF à la place du moteur procédural sans rien changer à l'interface. Inventaire des 47 muscles. | Maquette identique fonctionnant avec un GLB de test. Liste des corrections anatomiques proposées sur `anatomy.js`. |
| **1. Squelette** | Crâne (sutures, foramens, 44 dents séparées), 7 C + 14 T + 6 L + sacrum 4 soudées + 20 caudales, 14 paires de côtes, sternum 6 sternèbres, membres complets (carpe 8 os, doigts II–V à 3 phalanges, tarse). | Rendus 6 angles + vues de détail (crâne, carpe, tarse, vertèbre type) mis à côté de planches de référence. |
| **2. Muscles** | Les 47 muscles de `anatomy.js` + compléments (≈ 90–110 au total : peauciers, muscles de la tête, de l'avant-bras et de la jambe, intercostaux, diaphragme, muscles du cou profonds…), tendons et aponévroses (fascia thoraco-lombaire, tendon calcanéen…). Classement superficiel / moyen / profond. | Rendus par couche, vues latérale, dorsale, ventrale, médiale (demi-carcasse). |
| **3. Peau et gras** | Porc charcutier ≈ 110 kg (silhouette type Large White × Piétrain), groin, oreilles, onglons, 12–14 tétines, plis du cou ; gras de couverture d'épaisseur variable (bardière dorsale ≈ 1,5–2,5 cm au P2). | Rendus face, profil, trois-quarts ; coupe transversale au niveau de la dernière côte. |
| **4. Morceaux** | Découpe française (liste complète du cahier des charges, jambon en 4 muscles) et ibérique (16 pièces), par booléens sur l'animal complet, faces de coupe texturées. Demi-carcasse, vue éclatée, os sous les morceaux. | Rendus de la carcasse découpée, vue éclatée, faces de coupe en gros plan. Tableau des correspondances sourcé. |
| **5. Finitions** | LOD, compression, hors ligne, accessibilité clavier, thèmes, tests téléphone (émulation milieu de gamme), `README.md` et `SOURCES.md` finaux. | Mesures : poids, temps de premier affichage, images/seconde. |

À chaque étape : rendus de contrôle joints au compte rendu, liste de ce qui reste imparfait, commit et push sur `claude/pig-anatomy-3d-model-1pwffa`.

---

## 5. Correspondances à vérifier dès maintenant (connues avant lecture d'`anatomy.js`)

Points où les maquettes se trompent souvent ; je les vérifierai dans votre fichier :

- **Presa** : partie crâniale du m. *serratus ventralis cervicis* ; la norme ibérique la situe « entre l'échine et la palette ». Certains auteurs y rattachent aussi une part du *trapezius*/*rhomboideus* : à trancher sur source.
- **Secreto** : surtout le m. *latissimus dorsi* (grand dorsal) avec le gras qui l'entoure — conforme au cahier des charges.
- **Pluma** : extrémité crâniale du *longissimus thoracis* (lomo) au niveau des premières vertèbres thoraciques, avec une part de *spinalis* — à vérifier.
- **Lagarto** : bande du m. *iliocostalis* le long des côtes — conforme.
- **Abanico** : en réalité surtout le m. *serratus ventralis thoracis* et la viande de couverture des côtes : chevauchement possible avec la presa, à clarifier.
- **Carrillera** : *masseter* (parfois avec le *pterygoideus*) — conforme.
- **Solomillo / filet mignon** : *psoas major* + *iliacus* (ilio-psoas), *psoas minor* — à préciser.
- **Jambon français** : noix = *semimembranosus* (+ *adductor*), sous-noix = *biceps femoris* + *semitendinosus*, noix pâtissière = *quadriceps*, quasi = *gluteus medius* + *tensor fasciae latae*. Vérifié sur sources IFIP avant validation.
- **Colonne** : 14 thoraciques en standard mais 15–16 fréquent chez les lignées « longues » : je modéliserai 14 avec une note dans la fiche.

---

## 6. Calendrier indicatif

Le travail se fait en plusieurs sessions. Chaque étape se termine par un compte rendu avec captures ; vous validez avant l'étape suivante.

## 7. Ce que j'attends de vous

1. Le dossier `src/` (B1).
2. Votre accord pour ouvrir l'accès réseau aux sites de sources (B2).
3. Votre choix : **chaîne 100 % libre** ou **achat du modèle à 200 $** après vérification de sa fiche (B3).
4. Le cas échéant : la formation est-elle gratuite ou payante ? (Décide si les sources « non commerciales » sont utilisables.)
