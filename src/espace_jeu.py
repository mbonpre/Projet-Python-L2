"""
espace_jeu.py — Gestion de la carte, des déplacements, du combat et des threads.
"""

import copy
import os
import random
import time
import threading

from personnages import Hero, Monstre
from objets import Arme, Potion


# ─────────────────────────────────────────────────────────────────────────────
# Constantes de la carte
# ─────────────────────────────────────────────────────────────────────────────

SYMBOLE_MUR    = '#'
SYMBOLE_HERO   = 'H'
SYMBOLE_VIDE   = ' '
SYMBOLE_XP     = '*'
SYMBOLE_DROITE = '>'
SYMBOLE_GAUCHE = '<'
SYMBOLES_MONSTRE = {SYMBOLE_DROITE, SYMBOLE_GAUCHE}

DELAI_ROTATION = 5.0   # secondes entre chaque rotation des monstres
DELAI_PAS      = 0.1   # résolution de la boucle du thread (secondes)


# ─────────────────────────────────────────────────────────────────────────────

class _EtoileXP:
    """Remplace un monstre mort sur la carte : contient l'XP à ramasser.

    Utiliser une vraie classe (plutôt qu'un dict) rend isinstance() fiable.
    """

    def __init__(self, xp: int, position: tuple[int, int]):
        self.xp = xp
        self.position = position


# ─────────────────────────────────────────────────────────────────────────────

