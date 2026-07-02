import sys
import os
import base64
import json
import requests
import psutil
import subprocess
import shlex
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self):
        self.key_file = "secret.key"
        self.filename = "session.data"
        if not os.path.exists(self.key_file):
            with open(self.key_file, "wb") as f: f.write(Fernet.generate_key())
        with open(self.key_file, "rb") as f: self.cipher = Fernet(f.read())

    def save_session(self, uuid, token):
        try:
            raw = f"{uuid}:{token}".encode()
            b64_data = base64.b64encode(raw)
            with open(self.filename, "wb") as f: f.write(self.cipher.encrypt(b64_data))
        except Exception as e:
            print(f"Erreur stockage: {e}")

class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CookiesMP Launcher")
        self.setFixedSize(900, 600)
        self.init_ui()

    def init_ui(self):
        # ... (UI reste similaire)
        pass

    def start_process(self):
        # Sécurisation : Utilisation d'un dictionnaire pour les paramètres
        auth = self.little_skin_login("user", "pass")
        if not auth:
            QMessageBox.critical(self, "Erreur", "Authentification échouée")
            return

        uuid = auth.get('selectedProfile', {}).get('id')
        token = auth.get('accessToken')
        
        # 1. Stockage sécurisé
        SecureStorage().save_session(uuid, token)
        
        # 2. Lancement sécurisé (Évite le fichier .bat manipulable)
        ram = "8G" if (psutil.virtual_memory().total // (1024**3)) >= 16 else "4G"
        
        # Commande construite via liste (sécurité contre injection shell)
        cmd = [
            "java", f"-Xmx{ram}", "-jar", "client.jar",
            "--username", auth['selectedProfile']['name'],
            "--accessToken", token
        ]
        
        try:
            # Lancement sans passer par un fichier .bat intermédiaire
            subprocess.Popen(cmd, shell=False)
            print("Processus lancé.")
        except Exception as e:
            print(f"Erreur lancement: {e}")
        
        # 3. Nettoyage mémoire
        del token
        del uuid

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Launcher()
    window.show()
    sys.exit(app.exec())
