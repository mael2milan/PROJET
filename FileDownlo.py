#!/usr/bin/env python3

import os
import requests
from urllib.parse import urlparse

class FileDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder
        os.makedirs(self.download_folder, exist_ok=True)
    
    def download_file(self, file_url):
        """
        Télécharge un fichier depuis une URL et le sauvegarde localement.
        :param file_url: URL du fichier à télécharger
        :return: Chemin du fichier téléchargé ou None en cas d'échec
        """
        try:
            response = requests.get(file_url, stream=True, timeout=10)
            response.raise_for_status()
            
            filename = os.path.basename(urlparse(file_url).path)
            file_path = os.path.join(self.download_folder, filename)
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            print(f"Downloaded: {filename} -> {file_path}")
            return file_path
        except (requests.RequestException, IOError) as e:
            print(f"Failed to download {file_url}: {e}")
            return None
