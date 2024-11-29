

from simple_bibli import base_bibli, simple_bibli

chemin_livres = r"C:\Users\diaou\OneDrive\Bureau\Pyhon M1 DS\Collecte_de_livres\Livre"
bibliotheque = simple_bibli(chemin_livres)

# Générer un rapport des livres
rapport_livres_fichier = r"C:\Users\diaou\OneDrive\Bureau\Pyhon M1 DS\Collecte_de_livres\Livre\rapport_livres.txt"
bibliotheque.rapport_livres("TXT", rapport_livres_fichier)

# Générer un rapport des auteurs
rapport_auteurs_fichier = r"C:\Users\diaou\OneDrive\Bureau\Pyhon M1 DS\Collecte_de_livres\Livre\rapport_auteurs.txt"
bibliotheque.rapport_auteurs("TXT", rapport_auteurs_fichier)

print("Les rapports ont été générés avec succès !")