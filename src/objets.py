"""
objets.py — Définition des objets du jeu : Arme, Potion, Inventaire.
"""


class Arme:
    """Représente une arme utilisable par un personnage.

    Attributes:
        nom (str): Nom de l'arme.
        degats (int): Points de dégâts infligés par attaque.
        munitions (int): Nombre d'utilisations restantes.
                         -1 signifie illimité (arme de corps-à-corps).
    """

    ILLIMITE = -1  # Sentinelle pour les armes sans munitions

    def __init__(self, nom: str, degats: int, munitions: int):
        self.nom = nom
        self.degats = degats
        self.munitions = munitions

    @property
    def est_utilisable(self) -> bool:
        """Retourne True si l'arme peut encore être utilisée."""
        return self.munitions == Arme.ILLIMITE or self.munitions > 0

    def consommer_munition(self):
        """Décrémente les munitions si l'arme n'est pas illimitée."""
        if self.munitions != Arme.ILLIMITE:
            self.munitions -= 1

    def __repr__(self):
        mun = "∞" if self.munitions == Arme.ILLIMITE else self.munitions
        return f"{{{self.nom}, {self.degats} dégâts, {mun} mun.}}"


# ─────────────────────────────────────────────────────────────────────────────

class Potion:
    """Représente une potion de soin.

    Attributes:
        nom (str): Nom de la potion.
        soin (int): Points de vie restaurés à l'utilisation.
    """

    def __init__(self, nom: str, soin: int):
        self.nom = nom
        self.soin = soin

    def __repr__(self):
        return f"[Potion: {self.nom}, +{self.soin} HP]"


# ─────────────────────────────────────────────────────────────────────────────

class Inventaire:
    """Représente l'inventaire d'un personnage : potions et armes de réserve.

    Attributes:
        potions (list[Potion]): Liste des potions disponibles.
        armes (list[Arme]): Liste des armes en réserve (non équipées).
    """

    def __init__(self):
        self.potions: list[Potion] = []
        self.armes: list[Arme] = []

    # ── Ajout ────────────────────────────────────────────────────────────────

    def ajouter_potion(self, potion: Potion):
        """Ajoute une potion à l'inventaire."""
        self.potions.append(potion)

    # Alias conservé pour la compatibilité avec l'ancien code du binôme
    def ajouter_objet(self, potion: Potion):
        """Alias de ajouter_potion() (compatibilité)."""
        self.ajouter_potion(potion)

    def ajouter_arme(self, arme: Arme):
        """Ajoute une arme à la réserve de l'inventaire."""
        self.armes.append(arme)

    # ── Affichage ────────────────────────────────────────────────────────────

    def afficher(self):
        """Affiche le contenu complet de l'inventaire dans la console."""
        separateur = "-" * 42
        print(separateur)
        print("  INVENTAIRE")
        print(separateur)

        print("  Potions :")
        if not self.potions:
            print("    (aucune potion)")
        for i, potion in enumerate(self.potions, start=1):
            print(f"    {i} — {potion.nom} (+{potion.soin} HP)")

        print("  Armes en réserve :")
        if not self.armes:
            print("    (aucune arme en stock)")
        for i, arme in enumerate(self.armes, start=1):
            mun = "∞" if arme.munitions == Arme.ILLIMITE else arme.munitions
            print(f"    {i} — {arme.nom}  |  {arme.degats} dégâts  |  {mun} mun.")
        print(separateur)

    # Alias conservé pour la compatibilité
    def afficher_inventaire(self):
        """Alias de afficher() (compatibilité)."""
        self.afficher()

    # ── Propriétés utiles ────────────────────────────────────────────────────

    @property
    def objets(self) -> list[Potion]:
        """Alias de self.potions (compatibilité avec l'ancien code)."""
        return self.potions
