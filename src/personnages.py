from objets import Inventaire, Arme, Potion

class Personnage: 
    """ Classe représentant un personnage dans le jeu. Classe mère des classes Hero et Monstre. 
    Elle contient les attributs et méthodes communs à tous les personnages du jeu. """
    def __init__(self, nom,hp,level):
        self.nom = nom
        self.hp = hp

        self.position = (1,1)
        self.level = level


""" ---------------------------------------------------------------------------------------- """
class Hero(Personnage):
    """ Classe représentant le héros du jeu. Hérite de la classe Personnage. """
    def __init__(self, nom, hp, level, arme_actuelle):
        super().__init__(nom, hp, level)
        self.experience = 0
        self.inventaire = Inventaire()
        self.arme_actuelle = arme_actuelle
    
    def gagner_experience(self, xp):
        """ Permet au héros de gagner de l'expérience en fonction des points d'expérience gagnés après avoir vaincu un monstre. """
        self.experience += xp
        print(f"  * {self.nom} gagne {xp} XP. (Total: {self.experience}/100)")
        if self.experience >= 100:
            self.level += 1
            self.experience = 0
            print(f"{self.nom} a gagné un niveau ! Niveau actuel : {self.level}")
    
    def utiliser_potion(self):
        """ Permet au héros d'utiliser une potion de soin depuis son inventaire. """
        if not self.inventaire.objets:
            print("  Vous n'avez aucune potion dans votre inventaire.")
            return
        self.inventaire.afficher_inventaire()
        choix = input("Entrez le numéro de la potion à utiliser (ou 0 pour annuler) : ")
        while not choix.isdigit() or not 1 <= choix <=inventaire.objets.len():
            print("  Choix invalide.Réessayez...")
            choix = input("Entrez le numéro de la potion à utiliser (ou 0 pour annuler) : ")
        choix = int(choix)
        if choix == 0:
            return
        potion = self.inventaire.objets.pop(choix - 1)
        self.hp = self.hp + potion.soin if self.hp + potion.soin < 100 else 100

        print(f"  {self.nom} utilise {potion.nom}. (HP: {self.hp})")

    def changer_arme(self):
        """ Permet au héros de changer d'arme depuis son inventaire. """
        if not self.inventaire.armes:
            print("  Vous n'avez aucune autre arme dans votre inventaire.")
            return
        self.inventaire.afficher_inventaire()
        choix = input("Entrez le numéro de l'arme à équiper (ou 0 pour annuler) : ")

        while not choix.isdigit() or not 1 <=choix <= self.inventaire.armes.len():
            print("  Choix invalide.Réessayez...")
            choix = input("Entrez le numéro de l'arme à équiper (ou 0 pour annuler) : ")
        choix = int(choix)
        if choix == 0:
            return
       
        # On échange l'arme courante avec celle choisie dans l'inventaire
        ancienne_arme = self.arme_actuelle
        self.arme_actuelle = self.inventaire.armes.pop(choix - 1)
        self.inventaire.ajouter_arme(ancienne_arme)
        print(f"  Vous équipez {self.arme_actuelle.nom} , Munitions: {self.arme_actuelle.munitions})")



    def ajouter_objet_inventaire(self, objet):
        """ Permet d'ajouter un objet à l'inventaire du héros. """
        self.inventaire.ajouter_objet(objet)

    def ajouter_arme_inventaire(self, arme):
        """ Permet d'ajouter une arme à l'inventaire du héros. """  
        self.inventaire.ajouter_arme(arme)
    
    def attaquer(self, monstre):
        """ Permet au héros d'attaquer un monstre en infligeant des dégâts en fonction de son arme actuelle. """
        if self.arme_actuelle.munitions > 0:
            monstre.hp -= self.arme_actuelle.degats
            self.arme_actuelle.munitions -= 1
            print(f"  Bang Bang. (HP monstre: {monstre.hp})")
        else:
            print(f"Click click {self.nom} n'a plus de munitions pour attaquer.")
            
    def afficher_stats(self):
        """ Affiche les statistiques du héros. """
        print(f"  [{self.nom}] HP: {self.hp}/100| Niveau: {self.level} | XP: {self.experience}/100 | Arme: {self.arme_actuelle.nom} ({self.arme_actuelle.munitions} munitions)")

""" ---------------------------------------------------------------------------------------- """

class Monstre(Personnage):
    """ Classe représentant un monstre dans le jeu. Hérite de la classe Personnage. """
    def __init__(self, nom, hp, level, xp_gagne, arme):
        super().__init__(nom, hp, level)
        self.xp_gagne = xp_gagne
        self.arme = arme
        self.position = (1,1)
        self.face = True #True = droite et False = gauche
    
    def attaquer(self, hero):
        """ Permet au monstre d'attaquer le héros en infligeant des dégâts en fonction de son arme. """
        if self.arme.munitions > 0:
            hero.hp -= self.arme.degats
            print(f"{self.nom} attaque {hero.nom} avec {self.arme.nom} HP héros: {hero.hp})")
            
    def __str__(self):
        return f"[{self.nom}, HP:{self.hp}, Niveau:{self.level}, Position:{self.position}, Arme:{self.arme}, Face:{self.face}]"
    def __repr__(self):
        return self.__str__()