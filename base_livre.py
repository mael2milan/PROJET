


import PyPDF2

from ebooklib import epub

class base_livre:
  def __init__(self,ressource):
    """
        ressource désigne soit le nom de fichier (local) correspondant au livre,
        soit une URL pointant vers un livre.
    """
    raise NotImplementedError("à définir dans les sous-classes")

  def type(self):
    """ renvoie le type (EPUB, PDF, ou autre) du livre """
    raise NotImplementedError("à définir dans les sous-classes")

  def titre(self):
    """ renvoie le titre du livre """
    raise NotImplementedError("à définir dans les sous-classes")

  def auteur(self):
    """ renvoie l'auteur du livre """
    raise NotImplementedError("à définir dans les sous-classes")

  def langue(self):
    """ renvoie la langue du livre """
    raise NotImplementedError("à définir dans les sous-classes")

  def sujet(self):
    """ renvoie le sujet du livre """
    raise NotImplementedError("à définir dans les sous-classes")

  def date(self):
    """ renvoie la date de publication du livre """
    raise NotImplementedError("à définir dans les sous-classes")


# Sous-classe pour les livres PDF
class LivrePDF(base_livre):
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
            with open(self.ressource, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                if pdf_reader.metadata:
                    self._titre = pdf_reader.metadata.title or "Titre inconnu"
                    self._auteur = pdf_reader.metadata.author or "Auteur inconnu"
                    self._sujet = pdf_reader.metadata.subject or "Sujet inconnu"
                    self._date = pdf_reader.metadata["/CreationDate"] if "/CreationDate" in pdf_reader.metadata else "Date inconnue"
                    self._langue = "Langue inconnue" 
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées du PDF : {e}")

    def type(self):
        return "PDF"

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