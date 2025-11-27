#!/usr/bin/env python3
"""
Script de migración para convertir config.json a users_config.json
Ejecutar UNA VEZ antes de usar el sistema multi-usuario
"""

import json
import os
from datetime import datetime

def migrate():
    print("🔄 Iniciando migración a sistema multi-usuario...")
    
    # Verificar si ya existe users_config.json
    if os.path.exists("users_config.json"):
        response = input("⚠️  users_config.json ya existe. ¿Sobrescribir? (s/N): ")
        if response.lower() != 's':
            print("❌ Migración cancelada")
            return
    
    # Leer config.json antiguo si existe
    old_databases = {}
    old_current_alias = None
    
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                old_config = json.load(f)
            old_databases = old_config.get("databases", {})
            old_current_alias = old_config.get("current_db_alias")
            print(f"✅ Leído config.json: {len(old_databases)} BD(s)")
        except Exception as e:
            print(f"⚠️  Error leyendo config.json: {e}")
    else:
        print("ℹ️  No se encontró config.json, creando configuración nueva")
    
    # Crear users_config.json con usuario "default"
    # Este usuario usa las credenciales globales del .env
    users_config = {
        "default_user": {
            "gemini_api_key": None,  # Usará DEFAULT_GEMINI_API_KEY del .env
            "notion_token": None,     # Usará NOTION_INTEGRATION_TOKEN del .env
            "notion_databases": old_databases,
            "current_db_alias": old_current_alias,
            "created_at": datetime.now().isoformat(),
            "note": "Usuario default que usa credenciales globales del .env"
        }
    }
    
    # Guardar nueva configuración
    with open("users_config.json", "w") as f:
        json.dump(users_config, f, indent=2)
    
    print("✅ Migración completada exitosamente")
    print(f"📄 Creado: users_config.json")
    
    if os.path.exists("config.json"):
        # Hacer backup
        backup_name = f"config.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename("config.json", backup_name)
        print(f"📦 Backup creado: {backup_name}")
    
    print("\n📝 Próximos pasos:")
    print("1. Revisa users_config.json")
    print("2. Actualiza tu .env con DEFAULT_GEMINI_API_KEY (opcional)")
    print("3. Reinicia el bot")
    print("4. Los usuarios nuevos podrán configurar sus propias credenciales")

if __name__ == "__main__":
    migrate()
