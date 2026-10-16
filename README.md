# RAG Voice Agent

Agente de voz conversacional con recuperación aumentada de información (RAG).
Se conecta a una sala LiveKit, transcribe audio en tiempo real, consulta tu base de conocimiento y responde con voz sintetizada.

**Stack:** STT (Deepgram / AssemblyAI) · TTS (Cartesia) · LLM (OpenAI / Ollama) · RAG (LlamaIndex)

---

## Requisitos previos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) 0.12+
- Servidor LiveKit (cloud o self-hosted)
- Ollama (opcional, para LLM local)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd rag_voice_agent

# 2. Instalar dependencias
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus claves

# 4. Ejecutar el agente
uv run python voice_agent.py dev
```

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

| Variable | Estado | Descripción |
|---|---|---|
| `LIVEKIT_URL` | requerido | URL del servidor LiveKit (ej. `wss://my-app.livekit.cloud`) |
| `LIVEKIT_API_KEY` | requerido | API key de LiveKit |
| `LIVEKIT_API_SECRET` | requerido | API secret de LiveKit |
| `OPENAI_API_KEY` | requerido | Clave de OpenAI (LLM y/o embeddings) |
| `CARTESIA_API_KEY` | requerido | Clave de Cartesia para TTS |
| `DEEPGRAM_API_KEY` | opcional | Clave de Deepgram para STT |
| `ASSEMBLYAI_API_KEY` | opcional | Clave de AssemblyAI para STT (alternativa a Deepgram). Obtener en [app.assemblyai.com](https://www.assemblyai.com/) |
| `OLLAMA_BASE_URL` | opcional | URL del servidor Ollama (ej. `http://localhost:11434`) |

> Se requiere al menos una clave de Deepgram **o** AssemblyAI para transcribir audio.

---

## Estructura del proyecto

```
rag_voice_agent/
├── voice_agent.py          # Punto de entrada del agente
├── src/
│   └── rag_voice_agent/
│       └── __init__.py     # Módulo principal
├── chat-engine-storage/    # Índice RAG persistente (generado en runtime)
├── pyproject.toml          # Dependencias y metadatos
├── uv.lock                 # Lockfile reproducible
└── .env                    # Variables de entorno (no versionar)
```

> El directorio `chat-engine-storage/` se crea automáticamente la primera vez que el agente indexa documentos. Contiene el índice vectorial persistente de LlamaIndex.

---

## Comandos

```bash
# Desarrollo (recarga automática)
uv run python voice_agent.py dev

# Producción
uv run python voice_agent.py start

# Conectar a una sala específica
uv run python voice_agent.py connect --room <nombre-sala>
```

### Gestión de dependencias

```bash
# Añadir un paquete
uv add <paquete>

# Actualizar dependencias
uv sync --upgrade
```

---

## Preguntas de ejemplo al agente

El documento indexado es el perfil profesional de Rafael Guevara Aller. Estas son preguntas que puedes hacer al agente por voz:

**Experiencia y carrera**
- "¿Cuántos años de experiencia tiene Rafael?"
- "¿En qué empresa trabaja actualmente?"
- "¿Qué hizo en IBM?"
- "¿Cuál fue su rol en Belity?"
- "¿Cuánto tiempo trabajó en Apuesta Total?"
- "¿Ha trabajado como docente?"

**Habilidades técnicas**
- "¿Con qué frameworks de IA trabaja?"
- "¿Qué tecnologías cloud maneja?"
- "¿Sabe usar LangChain o LangGraph?"
- "¿Qué lenguajes de programación conoce?"
- "¿Tiene experiencia con Kubernetes y Docker?"
- "¿Ha trabajado con OpenAI o Anthropic?"

**Proyectos destacados**
- "¿Qué construyó en Culqi?"
- "¿Qué es lo más relevante que hizo en IBM Watsonx?"
- "¿Tiene experiencia con pasarelas de pago?"
- "¿Ha trabajado con microservicios?"

**Educación y certificaciones**
- "¿Dónde estudió Rafael?"
- "¿Qué certificaciones tiene?"
- "¿Tiene alguna certificación en IA?"

**Contacto**
- "¿Cómo puedo contactar a Rafael?"
- "¿Cuál es su LinkedIn?"
- "¿Dónde está ubicado?"

---

## Plugins disponibles

| Rol | Proveedor |
|---|---|
| STT | Deepgram, AssemblyAI |
| TTS | Cartesia |
| LLM | OpenAI, Ollama |
| RAG | LlamaIndex Core |
| VAD | Silero |
