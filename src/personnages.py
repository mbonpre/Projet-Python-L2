"""
personnages.py — Hiérarchie de classes pour les personnages du jeu.

    Personnage (classe mère abstraite)
    ├── Hero
    └── Monstre
"""

from objets import Inventaire, Arme, Potion


# ─────────────────────────────────────────────────────────────────────────────
# Classe mère
# ─────────────────────────────────────────────────────────────────────────────

class Personnage:
    """Classe mère commune à Hero et Monstre.

    Attributes:
        nom (str): Nom du personnage.
        hp (int): Points de vie actuels.
        hp_max (int): Points de vie maximum.
        level (int): Niveau du personnage.
        position (tuple[int, int]): Coordonnées (ligne, colonne) sur la carte.
    """

    def __init__(self, nom: str, hp: int, level: int):
        self.nom = nom
        self.hp = hp
        self.hp_max = hp
        self.level = level
        self.position: tuple[int, int] = (1, 1)

    @property
    def est_vivant(self) -> bool:
        """Retourne True si le personnage est encore en vie."""
        return self.hp > 0

    def subir_degats(self, degats: int):
        """Applique des dégâts au personnage (minimum 0 HP)."""
        self.hp = max(0, self.hp - degats)


# ─────────────────────────────────────────────────────────────────────────────
# Héros
# ─────────────────────────────────────────────────────────────────────────────

# Arme de corps-à-corps par défaut (munitions illimitées)
POINGS = Arme("Poings", degats=3, munitions=Arme.ILLIMITE)


