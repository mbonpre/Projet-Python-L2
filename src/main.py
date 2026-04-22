"""
main.py — Point d'entrée du RPG en console.

Contient :
  - Les données du jeu (listes de héros et de monstres disponibles).
  - Les fonctions de menu (choix du héros, actions, inventaire, etc.).
  - La boucle principale du jeu.
"""

import time

from espace_jeu import EspaceJeu
from personnages import Hero, Monstre
from objets import Arme, Potion

# ─────────────────────────────────────────────────────────────────────────────
# Données du jeu
# ─────────────────────────────────────────────────────────────────────────────

LISTE_MONSTRES = [
    Monstre("Gobelin", hp=50,  level=1, xp_gagne=20,  arme=Arme("Dague rouillée",    degats=5,  munitions=10)),
    Monstre("Orc",     hp=80,  level=2, xp_gagne=40,  arme=Arme("Hache en pierre",   degats=15, munitions=5)),
    Monstre("Troll",   hp=120, level=3, xp_gagne=60,  arme=Arme("Massue en fer",     degats=25, munitions=3)),
    Monstre("Dragon",  hp=200, level=5, xp_gagne=100, arme=Arme("Flamme du dragon",  degats=40, munitions=2)),
]

LISTE_HEROS = [
    Hero("Arthur",  hp=100, level=1, arme_actuelle=Arme("Épée en bois",         degats=10, munitions=5)),
    Hero("Ichigo",  hp=120, level=2, arme_actuelle=Arme("Zanpakuto",            degats=20, munitions=10)),
    Hero("Goku",    hp=150, level=3, arme_actuelle=Arme("Kamehameha",           degats=30, munitions=5)),
    Hero("Saitama", hp=200, level=5, arme_actuelle=Arme("One Punch",            degats=50, munitions=1)),
    Hero("Luffy",   hp=180, level=4, arme_actuelle=Arme("Gomu Gomu no Pistol", degats=25, munitions=7)),
]

# ─────────────────────────────────────────────────────────────────────────────
# Fonctions de menus
# ─────────────────────────────────────────────────────────────────────────────

def choisir_hero() -> Hero:
    """Affiche la liste des héros disponibles et retourne celui que le joueur choisit."""
    print('-' * 20, "Choisissez votre héros", '-' * 20)
    for i, hero in enumerate(LISTE_HEROS, start=1):
        mun = hero.arme_actuelle.munitions
        print(f"  {i} — {hero.nom}"
              f"  (HP : {hero.hp} | Niv. {hero.level}"
              f" | Arme : {hero.arme_actuelle.nom}, {mun} mun.)")

    while True:
        choix = input("Entrez le numéro du héros : ").strip()
        if choix.isdigit() and 1 <= int(choix) <= len(LISTE_HEROS):
            return LISTE_HEROS[int(choix) - 1]
        print(f"  Choix invalide. Entrez un nombre entre 1 et {len(LISTE_HEROS)}.")


def choisir_action() -> str | None:
    """Affiche le menu d'actions et retourne l'action choisie (ou None si invalide)."""
    print("Actions disponibles :")
    print("  1 — Haut      2 — Bas      3 — Gauche      4 — Droite")
    print("  5 — Attaquer  6 — Inventaire  7 — Stats     0 — Quitter")
    choix = input("Votre choix : ").strip()

    actions = {
        '1': 'haut',
        '2': 'bas',
        '3': 'gauche',
        '4': 'droite',
        '5': 'attaquer',
        '6': 'inventaire',
        '7': 'stats',
        '0': 'quitter',
    }
    return actions.get(choix)


def menu_pre_attaque(hero: Hero, jeu: EspaceJeu) -> bool:
    """Menu affiché avant que le héros attaque librement.

    Permet d'utiliser une potion ou changer d'arme avant de tirer.

    Returns:
        True si le joueur confirme l'attaque, False s'il annule.
    """
    mun = hero.arme_actuelle.munitions
    print("\n  Avant d'attaquer :")
    print("  1 — Utiliser une potion")
    print("  2 — Changer d'arme")
    print(f"  3 — Attaquer directement avec {hero.arme_actuelle.nom} ({mun} mun.)")
    print("  0 — Annuler")

    choix = input("  Votre choix : ").strip()

    if choix == '1':
        hero.utiliser_potion()
        return menu_pre_attaque(hero, jeu)
    elif choix == '2':
        hero.changer_arme()
        return menu_pre_attaque(hero, jeu)
    elif choix == '3':
        return True
    elif choix == '0':
        return False
    else:
        print("  Choix invalide.")
        return menu_pre_attaque(hero, jeu)


