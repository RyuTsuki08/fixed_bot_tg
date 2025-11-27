# 🤖 Cerebro Bot - Tu Asistente Personal con IA

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.0-orange?style=for-the-badge&logo=google&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-API-black?style=for-the-badge&logo=notion&logoColor=white)
![License](https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge)

**Bot de Telegram multi-usuario que integra Google Gemini AI con Notion para gestión inteligente de tareas**

[Características](#-características-principales) • [Arquitectura](#-arquitectura) • [Instalación](#-instalación-rápida) • [Demo](#-demostración)

</div>

---

## 🎯 Descripción General

**Cerebro Bot** es un asistente inteligente de Telegram que conecta el lenguaje natural con la gestión estructurada de tareas. Construido con tecnología de IA de vanguardia, transforma notas de voz casuales y mensajes de texto en tareas organizadas y accionables en bases de datos de Notion.

### 💡 El Problema que Resuelve

- ⏰ **Gestión del Tiempo**: Los usuarios luchan por capturar y organizar tareas rápidamente
- 🎙️ **Prioridad a la Voz**: La mayoría de los gestores de tareas no soportan entrada de voz efectivamente
- 🤝 **Colaboración**: Compartir un bot con credenciales personales crea riesgos de seguridad
- 🔄 **Cambio de Contexto**: Moverse entre apps de mensajería y gestores de tareas interrumpe el flujo de trabajo

### ✨ La Solución

Un **único bot de Telegram** que:
- Entiende lenguaje natural en español (expandible a otros idiomas)
- Transcribe notas de voz usando Google Gemini 2.0
- Extrae automáticamente detalles de tareas (título, fecha, prioridad, tipo)
- Crea tareas directamente en tu workspace personal de Notion
- Soporta **múltiples usuarios** con credenciales aisladas y seguras

---

## 🚀 Características Principales

### 🧠 Inteligencia Artificial Avanzada

- **Procesamiento de Lenguaje Natural**: Impulsado por Google Gemini 2.5 Flash
  ```
  Usuario: "Reunión con el equipo mañana a las 10am tipo:Trabajo"
  Bot: ✅ Tarea creada: "Reunión con equipo" | Fecha: 2025-11-28 | Tipo: Trabajo
  ```

- **Transcripción de Notas de Voz**: Convierte mensajes de audio en tareas instantáneamente
  - Transcripción automática en español
  - Análisis contextual
  - Extracción de múltiples campos

### 📊 Integración con Notion

- **Gestión Completa de Bases de Datos**
  - Crea tareas con título, descripción, fecha, estado y tipo
  - Soporte para múltiples bases de datos por usuario
  - Validación dinámica de estados
  - Actualizaciones en tiempo real

- **Capacidades de Búsqueda y Edición**
  ```bash
  /buscar reunión    # Encuentra todas las tareas con "reunión"
  /editar abc123 estado:Completado    # Actualiza el estado de la tarea
  ```

### 👥 Arquitectura Multi-Usuario

- **Credenciales Personales**: Cada usuario configura sus propias:
  - API key de Google Gemini
  - Token de integración de Notion
  - Bases de datos de Notion

- **Privacidad y Seguridad**:
  - Credenciales almacenadas por usuario (no compartidas)
  - Mensajes con datos sensibles auto-eliminados
  - Acceso aislado a workspaces
  - Fallback a credenciales globales para compatibilidad

### 🎨 Experiencia de Usuario

- **Menús Interactivos**: Botones de teclado en línea para navegación fácil
- **Ayuda Contextual**: Guías paso a paso para configuración
- **Parsing de Fechas en Español**: Entiende "mañana", "próximo lunes", "en 3 días"
- **Recuperación de Errores**: Lógica de reintentos con backoff exponencial
- **Logging Completo**: Registros detallados para debugging

---

## 🏗️ Arquitectura

### Diseño del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                     BOT TELEGRAM                        │
│                      (main.py)                          │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
    ┌────────────────┐          ┌─────────────────┐
    │ Servicio Gemini│          │ Servicio Notion │
    │                │          │                 │
    │ • Chat         │          │ • Crear Página  │
    │ • Transcribir  │          │ • Buscar        │
    │ • Extraer Info │          │ • Actualizar    │
    └────────┬───────┘          └────────┬────────┘
             │                           │
             ▼                           ▼
    ┌─────────────────┐        ┌──────────────────┐
    │  Gemini 2.5 API │        │   Notion API     │
    │  (Flash Lite)   │        │                  │
    └─────────────────┘        └──────────────────┘
             │
             ▼
    ┌──────────────────────────────────────────┐
    │   Gestor de Configuración de Usuarios    │
    │   (user_config_manager.py)               │
    │                                          │
    │  {                                       │
    │    "user_123": {                         │
    │      "gemini_api_key": "...",            │
    │      "notion_token": "...",              │
    │      "databases": {...}                  │
    │    }                                     │
    │  }                                       │
    └──────────────────────────────────────────┘
```

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|-----------|-----------|---------|
| **Framework Bot** | `python-telegram-bot 20+` | Interacción con API de Telegram |
| **Motor IA** | Google Gemini 2.5 Flash | NLP, transcripción, extracción |
| **Base de Datos** | Notion API | Almacenamiento y gestión de tareas |
| **Parsing de Fechas** | Custom `date_utils.py` | Interpretación de fechas en español |
| **Configuración** | JSON + Variables de Entorno | Gestión de credenciales multi-usuario |
| **Logging** | Módulo `logging` de Python | Seguimiento estructurado de errores |

### Estructura de Archivos

```
cerebro-bot/
├── main.py                    # Orquestación del bot y handlers
├── gemini_service.py          # Servicios de IA (chat, transcribir, extraer)
├── notion_service.py          # Operaciones CRUD de Notion
├── user_config_manager.py     # Gestión de credenciales multi-usuario
├── date_utils.py              # Utilidades de parsing de fechas en español
├── config_manager.py          # Config legacy (compatibilidad)
├── migrate_to_multiuser.py    # Script de migración
├── users_config.json          # Almacenamiento de credenciales
├── .env                       # Variables de entorno
├── requirements.txt           # Dependencias de Python
└── README.md                  # Este archivo
```

---

## 📚 Referencia de Comandos

### Comandos de Configuración

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Mensaje de bienvenida e inicio rápido | `/start` |
| `/config` | Ver tu configuración personal | `/config` |
| `/set_gemini <key>` | Configurar tu API key de Gemini | `/set_gemini AIza...` |
| `/set_notion <token>` | Configurar tu token de Notion | `/set_notion secret_...` |
| `/setup_notion` | Guía completa de configuración de Notion | `/setup_notion` |
| `/add_db <alias> <id>` | Añadir una base de datos de Notion | `/add_db trabajo abc123...` |
| `/set_db <alias>` | Cambiar base de datos activa | `/set_db personal` |
| `/list_dbs` | Ver todas tus bases de datos | `/list_dbs` |
| `/reset_config` | Eliminar tu configuración | `/reset_config` |

### Comandos de Gestión de Tareas

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/plan <tarea>` | Crear tarea desde texto | `/plan Comprar leche mañana` |
| 🎙️ Nota de Voz | Crear tarea desde audio | *(Enviar mensaje de voz)* |
| `/buscar <término>` | Buscar tareas por título | `/buscar reunión` |
| `/editar <id> <cambios>` | Actualizar tarea existente | `/editar abc123 estado:Hecho` |
| Mensaje directo | Chatear con Gemini AI | `¿Qué es Python?` |

---

## 🛠️ Instalación Rápida

### Requisitos Previos

- Python 3.10+
- Cuenta de Telegram
- API key de Google Gemini ([Consíguela aquí](https://aistudio.google.com/apikey))
- Cuenta de Notion con integración ([Guía de configuración](https://www.notion.so/my-integrations))

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tuusuario/cerebro-bot.git
   cd cerebro-bot
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Crear archivo `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=tu_token_de_telegram
   DEFAULT_GEMINI_API_KEY=tu_key_gemini  # Opcional (fallback)
   NOTION_INTEGRATION_TOKEN=tu_token_notion  # Opcional (fallback)
   ```

5. **Ejecutar el bot**
   ```bash
   python main.py
   ```

6. **Configurar en Telegram**
   - Abre el bot en Telegram
   - Envía `/start`
   - Sigue el asistente de configuración
   - Usa `/setup_notion` para configuración detallada de Notion

---

## 🎬 Demostración

### Creando una Tarea desde Voz

```
Usuario: 🎙️ "Recordar comprar leche mañana y pan pasado mañana, tipo personal"

Bot: 🎙️ Procesando...

Bot: ✅ Tarea creada

📝 Transcripción: "Recordar comprar leche mañana y pan pasado mañana tipo personal"

✅ Página creada: Comprar leche y pan
🔗 https://notion.so/abc123...
```

### Creación de Tarea en Lenguaje Natural

```
Usuario: /plan Reunión con cliente próximo lunes a las 3pm estado:Por hacer tipo:Negocio

Bot: 🧠 Analizando...

Bot: ✅ Página creada: Reunión con cliente
📅 Fecha: 2025-12-02
📊 Estado: Por hacer
🏢 Tipo: Negocio
🔗 https://notion.so/def456...
```

### Privacidad Multi-Usuario

```
Usuario A: /set_gemini AIza_UsuarioA_Key
Bot: ✅ Tu API key de Gemini fue configurada.
      🔒 El mensaje fue borrado por seguridad.

Usuario B: /set_gemini AIza_UsuarioB_Key
Bot: ✅ Tu API key de Gemini fue configurada.
      🔒 El mensaje fue borrado por seguridad.

# Las tareas del Usuario A van al Notion del Usuario A
# Las tareas del Usuario B van al Notion del Usuario B
# ¡Sin compartir credenciales!
```

---

## 🔐 Seguridad y Privacidad

### Aislamiento Multi-Inquilino

- ✅ **Credenciales por usuario**: API keys de cada usuario almacenadas por separado
- ✅ **Eliminación automática de mensajes**: Mensajes sensibles auto-eliminados después del procesamiento
- ✅ **Almacenamiento encriptado**: Credenciales en JSON (puede encriptarse con Fernet)
- ✅ **Sin acceso cruzado**: Los usuarios no pueden acceder a datos de Notion de otros

### Mejores Prácticas Implementadas

- Variables de entorno para datos globales sensibles
- Logging estructurado sin exposición de credenciales
- Lógica de reintentos para resiliencia de API
- Validación y sanitización de entrada

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|--------|-------|
| **Líneas de Código** | ~1,200 |
| **Módulos** | 7 |
| **Comandos** | 15+ |
| **Idiomas Soportados** | Español (expandible) |
| **APIs Integradas** | 3 (Telegram, Gemini, Notion) |
| **Tiempo de Desarrollo** | 2 semanas |
| **Cobertura de Tests** | Pruebas manuales (tests automatizados pendientes) |

---

## 🗺️ Hoja de Ruta

### Completado ✅

- [x] Creación básica de tareas desde texto
- [x] Integración con Google Gemini
- [x] Integración con base de datos de Notion
- [x] Transcripción de notas de voz
- [x] Soporte multi-usuario
- [x] Parsing de fechas en español
- [x] Funcionalidad de búsqueda y edición
- [x] Manejo robusto de errores
- [x] Sistema de ayuda interactivo

### En Progreso 🚧

- [ ] Suite de tests automatizados (pytest)
- [ ] Pipeline CI/CD (GitHub Actions)
- [ ] Dockerización
- [ ] Soporte multi-idioma

### Mejoras Futuras 🔮

- [ ] Dashboard web para configuración
- [ ] Tareas recurrentes y recordatorios
- [ ] Plantillas de tareas
- [ ] Integración con Google Calendar
- [ ] Funciones de colaboración (asignar tareas a otros)
- [ ] Dashboard de analíticas de uso
- [ ] Consultas en lenguaje natural ("Muéstrame las tareas de esta semana")
- [ ] Integración con más herramientas de productividad (Trello, Asana)

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, siéntete libre de enviar un Pull Request.

### Configuración de Desarrollo

1. Haz fork del repositorio
2. Crea una rama de feature (`git checkout -b feature/CaracteristicaAsombrosa`)
3. Haz commit de tus cambios (`git commit -m 'Añadir CaracteristicaAsombrosa'`)
4. Push a la rama (`git push origin feature/CaracteristicaAsombrosa`)
5. Abre un Pull Request

### Estilo de Código

- Seguir las guías PEP 8
- Añadir docstrings a las funciones
- Incluir type hints donde sea aplicable
- Escribir mensajes de commit significativos

---

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- **Google Gemini AI** - Por el poderoso procesamiento de lenguaje natural
- **Telegram Bot API** - Por el excelente framework y documentación para bots
- **Notion API** - Por la gestión flexible de bases de datos
- **python-telegram-bot** - Por el wrapper completo en Python

---

## 📧 Contacto

**Tomas** - [LinkedIn](https://linkedin.com/in/tuprofile)

Link del Proyecto: [https://github.com/tuusuario/cerebro-bot](https://github.com/tuusuario/cerebro-bot)

---

<div align="center">

**⭐ ¡Dale una estrella a este repo si te resulta útil!**

Hecho con ❤️ y Python

</div>