class Hero(Personnage):
    """Représente le héros contrôlé par le joueur.

    Attributes:
        experience (int): XP accumulée depuis le dernier niveau.
        inventaire (Inventaire): Potions et armes en réserve.
        arme_actuelle (Arme): Arme actuellement équipée.
    """

    XP_PAR_NIVEAU = 100  # XP nécessaire pour passer au niveau suivant

    def __init__(self, nom: str, hp: int, level: int, arme_actuelle: Arme):
        super().__init__(nom, hp, level)
        self.experience = 0
        self.inventaire = Inventaire()
        self.arme_actuelle = arme_actuelle

    # ── Progression ──────────────────────────────────────────────────────────

    def gagner_experience(self, xp: int):
        """Ajoute de l'XP et déclenche une montée de niveau si le seuil est atteint."""
        self.experience += xp
        print(f"  ★ {self.nom} gagne {xp} XP ! "
              f"(Total : {self.experience}/{self.XP_PAR_NIVEAU})")
        while self.experience >= self.XP_PAR_NIVEAU:
            self.experience -= self.XP_PAR_NIVEAU
            self.level += 1
            self.hp_max += 10          # bonus de vitalité à chaque niveau
            self.hp = self.hp_max       # soin complet lors du level-up
            print(f"  ⬆  {self.nom} passe au niveau {self.level} ! "
                  f"(HP max : {self.hp_max})")

    # ── Combat ───────────────────────────────────────────────────────────────

    def attaquer(self, cible: "Personnage"):
        """Attaque une cible avec l'arme actuellement équipée.

        Si l'arme est vide, bascule automatiquement sur les Poings.
        """
        if not self.arme_actuelle.est_utilisable:
            print(f"  {self.nom} n'a plus de munitions pour "
                  f"{self.arme_actuelle.nom} ! Il se bat à mains nues.")
            self.arme_actuelle = POINGS

        degats = self.arme_actuelle.degats
        self.arme_actuelle.consommer_munition()
        cible.subir_degats(degats)

        mun = ("∞" if self.arme_actuelle.munitions == Arme.ILLIMITE
               else self.arme_actuelle.munitions)
        print(f"  ⚔  {self.nom} attaque avec {self.arme_actuelle.nom} "
              f"et inflige {degats} dégâts. "
              f"(HP ennemi : {max(0, cible.hp)} | Mun. restantes : {mun})")

    # ── Gestion de l'inventaire ──────────────────────────────────────────────

    def utiliser_potion(self):
        """Permet au héros de choisir et d'utiliser une potion depuis l'inventaire."""
        if not self.inventaire.potions:
            print("  Vous n'avez aucune potion dans votre inventaire.")
            return

        self.inventaire.afficher()
        choix = input("  Numéro de la potion à utiliser (0 pour annuler) : ").strip()

        if not choix.isdigit():
            print("  Choix invalide.")
            return

        choix = int(choix)
        if choix == 0:
            return

        if 1 <= choix <= len(self.inventaire.potions):
            potion = self.inventaire.potions.pop(choix - 1)
            soin_effectif = min(potion.soin, self.hp_max - self.hp)
            self.hp += soin_effectif
            print(f"  {self.nom} utilise {potion.nom} "
                  f"et récupère {soin_effectif} HP. "
                  f"(HP : {self.hp}/{self.hp_max})")
        else:
            print("  Numéro hors de la liste.")

    def changer_arme(self):
        """Permet au héros de choisir une arme de réserve et de l'équiper."""
        if not self.inventaire.armes:
            print("  Vous n'avez aucune autre arme dans votre inventaire.")
            return

        self.inventaire.afficher()
        choix = input("  Numéro de l'arme à équiper (0 pour annuler) : ").strip()

        if not choix.isdigit():
            print("  Choix invalide.")
            return

        choix = int(choix)
        if choix == 0:
            return

        if 1 <= choix <= len(self.inventaire.armes):
            ancienne_arme = self.arme_actuelle
            self.arme_actuelle = self.inventaire.armes.pop(choix - 1)
            # L'ancienne arme rejoint la réserve (sauf si c'est les Poings)
            if ancienne_arme is not POINGS:
                self.inventaire.ajouter_arme(ancienne_arme)
            mun = ("∞" if self.arme_actuelle.munitions == Arme.ILLIMITE
                   else self.arme_actuelle.munitions)
            print(f"  Vous équipez {self.arme_actuelle.nom} ! "
                  f"(Dégâts : {self.arme_actuelle.degats} | Mun. : {mun})")
        else:
            print("  Numéro hors de la liste.")

    def ajouter_objet_inventaire(self, potion: Potion):
        """Ajoute une potion à l'inventaire du héros."""
        self.inventaire.ajouter_potion(potion)

    def ajouter_arme_inventaire(self, arme: Arme):
        """Ajoute une arme à la réserve de l'inventaire du héros."""
        self.inventaire.ajouter_arme(arme)

    # ── Affichage ────────────────────────────────────────────────────────────

    def afficher_stats(self):
        """Affiche un résumé des statistiques du héros sur une ligne."""
        mun = ("∞" if self.arme_actuelle.munitions == Arme.ILLIMITE
               else self.arme_actuelle.munitions)
        print(
            f"  [{self.nom}]  "
            f"HP : {self.hp}/{self.hp_max}  |  "
            f"Niv. {self.level}  |  "
            f"XP : {self.experience}/{self.XP_PAR_NIVEAU}  |  "
            f"Arme : {self.arme_actuelle.nom} ({mun} mun.)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Monstre
# ─────────────────────────────────────────────────────────────────────────────

class Monstre(Personnage):
    """Représente un monstre contrôlé par le jeu.

    Attributes:
        xp_gagne (int): XP accordée au héros lors de la défaite du monstre.
        arme (Arme): Arme du monstre.
        face (bool): True → regarde à droite ('>'), False → à gauche ('<').
    """

    def __init__(self, nom: str, hp: int, level: int, xp_gagne: int, arme: Arme):
        super().__init__(nom, hp, level)
        self.xp_gagne = xp_gagne
        self.arme = arme
        self.face: bool = True  # True = '>'  False = '<'

    @property
    def symbole(self) -> str:
        """Retourne le caractère affiché sur la carte selon la direction."""
        return '>' if self.face else '<'

    def attaquer(self, hero: Hero):
        """Le monstre attaque le héros.

        Si ses munitions sont épuisées, il passe aux griffes (dégâts réduits).
        """
        if not self.arme.est_utilisable:
            # Le monstre griffe quand il n'a plus de munitions
            degats_griffes = max(1, self.level * 2)
            hero.subir_degats(degats_griffes)
            print(f"  💀 {self.nom} griffe {hero.nom} "
                  f"et inflige {degats_griffes} dégâts. "
                  f"(HP héros : {max(0, hero.hp)})")
        else:
            degats = self.arme.degats
            self.arme.consommer_munition()
            hero.subir_degats(degats)
            print(f"  💀 {self.nom} attaque {hero.nom} "
                  f"avec {self.arme.nom} "
                  f"et inflige {degats} dégâts. "
                  f"(HP héros : {max(0, hero.hp)})")

    def __str__(self):
        return (f"[{self.nom}  HP:{self.hp}  Niv:{self.level}  "
                f"Pos:{self.position}  Arme:{self.arme}  "
                f"Face:{self.symbole}]")

    def __repr__(self):
        return self.__str__()
