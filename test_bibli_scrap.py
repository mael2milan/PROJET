from bibli_scrap import bibli_scrap


url = "https://math.univ-angers.fr/~jaclin/biblio/livres/"
scraper = bibli_scrap()
scraper.scrap(url, profondeur=1, nbmax=10)