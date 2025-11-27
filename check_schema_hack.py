import os
from notion_client import Client
from dotenv import load_dotenv
import config_manager
import json

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_INTEGRATION_TOKEN")

def check_schema():
    print("--- INICIO CHECK SCHEMA ---")
    if not NOTION_TOKEN:
        print("Error: No hay token configurado.")
        return

    db_id = config_manager.get_current_database_id()
    if not db_id:
        print("Error: No hay base de datos configurada.")
        return

    notion = Client(auth=NOTION_TOKEN)
    
    print(f"Usando ID: {db_id}")
    
    try:
        # 1. Create dummy page
        print("Creando página de prueba...")
        new_page = notion.pages.create(
            parent={"database_id": db_id},
            properties={
                "Name": { # Assuming 'Name' exists, usually safe. If fails, we'll know.
                    "title": [
                        {
                            "text": {
                                "content": "Test Schema Check"
                            }
                        }
                    ]
                }
            }
        )
        
        print("✅ Página creada. ID:", new_page["id"])
        
        # 2. Inspect properties in response
        print("\n🔍 Propiedades detectadas:")
        props = new_page.get("properties", {})
        for name, prop in props.items():
            prop_type = prop.get("type")
            print(f"- Nombre: '{name}' | Tipo: {prop_type}")
            
            # Print options for selects
            if prop_type == "select":
                # Select options are not in page response, sadly. They are in DB schema.
                # But we can at least know the column exists.
                pass
        
        # 3. Archive page
        print("\nBorrando página de prueba...")
        notion.pages.update(page_id=new_page["id"], archived=True)
        print("✅ Página borrada.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if "Name is not a property" in str(e):
            print("💡 PISTA: La propiedad de título no se llama 'Name'.")

    print("--- FIN CHECK SCHEMA ---")

if __name__ == "__main__":
    check_schema()