def ouvrir_inventaire(hero: Hero, jeu: EspaceJeu):
    """Ouvre l'inventaire du héros (rotation mise en pause)."""
    jeu.mettre_en_pause_rotation()
    hero.inventaire.afficher()
    print(f"  Arme équipée : {hero.arme_actuelle.nom}"
          f" (Dégâts : {hero.arme_actuelle.degats}"
          f" | Mun. : {hero.arme_actuelle.munitions})")
    choix = input("\n  1 — Utiliser une potion  |  2 — Changer d'arme  |  0 — Fermer : ").strip()
    if choix == '1':
        hero.utiliser_potion()
    elif choix == '2':
        hero.changer_arme()
    jeu.reprendre_rotation()


def verifier_fin_partie(hero: Hero, jeu: EspaceJeu) -> bool:
    """Vérifie si la partie est terminée (mort du héros ou tous les monstres vaincus).

    Returns:
        True si la partie doit s'arrêter.
    """
    if not hero.est_vivant:
        jeu.afficher_espace()
        print("=" * 45)
        print("  GAME OVER — Vous avez été vaincu…")
        print("=" * 45)
        return True

    monstres_restants = [e for e in jeu.liste_monstre if isinstance(e, Monstre)]
    if not monstres_restants:
        jeu.afficher_espace()
        print("=" * 45)
        print("  VICTOIRE ! Tous les monstres sont vaincus !")
        print(f"  {hero.nom} termine au niveau {hero.level} "
              f"avec {hero.experience} XP.")
        print("=" * 45)
        return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Boucle principale
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 45)
    print("    Bienvenue dans le RPG du Donjon !")
    print("=" * 45)
    print("Explorez les couloirs, combattez les monstres,")
    print("ramassez les étoiles ★ pour gagner de l'XP !")
    print("Les monstres changent de direction toutes les "
          "5 secondes !\n")

    # Choix du héros
    hero = choisir_hero()

    # Dotation de départ
    hero.ajouter_objet_inventaire(Potion("Petite potion", soin=30))
    hero.ajouter_objet_inventaire(Potion("Grande potion", soin=60))

    print(f"\nVous incarnez {hero.nom} ! Bonne chance !\n")
    time.sleep(1)

    # Création et initialisation de la carte
    monstre_modele = LISTE_MONSTRES[0]
    jeu = EspaceJeu(largeur=15, hauteur=11, niveau=1,
                    hero=hero, monstre_modele=monstre_modele)
    jeu.placer_monstre()
    jeu.placer_hero()
    jeu.demarrer_rotation_monstres()

    # ── Boucle principale ─────────────────────────────────────────────────
    en_cours = True
    while en_cours:

        jeu.afficher_espace()

        # Un monstre voit-il le héros ? → combat immédiat
        monstre_ennemi = jeu.trouver_monstre_qui_voit_hero()
        if monstre_ennemi is not None:
            hero_survit = jeu.declencher_combat(monstre_ennemi, hero)
            if not hero_survit:
                jeu.arreter_rotation_monstres()
                jeu.afficher_espace()
                print("=" * 45)
                print("  GAME OVER — Vous avez été vaincu…")
                print("=" * 45)
                break
            if verifier_fin_partie(hero, jeu):
                jeu.arreter_rotation_monstres()
                break
            continue   # réafficher la carte avant la prochaine action

        # ── Action du joueur ──────────────────────────────────────────────
        action = choisir_action()

        if action is None:
            print("  Action invalide, réessayez.")
            time.sleep(0.6)

        elif action == 'quitter':
            print("  Vous quittez le jeu. À bientôt !")
            jeu.arreter_rotation_monstres()
            en_cours = False

        elif action in ('haut', 'bas', 'gauche', 'droite'):
            jeu.deplacer_joueur(hero, action)
            # Le ramassage XP est désormais automatique dans deplacer_joueur

        elif action == 'attaquer':
            jeu.mettre_en_pause_rotation()
            if menu_pre_attaque(hero, jeu):
                jeu.attaque_hero(hero)
            jeu.reprendre_rotation()

            if verifier_fin_partie(hero, jeu):
                jeu.arreter_rotation_monstres()
                en_cours = False

        elif action == 'inventaire':
            ouvrir_inventaire(hero, jeu)

        elif action == 'stats':
            jeu.mettre_en_pause_rotation()
            hero.afficher_stats()
            input("  (Appuyez sur Entrée pour continuer)")
            jeu.reprendre_rotation()


if __name__ == "__main__":
    main()
