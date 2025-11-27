import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import gemini_service
import notion_service
import user_config_manager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    has_config = user_config_manager.has_user_config(user_id)
    
    if not has_config:
        text = """
🎉 **¡Bienvenido a Cerebro Bot!**

Para empezar, configura tus credenciales:

⚙️ Usa `/config` para ver opciones

💡 Tus datos son **privados** y seguros.
"""
    else:
        text = """
🤖 **Cerebro Bot - Tu Asistente Personal**

📝 **Crear Tareas:**
• `/plan <descripción>` - Crea tarea
• 🎙️ Nota de voz - Crea desde audio

🔍 **Buscar y Editar:**
• `/buscar <término>` - Busca tareas
• `/editar <ID> <cambios>` - Edita tarea

💬 **Conversar:**
• Envía cualquier mensaje

⚙️ **Configuración:**
• `/config` - Tu configuración
• `/add_db <alias> <id>` - Añadir BD
• `/list_dbs` - Ver BDs

❓ `/help` - Ver ayuda
"""
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Configuración", callback_data='show_config')],
        [
            InlineKeyboardButton("📝 Crear", callback_data='help_plan'),
            InlineKeyboardButton("🔍 Buscar", callback_data='help_search')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menú de configuración personal."""
    user_id = update.effective_user.id
    user_cfg = user_config_manager.get_user_config(user_id)
    
    has_gemini = bool(user_cfg and user_cfg.get("gemini_api_key"))
    has_notion = bool(user_cfg and user_cfg.get("notion_token"))
    num_dbs = len(user_cfg.get("notion_databases", {})) if user_cfg else 0
    
    text = f"""
⚙️ **Tu Configuración Personal**

🤖 Gemini: {'✅ Configurado' if has_gemini else '❌ No configurado'}
📊 Notion: {'✅ Configurado' if has_notion else '❌ No configurado'}
🗄️ Bases de datos: {num_dbs}

**Comandos:**
• `/set_gemini <api_key>` - Configura Gemini
• `/set_notion <token>` - Configura Notion
• `/add_db <alias> <id>` - Añade BD
• `/setup_notion` - 📖 Guía paso a paso
• `/list_dbs` - Ver tus BDs
• `/reset_config` - Borrar configuración

💡 Tus credenciales son **privadas**.

**Obtener credenciales:**
• Gemini: https://aistudio.google.com/apikey
• Notion: https://www.notion.so/my-integrations
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def set_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configura la API key de Gemini del usuario."""
    user_id = update.effective_user.id
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "Uso: `/set_gemini <tu_api_key>`\n\n"
            "Obtén tu clave en: https://aistudio.google.com/apikey",
            parse_mode='Markdown'
        )
        return
    
    api_key = context.args[0]
    user_config_manager.set_user_gemini_key(user_id, api_key)
    
    # Borrar mensaje del usuario por seguridad
    try:
        await update.message.delete()
    except:
        pass
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Tu API key de Gemini fue configurada.\n"
             "🔒 El mensaje fue borrado por seguridad."
    )

async def set_notion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configura el token de Notion del usuario."""
    user_id = update.effective_user.id
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "Uso: `/set_notion <tu_token>`\n\n"
            "Obtén tu token en: https://www.notion.so/my-integrations",
            parse_mode='Markdown'
        )
        return
    
    notion_token = context.args[0]
    user_config_manager.set_user_notion_token(user_id, notion_token)
    
    # Borrar mensaje del usuario por seguridad
    try:
        await update.message.delete()
    except:
        pass
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Tu token de Notion fue configurado.\n"
             "🔒 El mensaje fue borrado por seguridad.\n\n"
             "Ahora añade una base de datos con `/add_db`"
    )

async def reset_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina la configuración del usuario."""
    user_id = update.effective_user.id
    
    if user_config_manager.delete_user_config(user_id):
        await update.message.reply_text("✅ Tu configuración fue eliminada.")
    else:
        await update.message.reply_text("ℹ️ No tienes configuración guardada.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'show_config':
        user_id = update.effective_user.id
        user_cfg = user_config_manager.get_user_config(user_id)
        
        has_gemini = bool(user_cfg and user_cfg.get("gemini_api_key"))
        has_notion = bool(user_cfg and user_cfg.get("notion_token"))
        
        text = f"""
⚙️ **Configuración**

🤖 Gemini: {'✅' if has_gemini else '❌'}
📊 Notion: {'✅' if has_notion else '❌'}

Usa `/config` para más detalles
"""
        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        return
    
    help_texts = {
        'help_plan': """📝 **Crear Tareas**

**Texto:**
`/plan <descripción>`

Ejemplo:
`/plan Reunión mañana tipo:Negocio`

**Voz 🎙️:**
Presiona micrófono y di la tarea
""",
        'help_search': """🔍 **Buscar**

`/buscar <término>`

Ejemplo:
`/buscar reunión`

Muestra título, link e ID
""",
        'help_edit': """✏️ **Editar**

