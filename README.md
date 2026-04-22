# Projet-Python-L2
Projet Python L2 (APP) : création d’un environnement RPG simulant des interactions entre entités (joueurs, ennemis, objets) avec une architecture orientée objet (classes, héritage, encapsulation) et suivi de version avec Git.

Réalisé par : 
    MERE Marcellin 
    NAMBONI Précieux 

#  Jeu de Donjon en Terminal

Un jeu de rôle en mode texte jouable dans le terminal, développé en Python. Le joueur incarne un héros qui explore un donjon généré aléatoirement, affronte des monstres et gère son inventaire pour survivre.


##  Structure du projet

src 
├── main.py           # Point d'entrée du jeu, boucle principale
├── espace_jeu.py     # Gestion du terrain, déplacements et combats
├── personnages.py    # Classes Hero, Monstre et Personnage
└── objets.py         # Classes Inventaire, Arme et Potion
```

## Comment jouer

``bash
python main.py : pour lancer l'interprétation 
```
### Contrôles
`1` -> Se déplacer vers le haut 
`2` -> Se déplacer vers le bas 
`3` -> Se déplacer vers la gauche 
`4` -> Se déplacer vers la droite 
`5` -> Attaquer 
`6` -> Ouvrir l'inventaire 
`0` -> Quitter le jeu 


##  Le terrain

- Le donjon est généré aléatoirement à chaque partie (15×11 cases par défaut).
- `#` représente les murs, `H` le héros, `>` ou `<` un monstre (selon sa direction), `*` l'XP laissée par un monstre vaincu.
- Des couloirs séparent les zones, avec des passages aléatoires dans les murs intérieurs.

##  Système de combat

- Le héros attaque dans les 4 directions. La première cible rencontrée dans la ligne de vue reçoit les dégâts.
- Les monstres voient le héros dans leur ligne de vue (droite ou gauche selon leur orientation) et attaquent automatiquement lorsqu'il entre dans leur champ.
- Les monstres pivotent tous les 3 tours.
- Chaque arme a un nombre limité de **munitions**.

## Inventaire

Accessible avec la touche `6` :

- **Utiliser une potion** : restaure des HP (maximum 100).
- **Changer d'arme** : équipe une arme depuis l'inventaire, l'ancienne arme y est rangée automatiquement.

## Progression

- Vaincre un monstre laisse une `*` sur le sol. La ramasser rapporte de l'**XP**.
- À 100 XP, le héros gagne un niveau.

## Classes principales

### `Hero` *(personnages.py)*
Représente le joueur. Possède un inventaire, une arme équipée, des HP et un niveau. Peut attaquer, utiliser des potions et changer d'arme.

### `Monstre` *(personnages.py)*
Ennemi placé aléatoirement dans le donjon. Possède une orientation (gauche/droite), une arme et attaque le héros s'il le voit.

### `EspaceJeu` *(espace_jeu.py)*
Gère la grille de jeu, le placement des personnages, les déplacements, la rotation des monstres, les attaques et le ramassage d'XP.

### `Inventaire`, `Arme`, `Potion` *(objets.py)*
Gestion des objets du héros : armes avec dégâts et munitions, potions de soin, affichage de l'inventaire.

### Bon jeu à vous 