import os
import subprocess
import json
import uuid
import minecraft_launcher_lib
import requests

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_MINECRAFT_DIR = os.path.join(BASE_DIR, ".minecraft")
INSTALLER_URL = "https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.234/neoforge-21.1.234-installer.jar"
INSTALLER_NAME = "neoforge-installer.jar"
VERSION_VANILLA = "1.21.1"
# URL standard Yggdrasil pour LittleSkin
LITTLE_SKIN_AUTH_URL = "https://littleskin.cn/api/yggdrasil/authserver"

def setup_tout_en_un():
    os.makedirs(LOCAL_MINECRAFT_DIR, exist_ok=True)
    
    # 1. Profil requis par l'installeur
    profile_path = os.path.join(LOCAL_MINECRAFT_DIR, "launcher_profiles.json")
    if not os.path.exists(profile_path):
        with open(profile_path, "w") as f:
            json.dump({"profiles": {}, "settings": {}}, f)

    # 2. Vérification Vanilla
    version_dir = os.path.join(LOCAL_MINECRAFT_DIR, "versions", VERSION_VANILLA)
    if not os.path.exists(version_dir):
        print(f"Installation de la version {VERSION_VANILLA}...")
        minecraft_launcher_lib.install.install_minecraft_version(VERSION_VANILLA, LOCAL_MINECRAFT_DIR)
    
    # 3. Installation NeoForge
    versions_dir = os.path.join(LOCAL_MINECRAFT_DIR, "versions")
    forge_installed = any("neoforge" in folder.lower() for folder in os.listdir(versions_dir))
    
    if not forge_installed:
        installer_path = os.path.join(BASE_DIR, INSTALLER_NAME)
        print("Téléchargement de l'installeur NeoForge...")
        with requests.get(INSTALLER_URL, stream=True) as r:
            with open(installer_path, 'wb') as f:
                f.write(r.content)
        
        print("Exécution de l'installeur NeoForge...")
        subprocess.run(["java", "-jar", installer_path, "--installClient", LOCAL_MINECRAFT_DIR], check=True)
        print("Installation NeoForge terminée.")

def lancer_jeu(mode, username=None, password=None):
    versions_dir = os.path.join(LOCAL_MINECRAFT_DIR, "versions")
    version_id = next(f for f in os.listdir(versions_dir) if "neoforge" in f.lower())
    
    options = {"username": username, "uuid": str(uuid.uuid4()), "token": "0"}

    if mode == "2":
        print("Authentification sur LittleSkin...")
        payload = {
            "agent": {"name": "Minecraft", "version": 1},
            "username": username,
            "password": password,
            "clientToken": str(uuid.uuid4())
        }
        headers = {'Content-Type': 'application/json'}
        
        try:
            resp = requests.post(f"{LITTLE_SKIN_AUTH_URL}/authenticate", json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                options["username"] = data["selectedProfile"]["name"]
                options["uuid"] = data["selectedProfile"]["id"]
                options["token"] = data["accessToken"]
                print(f"✅ Connecté en tant que {options['username']}")
            else:
                print(f"❌ Erreur {resp.status_code} : {resp.text}")
                return
        except Exception as e:
            print(f"❌ Erreur réseau : {e}")
            return

    print(f"Lancement de {version_id}...")
    command = minecraft_launcher_lib.command.get_minecraft_command(version_id, LOCAL_MINECRAFT_DIR, options)
    subprocess.Popen(command)

if __name__ == "__main__":
    print("--- NEBU CLIENT (V1) ---\nDesciptions:\nNebuCLient et le Client Officiel pour rejoindre le serveur NebulaSMP \nPetit Conseil dans #Code du server discord taper LEOLEGOAT2026 pour 1 Lvl offert :) .\n\nBy Astra and Leo (C).copyright 2026-2027")
    setup_tout_en_un()
    
    print("\nModes : 1 = Officiel Microsoft | 2 = Crack / LittleSkin | 3 = Offline")
    mode = input("Ton choix (1,2 ou 3) / Your choice one,two or 3 : ")
    
    if mode == "2":
        pseudo = input("Email/Pseudo LittleSkin / Mail/ Pseudo LittleSkin : ")
        mdp = input("Mot de passe / password: ")
        lancer_jeu(mode, pseudo, mdp)
    else:
        pseudo = input("Pseudo : ")
        lancer_jeu(mode, pseudo)
    if mode == "3":
        print("Warning Mode Test Tu ne poura pas rejoindre le server / Warning Test mode you can't join server")
        speudo = input("Speudo ? : ")
        lancer_jeu(mode, speudo)
