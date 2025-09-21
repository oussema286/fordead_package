#!/usr/bin/env python3
"""
Configuration pour l'authentification Copernicus
"""

import os
from pathlib import Path

def setup_copernicus_auth():
    """
    Configurer l'authentification Copernicus pour phidown
    """
    
    # Méthode 1: Variables d'environnement
    username = os.getenv('COPERNICUS_USERNAME')
    password = os.getenv('COPERNICUS_PASSWORD')
    client_id = os.getenv('COPERNICUS_CLIENT_ID')
    client_secret = os.getenv('COPERNICUS_CLIENT_SECRET')
    
    if username and password:
        print("✅ Identifiants Copernicus trouvés dans les variables d'environnement")
        return {
            'username': username,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret
        }
    
    # Méthode 2: Fichier de configuration local
    config_file = Path(__file__).parent / 'copernicus_credentials.txt'
    
    if config_file.exists():
        print("✅ Fichier de configuration Copernicus trouvé")
        with open(config_file, 'r') as f:
            lines = f.readlines()
            credentials = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    credentials[key.strip()] = value.strip()
            return credentials
    
    # Méthode 3: Demander à l'utilisateur
    print("❌ Aucun identifiant Copernicus trouvé")
    print("\n📋 Pour utiliser phidown, vous devez :")
    print("1. Créer un compte sur https://dataspace.copernicus.eu/")
    print("2. Configurer vos identifiants de l'une des façons suivantes :")
    print("\n   Option A - Variables d'environnement :")
    print("   export COPERNICUS_USERNAME='votre_username'")
    print("   export COPERNICUS_PASSWORD='votre_password'")
    print("\n   Option B - Fichier de configuration :")
    print(f"   Créer le fichier : {config_file}")
    print("   Contenu :")
    print("   COPERNICUS_USERNAME=votre_username")
    print("   COPERNICUS_PASSWORD=votre_password")
    print("   COPERNICUS_CLIENT_ID=votre_client_id")
    print("   COPERNICUS_CLIENT_SECRET=votre_client_secret")
    
    return None

def create_credentials_template():
    """
    Créer un template de fichier de credentials
    """
    template_content = """# Configuration Copernicus pour phidown
# Remplacez les valeurs par vos identifiants réels

COPERNICUS_USERNAME=votre_username_ici
COPERNICUS_PASSWORD=votre_password_ici
COPERNICUS_CLIENT_ID=votre_client_id_ici
COPERNICUS_CLIENT_SECRET=votre_client_secret_ici

# Instructions :
# 1. Créez un compte sur https://dataspace.copernicus.eu/
# 2. Remplacez les valeurs ci-dessus par vos identifiants
# 3. Ne partagez jamais ce fichier (ajoutez-le à .gitignore)
"""
    
    config_file = Path(__file__).parent / 'copernicus_credentials_template.txt'
    with open(config_file, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Template créé : {config_file}")
    return config_file

if __name__ == "__main__":
    # Créer le template
    create_credentials_template()
    
    # Tester la configuration
    auth = setup_copernicus_auth()
    if auth:
        print("🎉 Configuration Copernicus prête !")
    else:
        print("⚠️ Configuration Copernicus requise")

