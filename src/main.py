import time
from espace_jeu import EspaceJeu
from personnages import Hero, Monstre
from objets import Arme, Potion

hero = Hero("Ishida(Quincy)", 100, 1, Arme("Flèche", 20, 5))
hero.ajouter_objet_inventaire(Potion("Potion", 20))
hero.ajouter_arme_inventaire(Arme("Voolstanding", 30, 3))

monstre_modele = Monstre("Dragonnute", 50, 1, 20, Arme("Boule de feu", 10, 10))


jeu = EspaceJeu(15, 11, 1, hero, monstre_modele)
jeu.placer_monstre()
jeu.placer_hero()

en_cours = True

while en_cours:
    jeu.afficher_espace()
    
    """ # PRIORITÉ : monstre agressif
    jeu.gerer_monstre_agressif() """

    if hero.hp <= 0:
        print("-------- GAME OVER -------------")
        break

    # rotation seulement si pas de combat
    jeu.rotation_monstres()

    print("1-Haut 2-Bas 3-Gauche 4-Droite 5-Attaquer 6- Inventaire 0-Quitter")
    choix = input("Choix : ")

    actions = {
        '1': 'haut',
        '2': 'bas',
        '3': 'gauche',
        '4': 'droite',
        '5': 'attaquer',
        '6': 'inventaire',
        '0': 'quitter'
    }
    action = actions.get(choix)

    #Arrêt du jeu
    if action == 'quitter':
        break

    elif action in ('haut', 'bas', 'gauche', 'droite'):
        jeu.deplacer_joueur(hero, action)
        jeu.verifier_ramassage_xp(hero)
        for m in jeu.liste_monstre:
            if isinstance(m, Monstre) and jeu.monstre_voit_hero(m):
                m.attaquer(hero)
                break

    elif action == 'attaquer':
        jeu.attaque_hero(hero)
    
    elif action == 'inventaire':
        hero.inventaire.afficher_inventaire()
        print("1 - Utiliser une potion | 2 - Changer d'arme | 0 - Retour")
        sub = input("Choix : ")
        
        if sub == '1':
            if not hero.inventaire.objets:
                print("Aucune potion disponible.")
            else:
                choix = input("Numéro de la potion (0 pour annuler) : ")
                if choix.isdigit() and 1 <= int(choix) <= len(hero.inventaire.objets):
                    choix = int(choix)
                    potion = hero.inventaire.objets.pop(choix - 1)
                    hero.hp = min(hero.hp + potion.soin, 100)
                    print(f"{hero.nom} utilise {potion.nom}. (HP: {hero.hp})")

        elif sub == '2':
            if not hero.inventaire.armes:
                print("Aucune arme disponible.")
            else:
                choix = input("Numéro de l'arme (0 pour annuler) : ")
                if choix.isdigit() and 1 <= int(choix) <= len(hero.inventaire.armes):
                    choix = int(choix)
                    ancienne_arme = hero.arme_actuelle
                    hero.arme_actuelle = hero.inventaire.armes.pop(choix - 1)
                    hero.inventaire.ajouter_arme(ancienne_arme)
                    print(f"Vous équipez {hero.arme_actuelle.nom}, Munitions: {hero.arme_actuelle.munitions}")
        
        input("\nAppuyez sur Entrée pour continuer...")