# Néo-Kairos

Jeu d'exploration et de survie dans une ville futuriste, en un seul fichier HTML (aucune dépendance).

**Jouer :** ouvrir `index.html` dans un navigateur.

## Principe
- La ville est divisée en 4 secteurs : Néo-Marché → Secteur Industriel → Marais Toxiques → Citadelle Quantique.
- Les trésors sont cachés : le **scanner** bipe de plus en plus vite quand tu t'en approches. Appuie sur **E** pour fouiller.
- Revends-les automatiquement en crédits (¢) et achète chez le **marchand** de chaque secteur : nourriture, soins, améliorations… et l'objet qui ouvre le portail du secteur suivant (Badge, Combinaison anti-toxique, Clé quantique).
- Survis : l'énergie baisse en continu, les flaques toxiques brûlent sans combinaison, et les drones de sécurité attaquent.
- Victoire : acheter le **billet de la navette orbitale** (5 000 ¢) dans la Citadelle Quantique.

## Commandes
| Touche | Action |
|---|---|
| ZQSD / WASD / flèches | Se déplacer |
| E / Espace | Fouiller, parler au marchand |
| F | Grenade IEM (neutralise les drones proches) |
| P / Échap | Pause |

Sur mobile : joystick virtuel + boutons E et IEM. La partie est sauvegardée automatiquement dans le navigateur.

---

# Atlas 3D de l'anatomie du porc (en cours)

Plan : `PLAN.md` · Sources et licences : `SOURCES.md` · Rendus de contrôle : `docs/controle/`.

## Chaîne de sculpture des os (étape 1, pilote)

Prérequis : Python 3.13 avec `bpy==5.2.4`, `scikit-image`, `scipy`, `pillow` (`pip install bpy==5.2.4 scikit-image scipy pillow`).

```bash
# sculpter un os (pas de grille en cm) → maillage PLY
python tools/sculpt/build_bone.py femur 0.06 /tmp/femur.ply
# planche de contrôle 6 vues (Blender sans interface, rendu Cycles)
python tools/blender/render_check.py /tmp/femur.png "Fémur gauche" /tmp/femur.ply
```

**Ajouter un os** : créer `tools/sculpt/bones/<nom>.py` avec `BBOX` (boîte englobante en cm) et une fonction `sdf(P)`
qui compose les primitives de `tools/sculpt/sdf.py` (têtes, fûts, lames, crêtes, fosses, foramens). Repère local
documenté en tête de chaque fichier ; repère de l'animal : X vers le groin, Y vers le haut, Z vers la gauche, en cm.
