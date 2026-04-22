import random
import copy
import os
import time
from personnages import Hero, Monstre
from objets import Inventaire, Arme, Potion

class EspaceJeu:

    def __init__(self, largeur, hauteur, niveau, hero, monstre_modele):
        self.largeur = largeur
        self.hauteur = hauteur
        self.niveau = niveau
        self.hero = hero
        self.monstre_modele = monstre_modele
        self.espace = self.creer_espace()
        self.liste_monstre = []

        self.compteur_tour = 0

        
          

    def creer_espace(self):
        """ Permet de créer le terrain du jeu, les couloir et les mûrs intérieur et extérieur """
        espace = [[' ' for _ in range(self.largeur)] for _ in range(self.hauteur)]

        #Mur extérieur
        for i in range(self.hauteur):
            for j in range(self.largeur):
                if i == 0 or i == self.hauteur - 1 or j == 0 or j == self.largeur - 1:
                    espace[i][j] = '#'

        #Mur intérieur avec des passages
        for i in range(2, self.hauteur - 2, 2):
            for j in range(self.largeur):
                espace[i][j] = '#'
            trou = random.randint(1, self.largeur - 2)
            espace[i][trou] = ' '

        return espace

    #Permet d'effacer la console à chaque nouvelle affichage pour que ça ait l'air d'un véritable jeu
    def effacer_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')


    def afficher_espace(self):
        self.effacer_console()
        self.hero.afficher_stats() #Statistique du joueur
        print()
    
        for ligne in self.espace: 
            for case in ligne:
                print(case, end=' ')
            print()


    def placer_monstre(self):
        """ Permet de placer les monstres aux hazard dans l'espace de jeu. Dans chaque couloir excepté la première couloir, qui est le couloir de départ """
        self.liste_monstre = []

        for i in range(3, self.hauteur - 1, 2):
            j = random.randint(2, self.largeur - 2)# A faire passer à 3
            m = Monstre(
                self.monstre_modele.nom,
                self.monstre_modele.hp,
                self.monstre_modele.level,
                self.monstre_modele.xp_gagne,
                copy.copy(self.monstre_modele.arme)
            )
            m.position = (i, j)
            m.face = True
            self.liste_monstre.append(m)
            self.espace[i][j] = '>'

    def placer_hero(self):
        """Permet de positionner l'hero dans l'espace du jeu en utilisant sont attribut position"""
        x, y = self.hero.position
        self.espace[x][y] = 'H'

    def deplacer_joueur(self, hero, direction):
        """ Pour le déplacement du joueur dans l'espace du jeu """
        x, y = hero.position

        deplacement = {
            'haut': (-1, 0),
            'bas': (1, 0),
            'gauche': (0, -1),
            'droite': (0, 1)
        }

        dx, dy = deplacement.get(direction, (0, 0))
        nx, ny = x + dx, y + dy #Nouvelle position 

        if self.espace[nx][ny] == '#':
            return

        self.espace[x][y] = ' '
        hero.position = (nx, ny)
        self.placer_hero()

    # ---------------- ROTATION ----------------

    def rotation_monstres(self):
        self.compteur_tour += 1

        if self.compteur_tour % 3 != 0:
            return

        for m in self.liste_monstre:
            if isinstance(m, Monstre):
                x, y = m.position

                # changer direction
                m.face = not m.face

                # mettre à jour la grille directement
                self.espace[x][y] = '>' if m.face else '<'
    """ ------------------------ POUR LA VISION --------------------------------- """
    def monstre_voit_hero(self, monstre):
        """ Permet de vérifier si le monstre vois le hero """
        ligne, col = monstre.position

        if monstre.face:
            for j in range(col, self.largeur):
                if self.espace[ligne][j] == '#':
                    break
                if self.espace[ligne][j] == 'H':
                    return True
        else:
            for j in range(col, -1, -1):
                if self.espace[ligne][j] == '#':
                    break
                if self.espace[ligne][j] == 'H':
                    return True
        return False


    def trouver_monstre_qui_voit_hero(self):
        """ Exécuter à chaque déplacement du joueurs pour vérifier si un monstre le voit ou pas """
        for m in self.liste_monstre:
            if isinstance(m, Monstre) and self.monstre_voit_hero(m):
                return m
        return None

    # ---------------- ATTAQUE ----------------

    def attaque_hero(self, hero):
        """ Lorsque le hero lance une attaque, la methode vérifie le monstre dans sont champ de vision, récupère
            ces coordonnées et fait des déduction d'hp
         """
        x, y = hero.position

        directions = [(0,1),(0,-1),(1,0),(-1,0)]

        for dx, dy in directions:
            i, j = x, y
            while True:
                i += dx
                j += dy

                if self.espace[i][j] == '#':
                    break

                if self.espace[i][j] in ('>', '<'):
                    m = self._trouver_monstre_par_position(i, j)
                    if m is None : 
                        break ; 
                    hero.attaquer(m)
                    #Vérifiez si le monstre est encore en vie ou pas
                    if m.hp <= 0:
                        self._monstre_mort(m)

                    return

        print("Aucun monstre...")

    def _trouver_monstre_par_position(self, x, y):
        """ Permet de trouver un monstre grâce à sa position dans l'espace de jeu """
        for m in self.liste_monstre:
            if isinstance(m, Monstre) and m.position == (x, y):
                return m


    def _monstre_mort(self, monstre):
        """ A la mort d'un monstre il se transforme en * qui lorsque consommé par le joueur lui permet de
            gagner des points d'expérience (XP). Et donc dans la liste de monstre , il est remplacé par un 
            dictionnaire. 
         """
        print(f"Aaarrg!!!{monstre.nom} est mort")
        x, y = monstre.position
        self.espace[x][y] = '*'
        indice = self.liste_monstre.index(monstre)
        self.liste_monstre[indice] = {'xp': monstre.xp_gagne, 'position': (x, y)}

    
    def verifier_ramassage_xp(self, hero):
        """ Vérifie si à la position actuelle de l'hero il n'y a pas une * à ramasser avant de l'y placer. Si 
            il y en a, il gagne des points d'expérience. 
         """
        x, y = hero.position

        for index, e in enumerate(self.liste_monstre):
            if isinstance(e, dict) and e['position'] == (x, y):
                hero.gagner_experience(e['xp'])
                self.liste_monstre[index] = None
                self.espace[x][y] = ' '
                self.placer_hero()