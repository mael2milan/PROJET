
import PyPDF2
from ebooklib import epub
from base_livre import base_livre


class base_bibli:
  def __init__(self,path):
    """ path désigne le répertoire contenant les livres de cette bibliothèque """
    raise NotImplementedError("à définir dans les sous-classes")

  def ajouter(self,livre):
    """
      Ajoute le livre à la bibliothèque """
    raise NotImplementedError("à définir dans les sous-classes")

  def rapport_livres(self,format,fichier):
    """
        Génère un état des livres de la bibliothèque.
        Il contient la liste des livres,
        et pour chacun d'eux
        son titre, son auteur, son type (PDF ou EPUB), et le nom du fichier correspondant.

        format: format du rapport (PDF ou EPUB)
        fichier: nom du fichier généré
    """
    raise NotImplementedError("à définir dans les sous-classes")

  def rapport_auteurs(self,format,fichier):
    """
        Génère un état des auteurs des livres de la bibliothèque.
        Il contient pour chaque auteur
        le titre de ses livres en bibliothèque et le nom du fichier correspondant au livre.
        le type (PDF ou EPUB),
        et le nom du fichier correspondant.

        format: format du rapport (PDF ou EPUB)
        fichier: nom du fichier généré
    """
    raise NotImplementedError("à définir dans les sous-classes")
  

# Sous classe

class simple_bibli(base_bibli):
    def init(self, path):
        """
        Initialise la bibliothèque avec un chemin vers le répertoire
        contenant les livres de cette bibliothèque.
        """
        self.path = path  # Chemin du répertoire des livres
        self.livres = []  # Liste pour stocker les livres

    def ajouter(self, livre):
        """
        Ajoute le livre à la bibliothèque.
        """
        if isinstance(livre, base_livre):
            self.livres.append(livre)
            print(f"Livre ajouté : {livre.titre()} ({livre.type()})")
        else:
            print("Erreur : l'objet ajouté n'est pas un type de livre valide.")

    def rapport_livres(self, format, fichier):
        """
        Génère un rapport des livres dans la bibliothèque.
        """
        # le rapport pourrait être sauvegardé dans un fichier dans le futur.
        print(f"Génération du rapport des livres en format {format} dans le fichier {fichier} :")
        for livre in self.livres:
            print(f"- Titre : {livre.titre()}, Auteur : {livre.auteur()}, Type : {livre.type()}")

    def rapport_auteurs(self, format, fichier):
        """
        Génère un rapport des auteurs et de leurs livres.
        """
        print(f"Génération du rapport des auteurs en format {format} dans le fichier {fichier} :")
        auteurs = {}
        for livre in self.livres:
            if livre.auteur() not in auteurs:
                auteurs[livre.auteur()] = []
            auteurs[livre.auteur()].append(livre)

        for auteur, livres in auteurs.items():
            print(f"Auteur : {auteur}")
            for livre in livres:
                print(f"    - Titre : {livre.titre()}, Type : {livre.type()}")




# Sous-classe pour les livres EPUB
class LivreEPUB(base_livre):
    def __init__(self, ressource):
        self.ressource = ressource
        self._titre = None
        self._auteur = None
        self._langue = None
        self._sujet = None
        self._date = None
        self.extraire_metadonnees()

    def extraire_metadonnees(self):
        try:
            book = epub.read_epub(self.ressource)
            metadata = book.get_metadata("DC", {})
            
            self._titre = metadata.get('title', ["Titre inconnu"])[0]
            self._auteur = metadata.get('creator', ["Auteur inconnu"])[0]
            self._langue = metadata.get('language', ["Langue inconnue"])[0]
            self._sujet = metadata.get('subject', ["Sujet inconnu"])[0]
            self._date = metadata.get('date', ["Date inconnue"])[0]
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées de l'EPUB : {e}")

    def type(self):
        return "EPUB"

    def titre(self):
        return self._titre

    def auteur(self):
        return self._auteur

    def langue(self):
        return self._langue

    def sujet(self):
        return self._sujet

    def date(self):
        return self._date