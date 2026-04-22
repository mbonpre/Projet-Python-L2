
class Inventaire:
    """ Classe représentant l'inventaire du joueur, qui peut contenir des objets et des armes."""
    def __init__(self):
        self.objets = []
        self.armes = []
    
    def ajouter_objet(self, objet):
        self.objets.append(objet)
    
    def ajouter_arme(self, arme):
        self.armes.append(arme)
    
    def afficher_inventaire(self):
        print("-"*20,"Inventaire:","-"*20)
        print("Potions :")
        if not self.objets:
            print("\t(aucune potion)")
        for i, objet in enumerate(self.objets):
            print(f"\t{i+1} - {objet.nom} (+{objet.soin} HP)")
        print("Armes:")
        if not self.armes:
            print("\t(aucune arme en stock)")
        for i, arme in enumerate(self.armes):
            print(f"\t{i+1} - {arme.nom} | Dégâts: {arme.degats} | Munitions: {arme.munitions}")

""" ---------------------------------------------------------------------------------------- """
class Arme:
    """ Classe représentant les armes """
    def __init__ (self, nom, degats,munitions):
        self.nom = nom
        self.degats = degats
        self.munitions = munitions

    def __repr__(self):
        return "{"+ self.nom + f",{self.degats}, {self.munitions}"+ "}"

""" ---------------------------------------------------------------------------------------- """
class Potion: 
    """ Classe représentant les potions de soin """
    def __init__(self, nom, soin):
        self.nom = nom
        self.soin = soin
    
    def __repr__(self):
        return f"[Potion: {self.nom}, +{self.soin} HP]"