1. `/buscar <término>`
2. Copia el ID
3. `/editar <ID> campo:valor`

Ejemplo:
`/editar abc123 estado:Completado`
"""
    }
    
    text = help_texts.get(query.data, "Ayuda no disponible")
    keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text_to_plan = ' '.join(context.args)
    
    if not text_to_plan:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ejemplo: /plan Comprar leche mañana"
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🧠 Analizando..."
    )

    task_info = gemini_service.extract_task_info(text_to_plan, user_id)
    result = notion_service.create_page(
        title=task_info.get("title"),
        user_id=user_id,
        description=task_info.get("description"),
        date=task_info.get("date"),
        status=task_info.get("status"),
        type_val=task_info.get("type_val")
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result
    )

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = ' '.join(context.args)
    
    if not query:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Uso: /buscar <término>"
        )
        return
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🔍 Buscando '{query}'..."
    )
    
    results = notion_service.search_pages(query, limit=10)
    
    if not results:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"No encontré tareas con '{query}'"
        )
        return
    
    msg = f"📋 Encontré {len(results)} tarea(s):\n\n"
    for i, task in enumerate(results, 1):
        msg += f"{i}. {task['title']}\n"
        msg += f"   🔗 {task['url']}\n"
        msg += f"   ID: `{task['id']}`\n\n"
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode='Markdown'
    )

async def editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Uso: /editar <ID> titulo:X estado:Y"
        )
        return
    
    page_id = context.args[0]
    changes_text = ' '.join(context.args[1:])
    
    import re
    import date_utils
    
    updates = {}
    patterns = {
        "titulo": r'titulo:([^estado:fecha:tipo:]+)',
        "status": r'estado:(\w+)',
        "date": r'fecha:([\w\s-]+)',
        "type_val": r'tipo:(\w+)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, changes_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if key == "titulo":
                updates["title"] = value
            elif key == "date":
                parsed_date = date_utils.parse_spanish_date(value)
                if parsed_date:
                    updates["date"] = parsed_date
            else:
                updates[key] = value
    
    if not updates:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Usa: titulo:X estado:Y fecha:Z"
        )
        return
    
    result = notion_service.update_page(page_id, **updates)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result
    )

async def add_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) != 2:
        guide_text = """
📊 **Cómo Configurar tu Base de Datos de Notion**

**Paso 1: Crear Integración**
1. Ve a https://www.notion.so/my-integrations
2. Haz clic en "+ New integration"
3. Dale un nombre (ej: "Cerebro Bot")
4. Copia el **Integration Token** (secret_...)
5. Úsalo con: `/set_notion secret_...`

**Paso 2: Compartir Base de Datos**
1. Abre tu base de datos en Notion
2. Haz clic en "⋯" (arriba derecha)
3. Selecciona "Connections"
4. Busca y selecciona tu integración

**Paso 3: Obtener ID de la Base de Datos**

Desde la **URL de tu base de datos**:
```
https://notion.so/workspace/ESTE_ES_EL_ID?v=...
```

El ID es el código entre la última `/` y el `?`

**Ejemplo de URL:**
```
https://notion.so/miworkspace/34002516d51380a8...?v=abc
                            ↑ Copia desde aquí hasta el ?
```

**Paso 4: Añadir al Bot**
Una vez tengas el ID, usa:
```
/add_db personal 34002516d51380a8...
```

**Formato:**
`/add_db <alias> <database_id>`

• **alias**: Nombre corto (trabajo, personal, etc.)
• **database_id**: El ID que copiaste

💡 **Tip:** Puedes tener múltiples BDs y cambiar entre ellas con `/set_db <alias>`