class EspaceJeu:
    """Représente l'espace de jeu : carte, monstres, héros et logique de combat.

    Attributes:
        largeur (int): Nombre de colonnes de la carte.
        hauteur (int): Nombre de lignes de la carte.
        niveau (int): Numéro du niveau actuel (futur : plusieurs niveaux).
        hero (Hero): Héros contrôlé par le joueur.
        monstre_modele (Monstre): Modèle utilisé pour cloner les monstres placés.
        espace (list[list[str]]): Grille 2D de caractères représentant la carte.
        _entites (list): Monstres vivants, EtoileXP ou None (case vide).
    """

    def __init__(self, largeur: int, hauteur: int, niveau: int,
                 hero: Hero, monstre_modele: Monstre):
        self.largeur = largeur
        self.hauteur = hauteur
        self.niveau = niveau
        self.hero = hero
        self.monstre_modele = monstre_modele
        self.espace = self._creer_carte()
        self._entites: list = []   # Monstre | _EtoileXP | None

        # ── Thread de rotation ─────────────────────────────────────────────
        self._rotation_active = False
        self._thread_rotation: threading.Thread | None = None
        # L'Event est "set" quand la rotation est autorisée, "cleared" en pause
        self._rotation_autorisee = threading.Event()
        self._rotation_autorisee.set()

    # =========================================================================
    # Création de la carte
    # =========================================================================

    def _creer_carte(self) -> list[list[str]]:
        """Génère une carte avec des murs extérieurs et des couloirs séparés.

        Les murs intérieurs comportent chacun un trou aléatoire pour relier
        les couloirs entre eux.
        """
        carte = [[SYMBOLE_VIDE] * self.largeur for _ in range(self.hauteur)]

        # Murs extérieurs
        for i in range(self.hauteur):
            for j in range(self.largeur):
                if (i == 0 or i == self.hauteur - 1
                        or j == 0 or j == self.largeur - 1):
                    carte[i][j] = SYMBOLE_MUR

        # Murs intérieurs avec trou
        for i in range(2, self.hauteur - 2, 2):
            for j in range(self.largeur):
                carte[i][j] = SYMBOLE_MUR
            trou = random.randint(1, self.largeur - 2)
            carte[i][trou] = SYMBOLE_VIDE

        return carte

    # =========================================================================
    # Affichage
    # =========================================================================

    @staticmethod
    def _effacer_console():
        """Efface la console (cross-platform)."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def afficher_espace(self):
        """Efface la console et réaffiche la carte avec les stats du héros."""
        self._effacer_console()
        self.hero.afficher_stats()
        print()
        for ligne in self.espace:
            print(' '.join(ligne))
        print()

    # =========================================================================
    # Placement des personnages
    # =========================================================================

    def placer_monstre(self):
        """Place un clone du monstre modèle dans chaque couloir impair.

        Le premier couloir (ligne 1) est réservé au héros.
        """
        self._entites = []
        for i in range(3, self.hauteur - 1, 2):
            j = random.randint(2, self.largeur - 2)
            monstre = Monstre(
                self.monstre_modele.nom,
                self.monstre_modele.hp,
                self.monstre_modele.level,
                self.monstre_modele.xp_gagne,
                copy.copy(self.monstre_modele.arme),
            )
            monstre.position = (i, j)
            self._entites.append(monstre)
            self.espace[i][j] = monstre.symbole

    def placer_hero(self):
        """(Re)place le symbole du héros à sa position courante."""
        x, y = self.hero.position
        self.espace[x][y] = SYMBOLE_HERO

    # =========================================================================
    # Déplacement du joueur
    # =========================================================================

    _DIRECTIONS = {
        'haut':   (-1,  0),
        'bas':    ( 1,  0),
        'gauche': ( 0, -1),
        'droite': ( 0,  1),
    }

    def deplacer_joueur(self, hero: Hero, direction: str):
        """Déplace le héros d'une case dans la direction demandée.

        Bloque le déplacement sur un mur ou sur un monstre vivant.
        Ramasse automatiquement une étoile XP si le héros marche dessus.
        """
        if direction not in self._DIRECTIONS:
            return

        dx, dy = self._DIRECTIONS[direction]
        x, y = hero.position
        nx, ny = x + dx, y + dy

        case_cible = self.espace[nx][ny]

        if case_cible == SYMBOLE_MUR:
            print("  Vous ne pouvez pas aller dans cette direction (mur).")
            return

        # BUG CORRIGÉ : bloquer le passage sur un monstre vivant
        if case_cible in SYMBOLES_MONSTRE:
            print("  Un monstre bloque le passage ! Combattez-le d'abord.")
            return

        self.espace[x][y] = SYMBOLE_VIDE
        hero.position = (nx, ny)
        self.placer_hero()

        # BUG CORRIGÉ : ramassage automatique si le héros marche sur une étoile
        if case_cible == SYMBOLE_XP:
            self.verifier_ramassage_xp(hero)

    # =========================================================================
    # Thread de rotation des monstres
    # =========================================================================

    def demarrer_rotation_monstres(self):
        """Lance le thread de rotation automatique des monstres."""
        self._rotation_active = True
        self._thread_rotation = threading.Thread(
            target=self._boucle_rotation, daemon=True
        )
        self._thread_rotation.start()

    def arreter_rotation_monstres(self):
        """Arrête définitivement le thread (fin de partie)."""
        self._rotation_active = False
        self._rotation_autorisee.set()   # débloque le thread s'il était en pause

    def mettre_en_pause_rotation(self):
        """Suspend la rotation (inventaire ouvert, combat, etc.)."""
        self._rotation_autorisee.clear()

    def reprendre_rotation(self):
        """Reprend la rotation après une pause."""
        self._rotation_autorisee.set()

    def _boucle_rotation(self):
        """Boucle du thread : attend DELAI_ROTATION secondes puis retourne les monstres.

        Si une pause est détectée pendant le compte à rebours,
        le compteur repart à zéro au prochain cycle.
        """
        while self._rotation_active:
            self._rotation_autorisee.wait()   # bloque si en pause

            # Compte à rebours fractionné pour pouvoir détecter une pause
            nb_pas = int(DELAI_ROTATION / DELAI_PAS)
            pause_detectee = False
            for _ in range(nb_pas):
                if not self._rotation_active:
                    return
                if not self._rotation_autorisee.is_set():
                    pause_detectee = True
                    break
                time.sleep(DELAI_PAS)

            if not pause_detectee and self._rotation_autorisee.is_set():
                self._retourner_monstres()
                self.afficher_espace()
                print("  [Les monstres changent de direction !]")

                # BUG CORRIGÉ : vérifier si un monstre voit maintenant le héros
                monstre_visible = self.trouver_monstre_qui_voit_hero()
                if monstre_visible is not None:
                    print(f"  ⚠  {monstre_visible.nom} vous a dans sa ligne de mire !")
                    # Le combat sera déclenché au prochain tour de la boucle principale
                    # (le thread ne peut pas appeler input() directement)

                print("Actions (1-Haut 2-Bas 3-Gauche 4-Droite "
                      "5-Attaquer 6-Inventaire 0-Quitter) : ",
                      end='', flush=True)

    def _retourner_monstres(self):
        """Inverse la direction de tous les monstres vivants et met la carte à jour.

        BUG CORRIGÉ : après la rotation, si un monstre voit maintenant le héros,
        un combat est déclenché immédiatement (géré dans _boucle_rotation).
        """
        for entite in self._entites:
            if isinstance(entite, Monstre):
                entite.face = not entite.face
                x, y = entite.position
                self.espace[x][y] = entite.symbole

    # Propriété publique pour compatibilité avec main.py (ancien nom)
    @property
    def liste_monstre(self) -> list:
        return self._entites

    # =========================================================================
    # Détection du champ de vision
    # =========================================================================

    def monstre_voit_hero(self, monstre: Monstre) -> bool:
        """Retourne True si le monstre a le héros dans son champ de vision.

        Le champ de vision est la ligne du monstre dans sa direction de regard,
        bloqué par les murs '#'.
        """
        if not isinstance(monstre, Monstre):
            return False

        ligne = monstre.position[0]
        col   = monstre.position[1]

        if monstre.face:
            colonnes = range(col, self.largeur - 1)
        else:
            colonnes = range(col, 0, -1)

        for j in colonnes:
            case = self.espace[ligne][j]
            if case == SYMBOLE_MUR:
                break
            if case == SYMBOLE_HERO:
                return True

        return False

    def trouver_monstre_qui_voit_hero(self) -> Monstre | None:
        """Retourne le premier monstre qui voit le héros, ou None."""
        for entite in self._entites:
            if isinstance(entite, Monstre) and self.monstre_voit_hero(entite):
                return entite
        return None

    # =========================================================================
    # Combat au tour par tour (monstre vs héros)
    # =========================================================================

    def declencher_combat(self, monstre: Monstre, hero: Hero) -> bool:
        """Gère un combat complet au tour par tour.

        La rotation est suspendue pendant toute la durée du combat.

        Returns:
            True si le héros survit, False sinon.
        """
        self.mettre_en_pause_rotation()
        print(f"\n  ⚠  {monstre.nom} vous a repéré ! Le combat commence !")
        print("  (Rotation suspendue pendant le combat)\n")
        time.sleep(0.8)

        while monstre.est_vivant and hero.est_vivant:
            self.afficher_espace()
            print(f"  ══ COMBAT : {hero.nom}  vs  {monstre.nom} ══")
            print(f"  {hero.nom} : {hero.hp}/{hero.hp_max} HP   |   "
                  f"{monstre.nom} : {monstre.hp} HP\n")

            mun = ("∞" if hero.arme_actuelle.munitions == Arme.ILLIMITE
                   else hero.arme_actuelle.munitions)
            print(f"  1 — Attaquer avec {hero.arme_actuelle.nom} ({mun} mun.)")
            print("  2 — Utiliser une potion")
            print("  3 — Changer d'arme")
            print("  0 — Fuir (le monstre frappe avant votre fuite)")

            choix = input("  Votre choix : ").strip()

            if choix == '1':
                hero.attaquer(monstre)
                if monstre.est_vivant:
                    monstre.attaquer(hero)
                    time.sleep(0.5)

            elif choix == '2':
                hero.utiliser_potion()
                # Utiliser une potion ne déclenche pas de riposte

            elif choix == '3':
                hero.changer_arme()
                # Changer d'arme ne déclenche pas de riposte

            elif choix == '0':
                print(f"  Vous fuyez ! {monstre.nom} vous frappe dans le dos !")
                monstre.attaquer(hero)
                time.sleep(0.8)
                self.reprendre_rotation()
                return hero.est_vivant

            else:
                # BUG CORRIGÉ : choix invalide = juste un avertissement, pas de riposte
                print("  Choix invalide — réessayez.")

        # Fin du combat
        if not monstre.est_vivant:
            self._monstre_mort(monstre)

        self.reprendre_rotation()
        return hero.est_vivant

    # =========================================================================
    # Attaque initiative du héros (hors combat initié par un monstre)
    # =========================================================================

    def attaque_hero(self, hero: Hero) -> Monstre | None:
        """Le héros tire sur le premier monstre visible dans son couloir.

        Cherche d'abord sur la même ligne (droite puis gauche),
        puis sur la même colonne (bas puis haut).

        Returns:
            Le monstre touché et encore vivant, ou None.
        """
        x, y = hero.position
        monstre_cible = (
            self._chercher_monstre_ligne(x, range(y + 1, self.largeur - 1))
            or self._chercher_monstre_ligne(x, range(y - 1, 0, -1))
            or self._chercher_monstre_colonne(range(x + 1, self.hauteur - 1), y)
            or self._chercher_monstre_colonne(range(x - 1, 0, -1), y)
        )

        if monstre_cible is None:
            print("  Aucun monstre en vue… vous gaspillez une munition !")
            if hero.arme_actuelle.est_utilisable:
                hero.arme_actuelle.consommer_munition()
            return None

        hero.attaquer(monstre_cible)

        if not monstre_cible.est_vivant:
            self._monstre_mort(monstre_cible)
            return None

        return monstre_cible

    def _chercher_monstre_ligne(self, ligne: int, colonnes) -> Monstre | None:
        """Parcourt une ligne dans les colonnes données et retourne le premier monstre trouvé."""
        for j in colonnes:
            case = self.espace[ligne][j]
            if case == SYMBOLE_MUR:
                break
            if case in SYMBOLES_MONSTRE:
                return self._entite_en(ligne, j)
        return None

    def _chercher_monstre_colonne(self, lignes, col: int) -> Monstre | None:
        """Parcourt une colonne dans les lignes données et retourne le premier monstre trouvé."""
        for i in lignes:
            case = self.espace[i][col]
            if case == SYMBOLE_MUR:
                break
            if case in SYMBOLES_MONSTRE:
                return self._entite_en(i, col)
        return None

    def _entite_en(self, x: int, y: int) -> Monstre | None:
        """Retourne le Monstre situé aux coordonnées (x, y), ou None."""
        for entite in self._entites:
            if isinstance(entite, Monstre) and entite.position == (x, y):
                return entite
        return None

    # =========================================================================
    # Mort d'un monstre → étoile XP
    # =========================================================================

    def _monstre_mort(self, monstre: Monstre):
        """Remplace un monstre mort par une étoile '*' sur la carte et dans la liste."""
        print(f"  ☠  {monstre.nom} est vaincu ! "
              f"Une étoile ★ apparaît à sa place.")
        x, y = monstre.position
        self.espace[x][y] = SYMBOLE_XP
        idx = self._entites.index(monstre)
        self._entites[idx] = _EtoileXP(xp=monstre.xp_gagne, position=(x, y))

    # =========================================================================
    # Ramassage de l'XP
    # =========================================================================

    def verifier_ramassage_xp(self, hero: Hero):
        """Vérifie si le héros se trouve sur une étoile et lui attribue l'XP."""
        x, y = hero.position
        for idx, entite in enumerate(self._entites):
            if isinstance(entite, _EtoileXP) and entite.position == (x, y):
                hero.gagner_experience(entite.xp)
                self._entites[idx] = None      # étoile consommée
                self.espace[x][y] = SYMBOLE_VIDE
                self.placer_hero()
                print(f"  ★ Vous ramassez l'étoile et gagnez {entite.xp} XP !")
                time.sleep(0.8)
                break
