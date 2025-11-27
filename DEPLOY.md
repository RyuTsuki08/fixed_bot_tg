# 🚀 Guía de Deployment en Render

Esta guía te ayudará a deployar **Cerebro Bot** en Render de forma gratuita.

## 📋 Requisitos Previos

- Cuenta en [Render.com](https://render.com) (gratis)
- Cuenta en [GitHub](https://github.com) (para conectar el repositorio)
- Tus credenciales listas:
  - Token de Telegram Bot
  - API Key de Gemini (opcional)
  - Token de Notion (opcional)

---

## 🎯 Pasos para Deploy

### 1️⃣ Preparar el Repositorio

Si aún no tienes el código en GitHub:

```bash
# Inicializar git (si no lo hiciste)
git init

# Añadir archivos
git add .

# Crear commit
git commit -m "Initial commit - Cerebro Bot"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU_USUARIO/cerebro-bot.git
git branch -M main
git push -u origin main
```

### 2️⃣ Crear Servicio en Render

1. **Ir a [Render Dashboard](https://dashboard.render.com)**

2. **Click en "New +" → "Background Worker"**

3. **Conectar Repositorio:**
   - Autoriza GitHub si es la primera vez
   - Selecciona tu repositorio `cerebro-bot`

4. **Configuración del Servicio:**

   | Campo | Valor |
   |-------|-------|
   | **Name** | `cerebro-bot` (o el que prefieras) |
   | **Region** | Oregon (Free) |
   | **Branch** | `main` |
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `python main.py` |

5. **Variables de Entorno:**

   Click en "Advanced" → "Add Environment Variable" y añade:

   ```
   TELEGRAM_BOT_TOKEN = tu_token_de_telegram
   ```

   **Opcional (solo si quieres credenciales globales):**
   ```
   DEFAULT_GEMINI_API_KEY = tu_api_key_gemini
   NOTION_INTEGRATION_TOKEN = tu_token_notion
   ```

6. **Plan:** Selecciona **Free**

7. **Click en "Create Background Worker"**

### 3️⃣ Deploy Automático

Render detectará el archivo `render.yaml` y configurará todo automáticamente.

El bot se desplegará y:
- ✅ Instalará las dependencias
- ✅ Iniciará el bot
- ✅ Estará corriendo 24/7

---

## 🔄 Re-Deploy Automático

**Cada vez que hagas push a GitHub**, Render automáticamente:
1. Detecta los cambios
2. Hace rebuild
3. Reinicia el bot

```bash
# Hacer cambios en el código
git add .
git commit -m "Mejora en el bot"
git push origin main

# Render se actualiza automáticamente en ~1-2 minutos
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

1. Ir a tu servicio en Render Dashboard
2. Click en la pestaña **"Logs"**
3. Verás el output de `bot.log` en tiempo real

### Verificar Estado

- **Running** ✅ → Todo bien
- **Build Failed** ❌ → Revisa logs de build
- **Deploying** 🔄 → Esperando despliegue

---

## ⚙️ Configuración Avanzada

### Persistencia de Datos

Por defecto, Render usa sistema de archivos efímero. Para persistir `users_config.json`:

**Opción 1: Usar Render Disks (Paid)**
- Añadir un disco persistente en configuración

**Opción 2: Usar Base de Datos**
- Migrar `users_config.json` a PostgreSQL (gratis en Render)
- Requiere modificar `user_config_manager.py`

**Opción 3: Storage Externo**
- Guardar en AWS S3, Google Cloud Storage, etc.

### Variables de Entorno por Usuario

Para añadir más variables:

```bash
# En Render Dashboard → Environment
NEW_VARIABLE = valor
```

O editar `render.yaml`:

```yaml
envVars:
  - key: NUEVA_VARIABLE
    value: valor_estatico
```

---

## 🐛 Troubleshooting

### El bot no responde

1. **Verificar logs:**
   ```
   Render Dashboard → Logs
   ```

2. **Verificar que el servicio esté Running:**
   ```
   Render Dashboard → Service Status
   ```

3. **Verificar variables de entorno:**
   ```
   Render Dashboard → Environment
   Asegurarse de que TELEGRAM_BOT_TOKEN esté configurado
   ```

### Error "Module not found"

- **Solución:** Añadir el módulo a `requirements.txt`
- Render hará rebuild automáticamente

### El bot se detiene (plan Free)

**Render Free** tiene limitaciones:
- ⏰ Se suspende después de 15 minutos de inactividad
- 🔄 Se reactiva automáticamente con la primera petición

**Solución:**
- Upgrade a plan Starter ($7/mes) para 24/7 sin interrupciones
- O usar servicio de "ping" externo cada 10 minutos

---

## 💰 Costos

| Plan | Precio | Características |
|------|--------|-----------------|
| **Free** | $0/mes | • 750 horas/mes<br>• Se suspende tras inactividad<br>• Perfecto para pruebas |
| **Starter** | $7/mes | • 24/7 sin interrupciones<br>• No se suspende<br>• Ideal para producción |

**Recomendación:** Empieza con Free, upgrade si necesitas 24/7.

---

## 🎉 ¡Listo!

Tu bot ya está en la nube. Ahora puedes:

1. ✅ Usarlo desde cualquier lugar
2. ✅ Compartir con otros usuarios
3. ✅ Mostrar en tu portfolio con URL pública
4. ✅ Auto-deploy con cada push a GitHub

### URLs Importantes

- **Dashboard:** https://dashboard.render.com
- **Logs:** https://dashboard.render.com → Tu Servicio → Logs
- **Settings:** https://dashboard.render.com → Tu Servicio → Settings

---

## 📞 Soporte

- [Documentación Render](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Status de Render](https://status.render.com)

---

**¡Disfruta tu bot en producción! 🚀**