¿Necesitas ayuda? Usa `/setup_notion` para una guía visual.
"""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=guide_text,
            parse_mode='Markdown'
        )
        return
    
    alias, db_id = context.args[0], context.args[1]
    
    # Limpiar el ID (quitar guiones si los tiene)
    db_id = db_id.replace("-", "")
    
    if user_config_manager.add_user_database(user_id, alias, db_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ BD '{alias}' guardada correctamente\n\n"
                 f"Usa `/set_db {alias}` para activarla\n"
                 f"O `/list_dbs` para ver todas tus BDs"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error al guardar la base de datos"
        )

async def setup_notion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guía detallada para configurar Notion."""
    guide = """
🎯 **Guía Completa: Configurar Notion con el Bot**

**🔧 PARTE 1: Crear la Integración**

1. Abre https://www.notion.so/my-integrations
2. Click en **"+ New integration"**
3. Configuración:
   • Name: "Cerebro Bot" (o el que quieras)
   • Associated workspace: Tu workspace
   • Type: Internal
4. Click **"Submit"**
5. Copia el **Internal Integration Token**
   (Empieza con `secret_...`)
6. En Telegram, envía:
   ```
   /set_notion secret_tu_token_aqui
   ```
   _(El mensaje se borrará automáticamente)_

**📊 PARTE 2: Compartir tu Base de Datos**

1. Abre la base de datos en Notion
2. Click en **"⋯"** (esquina superior derecha)
3. Selecciona **"Connections"** o **"Add connections"**
4. Busca **"Cerebro Bot"** (o el nombre que pusiste)
5. Click para conectar

**🔑 PARTE 3: Obtener el ID**

**Opción A - Desde la URL:**
```
https://notion.so/workspace/ABC123DEF456?v=xyz
                            ↑ Copia esto
```

**Opción B - Copiar link:**
1. Click derecho en la base de datos
2. "Copy link"
3. Pega el link, se verá así:
   `https://notion.so/ABC123DEF456?v=xyz`
4. Copia el código entre `.so/` y `?v=`

**✅ PARTE 4: Añadir al Bot**

Con el ID copiado, envía:
```
/add_db personal ABC123DEF456
```

Donde:
• `personal` = alias (elige el que quieras)
• `ABC123DEF456` = el ID que copiaste

**🎉 ¡Listo!**

Ahora puedes:
• `/plan Comprar leche mañana` - Crear tareas
• `/list_dbs` - Ver tus bases de datos
• `/set_db otro_alias` - Cambiar entre BDs

**🆘 Problemas Comunes:**

❌ "Could not find database"
→ Asegúrate de compartir la BD con la integración

❌ "Invalid database ID"
→ Verifica que copiaste el ID completo

❌ "Property not found"
→ Tu BD necesita estas columnas:
  • Name (título)
  • descripcion (texto)
  • Fecha de Inicio (fecha)
  • Estado del Proyecto (select)
  • Tipo (texto)
"""
    
    await update.message.reply_text(guide, parse_mode='Markdown')

async def set_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Formato: /set_db <alias>"
        )
        return
    
    alias = context.args[0]
    
    if user_config_manager.set_user_current_database(user_id, alias):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ BD activa: '{alias}'"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Alias '{alias}' no encontrado"
        )

async def list_dbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dbs = user_config_manager.get_user_databases(user_id)
    current = user_config_manager.get_user_current_alias(user_id)
    
    if not dbs:
        msg = "No tienes BDs configuradas.\nUsa /add_db para añadir una."
    else:
        msg = "🗄️ Tus bases de datos:\n\n"
        for alias, db_id in dbs.items():
            status = " ✅" if alias == current else ""
            msg += f"• {alias}{status}\n"
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # Mostrar "escribiendo..." mientras procesa
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    try:
        response = gemini_service.get_chat_response(user_text, user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response
        )
    except Exception as e:
        logger.error(f"Error en chat: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error al conectar con Gemini. Intenta de nuevo."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("🎙️ Procesando...")
    
    voice_file_path = None
    try:
        voice_file = await update.message.voice.get_file()
        voice_file_path = f"voice_{update.message.voice.file_unique_id}.ogg"
        await voice_file.download_to_drive(voice_file_path)
        
        transcription = gemini_service.transcribe_audio(voice_file_path, user_id)
        
        if not transcription:
            await update.message.reply_text("❌ Error transcribiendo")
            return
        
        task_info = gemini_service.extract_task_info(transcription, user_id)
        
        result = notion_service.create_page(
            title=task_info.get("title"),
            user_id=user_id,
            description=task_info.get("description"),
            date=task_info.get("date"),
            status=task_info.get("status"),
            type_val=task_info.get("type_val")
        )
        
        await update.message.reply_text(
            f"✅ Tarea creada\n\n"
            f"📝 *Transcripción:* _{transcription}_\n\n"
            f"{result}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Error en voz: {e}", exc_info=True)
        await update.message.reply_text("❌ Error procesando voz")
    finally:
        if voice_file_path and os.path.exists(voice_file_path):
            os.remove(voice_file_path)

import keep_alive

if __name__ == '__main__':
    # Iniciar servidor web para keep-alive
    keep_alive.keep_alive()
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado")
    else:
        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Comandos
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', help_command))
        application.add_handler(CommandHandler('config', config))
        application.add_handler(CommandHandler('set_gemini', set_gemini))
        application.add_handler(CommandHandler('set_notion', set_notion))
        application.add_handler(CommandHandler('setup_notion', setup_notion))
        application.add_handler(CommandHandler('reset_config', reset_config))
        application.add_handler(CommandHandler('plan', plan))
        application.add_handler(CommandHandler('buscar', buscar))
        application.add_handler(CommandHandler('editar', editar))
        application.add_handler(CommandHandler('add_db', add_db))
        application.add_handler(CommandHandler('set_db', set_db))
        application.add_handler(CommandHandler('list_dbs', list_dbs))
        
        # Botones
        application.add_handler(CallbackQueryHandler(button_callback, pattern='^help_'))
        application.add_handler(CallbackQueryHandler(button_callback, pattern='^show_config$'))
        application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern='^back_to_menu$'))
        
        # Mensajes
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))

        print("✅ Bot iniciado con sistema multi-usuario")
        application.run_polling()
