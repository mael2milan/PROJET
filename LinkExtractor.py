

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class LinkExtractor:
    def extract_links(self, html_content, base_url):
        """
        Extrait tous les liens d'une page HTML.
        :param html_content: Contenu HTML de la page
        :param base_url: URL de base pour résoudre les liens relatifs
        :return: Liste des liens absolus
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
        return links

    def filter_links(self, links, extensions=None):
        """
        Filtre les liens par extension de fichier.
        :param links: Liste de liens à filtrer
        :param extensions: Extensions de fichiers valides (ex. ['.pdf', '.epub'])
        :return: Liste de liens filtrés
        """
        if extensions is None:
            return links
        return [link for link in links if any(link.lower().endswith(ext) for ext in extensions)]
