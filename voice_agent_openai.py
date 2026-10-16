import asyncio
import logging
import os

import pypdf
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.agents import llm as agents_llm
from livekit.agents.job import AutoSubscribe
from livekit.agents.llm import ChatChunk, ChoiceDelta
from livekit.agents.types import APIConnectOptions
from livekit.plugins import assemblyai, cartesia, silero
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.chat_engine.types import ChatMode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()
logger = logging.getLogger("voice-assistant")
logger.setLevel(logging.INFO)

PERSIST_DIR = "./chat-engine-storage"


def load_docs_from_pdf(docs_dir: str) -> list[Document]:
    documents = []
    pdf_files = [f for f in os.listdir(docs_dir) if f.lower().endswith(".pdf")]
    logger.info("Found %d PDF file(s) in '%s'", len(pdf_files), docs_dir)
    for fname in pdf_files:
        path = os.path.join(docs_dir, fname)
        logger.info("Reading PDF: %s", fname)
        reader = pypdf.PdfReader(path)
        full_text = "\n\n".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )
        logger.info("Extracted %d chars from %s (%d pages)", len(full_text), fname, len(reader.pages))
        documents.append(Document(text=full_text, metadata={"source": fname}))
    return documents


logger.info("Initializing embedding model and LLM...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = OpenAI(model="gpt-4o-mini", temperature=0.3)
Settings.llm = llm
Settings.embed_model = embed_model
logger.info("Models ready")

if not os.path.exists(PERSIST_DIR):
    logger.info("No existing index found — building from documents...")
    documents = load_docs_from_pdf("docs")
    logger.info("Indexing %d document(s)...", len(documents))
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    logger.info("Index built and persisted to '%s'", PERSIST_DIR)
else:
    logger.info("Loading existing index from '%s'...", PERSIST_DIR)
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    logger.info("Index loaded")


class LlamaIndexLLM(agents_llm.LLM):
    def __init__(self, chat_engine):
        super().__init__()
        self._chat_engine = chat_engine

    def chat(self, *, chat_ctx, tools=None, conn_options=None, **kwargs):
        return LlamaIndexStream(
            llm=self,
            chat_ctx=chat_ctx,
            tools=tools or [],
            conn_options=conn_options or APIConnectOptions(),
            chat_engine=self._chat_engine,
        )


class LlamaIndexStream(agents_llm.LLMStream):
    def __init__(self, *, chat_engine, **kwargs):
        super().__init__(**kwargs)
        self._chat_engine = chat_engine

    async def _run(self):
        user_msg = ""
        for msg in reversed(self._chat_ctx.messages()):
            if msg.role == "user":
                content = msg.content
                if isinstance(content, list):
                    user_msg = " ".join(str(c) for c in content)
                else:
                    user_msg = str(content)
                break

        response = await self._chat_engine.achat(user_msg)

        self._event_ch.send_nowait(
            ChatChunk(
                id="llamaindex",
                delta=ChoiceDelta(role="assistant", content=str(response)),
            )
        )


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Prewarmed VAD model")


async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    SYSTEM_PROMPT = (
        "Eres un gemelo digital que funciona en un sitio web e interactúa con sus visitantes mediante un chat. "
        "Representas a la persona propietaria del sitio web. "
        "Respondes preguntas relacionadas con su trayectoria profesional, formación, habilidades y experiencia. "
        "Si te preguntan, debes explicar claramente que eres una inteligencia artificial que actúa como el gemelo digital de esta persona. "
        "Interactúa activamente con el usuario. Mantén un tono profesional, cercano y atractivo, "
        "como si estuvieras conversando con un cliente potencial o un futuro empleador que ha visitado el sitio web. "
        "Responde únicamente preguntas relacionadas con la trayectoria profesional, formación, habilidades y experiencia de la persona. "
        "Si el usuario pregunta sobre un tema que no está relacionado con el ámbito profesional, "
        "redirige amablemente la conversación hacia temas profesionales. "
        "Mantente siempre en el papel de gemelo digital de la persona que representas. Habla y responde en su nombre. "
        "IMPORTANTE: Si desconoces la respuesta a una pregunta, informa al usuario que no dispones de esa información. "
        "Nunca inventes una respuesta."
    )

    logger.info("Building chat engine for room %s...", ctx.room.name)
    chat_engine = await asyncio.to_thread(
        index.as_chat_engine,
        chat_mode=ChatMode.CONTEXT,
        system_prompt=SYSTEM_PROMPT,
    )
    logger.info("Chat engine ready")

    agent = Agent(instructions=SYSTEM_PROMPT)

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=assemblyai.STT(language_code="es"),
        llm=LlamaIndexLLM(chat_engine),
        tts=cartesia.TTS(
            model="sonic-2",
            language="es",
            voice="5c5ad5e7-1020-476b-8b91-fdcbe9cc313c",  # Daniela - Mexican Spanish
        ),
    )

    await session.start(agent, room=ctx.room)
    await session.say("¡Hola! ¿En qué puedo ayudarte hoy?", allow_interruptions=True)


if __name__ == "__main__":
    print("Starting voice agent (OpenAI)...")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
