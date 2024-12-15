#!/usr/bin/env python3

import argparse
import configparser
import os
from bibli_scrap import bibli_scrap
from simple_bibli import simple_bibli

def lire_configuration(fichier_conf):
    """
    Lit le fichier de configuration et retourne les paramètres sous forme de dictionnaire.
    """
    config = configparser.ConfigParser()
    config.read(fichier_conf)
    return {
        'bibliotheque': config['DEFAULT']['bibliotheque'],
        'etats': config['DEFAULT']['etats'],
        'nbmax': int(config['DEFAULT']['nbmax'])
    }

def collecte(url, profondeur, config):
    """
    Lance une collecte de livres depuis l'URL donnée jusqu'à une certaine profondeur.
    """
    download_folder = config['bibliotheque']
    bibliotheque = bibli_scrap(download_folder=download_folder)
    bibliotheque.scrap(url, profondeur, config['nbmax'])
    print(f"Collecte terminée. Les livres sont enregistrés dans {download_folder}.")

def generation_rapports(config):
    """
    Génère les rapports des livres et des auteurs en PDF et EPUB.
    """
    chemin_bibli = config['bibliotheque']
    chemin_etats = config['etats']
    bibliotheque = simple_bibli(chemin_bibli)
    
    # Rapports des livres
    rapport_livres_pdf = os.path.join(chemin_etats, "rapport_livres.pdf")
    rapport_livres_epub = os.path.join(chemin_etats, "rapport_livres.epub")
    bibliotheque.rapport_livres("PDF", rapport_livres_pdf)
    bibliotheque.rapport_livres("EPUB", rapport_livres_epub)
    
    # Rapports des auteurs
    rapport_auteurs_pdf = os.path.join(chemin_etats, "rapport_auteurs.pdf")
    rapport_auteurs_epub = os.path.join(chemin_etats, "rapport_auteurs.epub")
    bibliotheque.rapport_auteurs("PDF", rapport_auteurs_pdf)
    bibliotheque.rapport_auteurs("EPUB", rapport_auteurs_epub)
    
    print(f"Les rapports ont été générés dans {chemin_etats}.")

def main():
    # Argument parser pour gérer les options en ligne de commande
    parser = argparse.ArgumentParser(description="Application de gestion de bibliothèque.")
    parser.add_argument("-c", "--config", default="bibli.conf", help="Spécifie le fichier de configuration.")
    parser.add_argument("action", choices=["url", "rapports"], help="Action à effectuer : collecte depuis une URL ou génération de rapports.")
    parser.add_argument("param", nargs="?", help="Paramètre additionnel (URL ou profondeur).")

    args = parser.parse_args()

    # Lire le fichier de configuration
    config = lire_configuration(args.config)
    # Actions
    if args.action == "url":
        if not args.param:
            print("Erreur : Une URL est nécessaire pour l'action 'url'.")
            return
        profondeur = 1  # Profondeur par défaut
        if args.param.isdigit():
            profondeur = int(args.param)
            print(f"Profondeur définie sur {profondeur}.")
        else:
            print(f"URL détectée : {args.param}")
            collecte(args.param, profondeur, config)
    elif args.action == "rapports":
        generation_rapports(config)
    else:
        print("Action inconnue. Utilisez 'url' ou 'rapports'.")

if __name__ == "__main__":
    main()





