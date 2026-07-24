"""
Service Coordinator Assistant
Version 0.7.0
Author: UD016

Prototype AI assistant for Cummins Service Operations

Change log:

v0.7.0
- Upgraded retrieval from keyword scoring to embedding-based retrieval.
    - Builds and caches an embedding index for Markdown chunks in knowledge_base.
    - Uses semantic similarity to retrieve the most relevant chunks for each question.
    - Keeps a small keyword boost for exact matches and technician-related queries.
- Retained session memory with the OpenAI Agents SDK SQLiteSession.

v0.5.0
- Implemented session memory using the OpenAI Agents SDK SQLiteSession.
    - Added a persistent session store for multi-turn conversations.
    - Added a session_id parameter to ask_service_assistant().
    - Kept lightweight retrieval and dynamic per-question context injection.

v0.4.0
- Switched from full knowledge-base injection to lightweight per-question retrieval.
    - Built a helper function that indexes Markdown files inside knowledge_base.
    - Retrieves only the most relevant Markdown chunks for each user question.
    - Injects retrieved excerpts into the agent prompt instead of the full knowledge base.

v0.3.0
- Changed knowledge retrieval method.
    - Defined a helper function to retrieve Markdown files inside knowledge_base instead of retrieving a single master file.
- Specified GPT model in the agent function 
- Reduced and refined system prompt.

v0.2.0
- Moved from a built-in prompt mechanism to a helper function integrated within Streamlit.

v0.1.0
- Initial prototype build.
    - Self-contained in the terminal, not usable elsewhere.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import log, sqrt
from pathlib import Path
import pickle
import re
from typing import Iterable

from agents import Agent, Runner, SQLiteSession
from openai import OpenAI


# Set virtual environment (python -m venv [your environment name])
# Set API Key (in PowerShell or PC environment)

OPENAI_CLIENT = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"
KNOWLEDGE_BASE_PATH = Path("knowledge_base")
CACHE_DIR = Path(".cache")
EMBEDDING_CACHE_PATH = CACHE_DIR / "service_assistant_embedding_index.pkl"
SESSION_DB_PATH = Path("service_assistant_sessions.sqlite3")
_SESSION_CACHE: dict[str, SQLiteSession] = {}

STOPWORDS = {
    "what", "does", "do", "is", "are", "the", "a", "an", "of", "for",
    "to", "in", "on", "and", "or", "by", "with", "stand", "stands",
    "mean", "meaning", "tell", "me", "about", "please", "can", "you",
    "this", "that", "it", "who", "which", "whom", "where", "when", "why",
    "how", "much", "many", "there", "here", "then", "than", "as"
}

TECHNICAL_QUERY_HINTS = {
    "technician", "tech", "recommend", "dispatch", "territory", "territories",
    "region", "regions", "clearance", "clearances", "bilingual", "travel",
    "engine", "diagnostic", "diagnostics", "ats", "commissioning", "controls",
    "field service", "field technician", "shop only", "shop-only", "who covers",
    "who is", "who handles", "who works", "specializes", "specializes in"
}

LIST_ALL_QUERY_HINTS = {
    "list", "all", "every", "show all", "which technicians", "who has",
    "who are", "qualified", "certified", "trained"
}

LIST_ALL_CAPABILITY_HINTS = {
    "training", "trainings", "certification", "certifications", "qualification",
    "qualifications", "course", "courses", "pcc", "ats", "controls",
    "commissioning", "engine", "diagnostic", "diagnostics"
}


@dataclass(frozen = True)
class Chunk:
    source: str
    text: str
    token_set: frozenset[str]


@dataclass(frozen = True)
class EmbeddedChunk:
    source: str
    text: str
    token_set: frozenset[str]
    vector: tuple[float, ...]


def normalize_text(text: str) -> str:
    """
    Normalize text for simple matching.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """
    Tokenize text into simple word tokens.
    """
    normalized = normalize_text(text)
    if not normalized:
        return []
    return normalized.split()


def tokenize_for_retrieval(text: str) -> list[str]:
    """
    Tokenize text and remove common stopwords.
    """
    return [t for t in tokenize(text) if t not in STOPWORDS]


def extract_acronym(question: str) -> str | None:
    """
    Detect questions like:
    - What does FSPG stand for?
    - What is CSA?
    - Define FSPG
    - Meaning of FSPG
    """
    patterns = [
        r"\bwhat does\s+([A-Z]{2,12})\s+stand for\b",
        r"\bwhat is\s+([A-Z]{2,12})\b",
        r"\bdefine\s+([A-Z]{2,12})\b",
        r"\bmeaning of\s+([A-Z]{2,12})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, question, flags = re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def is_technician_query(question: str) -> bool:
    """
    Heuristic that gives a small score boost to technician-profile lookups.
    """
    q = normalize_text(question)
    return any(hint in q for hint in TECHNICAL_QUERY_HINTS)

def is_list_all_query(question: str) -> bool:
    """
    Detect questions that need broader technician-profile coverage.
    """
    q = normalize_text(question)
    has_list_language = any(hint in q for hint in LIST_ALL_QUERY_HINTS)
    has_capability_language = any(hint in q for hint in LIST_ALL_CAPABILITY_HINTS)
    return has_list_language and has_capability_language


def split_markdown_into_chunks(text: str, max_words: int = 220) -> list[str]:
    """
    Split markdown into readable chunks.

    Strategy:
    - Prefer paragraph boundaries
    - Keep chunks small enough for targeted retrieval
    - Fall back to word-based splitting for oversized paragraphs
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[str] = []
    current: list[str] = []
    current_word_count = 0

    for para in paragraphs:
        para_words = len(para.split())

        if para_words > max_words:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_word_count = 0

            words = para.split()
            for i in range(0, len(words), max_words):
                chunks.append(" ".join(words[i : i + max_words]))
            continue

        if current and current_word_count + para_words > max_words:
            chunks.append("\n\n".join(current))
            current = []
            current_word_count = 0

        current.append(para)
        current_word_count += para_words

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def file_signature(file_path: Path) -> tuple[str, int, int]:
    stat = file_path.stat()
    return (str(file_path.relative_to(KNOWLEDGE_BASE_PATH)), stat.st_mtime_ns, stat.st_size)


@lru_cache(maxsize = 1)
def build_chunk_index(path: str = "knowledge_base") -> tuple[Chunk, ...]:
    """
    Load and chunk all Markdown documents in the active knowledge base.
    """
    kb_path = Path(path)
    if not kb_path.exists():
        return tuple()

    chunks: list[Chunk] = []

    for file in sorted(kb_path.rglob("*.md")):
        try:
            text = file.read_text(encoding = "utf-8")
        except Exception:
            continue

        relative_source = str(file.relative_to(kb_path))
        file_stem = file.stem

        for chunk_text in split_markdown_into_chunks(text):
            searchable_text = f"{relative_source}\n{file_stem}\n{chunk_text}"
            chunks.append(
                Chunk(
                    source = relative_source,
                    text = chunk_text,
                    token_set = frozenset(tokenize(searchable_text)),
                )
            )

    return tuple(chunks)


def build_embedding_input(chunks: Iterable[Chunk]) -> list[str]:
    """
    Build the text strings that will be embedded.
    """
    return [f"Source: {chunk.source}\n\n{chunk.text}" for chunk in chunks]


def cosine_similarity(vec_a: tuple[float, ...], vec_b: tuple[float, ...]) -> float:
    """
    Cosine similarity for two vectors.
    """
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sqrt(sum(a * a for a in vec_a))
    norm_b = sqrt(sum(b * b for b in vec_b))

    if not norm_a or not norm_b:
        return 0.0

    return dot / (norm_a * norm_b)


def embed_texts(texts: list[str], batch_size: int = 64) -> list[tuple[float, ...]]:
    """
    Embed texts in batches using the OpenAI Embeddings API.
    """
    vectors: list[tuple[float, ...]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = OPENAI_CLIENT.embeddings.create(
            model = EMBEDDING_MODEL,
            input = batch,
            encoding_format = "float",
        )

        ordered = sorted(response.data, key = lambda item: item.index)
        vectors.extend(tuple(item.embedding) for item in ordered)

    return vectors


def read_embedding_cache() -> tuple[tuple[tuple[str, int, int], ...], tuple[EmbeddedChunk, ...]] | None:
    """
    Load the cached embedding index if the knowledge base has not changed.
    """
    if not EMBEDDING_CACHE_PATH.exists():
        return None

    try:
        with EMBEDDING_CACHE_PATH.open("rb") as f:
            payload = pickle.load(f)
    except Exception:
        return None

    signature = payload.get("signature")
    chunks = payload.get("chunks")

    if not isinstance(signature, tuple) or not isinstance(chunks, tuple):
        return None

    return signature, chunks


def write_embedding_cache(
    signature: tuple[tuple[str, int, int], ...],
    chunks: tuple[EmbeddedChunk, ...],
) -> None:
    """
    Persist the embedding index for faster startup on future runs.
    """
    CACHE_DIR.mkdir(parents = True, exist_ok = True)

    payload = {
        "signature": signature,
        "chunks": chunks,
        "embedding_model": EMBEDDING_MODEL,
    }

    with EMBEDDING_CACHE_PATH.open("wb") as f:
        pickle.dump(payload, f)


@lru_cache(maxsize=1)
def build_embedding_index(path: str = "knowledge_base") -> tuple[EmbeddedChunk, ...]:
    """
    Load or build the embedding index for all active knowledge base Markdown files.
    """
    kb_path = Path(path)
    if not kb_path.exists():
        return tuple()

    current_signature = tuple(
        file_signature(file)
        for file in sorted(kb_path.rglob("*.md"))
    )

    cached = read_embedding_cache()
    if cached is not None:
        cached_signature, cached_chunks = cached
        if cached_signature == current_signature:
            return cached_chunks

    base_chunks = build_chunk_index(path)
    if not base_chunks:
        return tuple()

    texts = build_embedding_input(base_chunks)
    vectors = embed_texts(texts)

    embedded_chunks = tuple(
        EmbeddedChunk(
            source = chunk.source,
            text = chunk.text,
            token_set = chunk.token_set,
            vector = vector,
        )
        for chunk, vector in zip(base_chunks, vectors)
    )

    try:
        write_embedding_cache(current_signature, embedded_chunks)
    except Exception:
        # Cache failure should not break the assistant.
        pass

    return embedded_chunks


def score_chunk_embedding(
    question: str,
    question_vector: tuple[float, ...],
    chunk: EmbeddedChunk,
) -> float:
    """
    Score a chunk using semantic similarity plus a small keyword boost.
    """
    similarity = cosine_similarity(question_vector, chunk.vector)

    qtokens = tokenize_for_retrieval(question)
    overlap = len(set(qtokens) & chunk.token_set)

    score = similarity + (0.05 * overlap)

    acronym = extract_acronym(question)
    if acronym and acronym.lower() in chunk.token_set:
        score += 0.25

    if is_technician_query(question) and chunk.source.startswith("technicians/"):
        score += 0.12

    return score


def retrieve_relevant_chunks(
    question: str,
    kb_index: tuple[EmbeddedChunk, ...],
    top_k: int = 4,
) -> list[EmbeddedChunk]:
    """
    Return the most relevant chunks for a question using embedding similarity.
    """
    if not question.strip() or not kb_index:
        return []

    question_vector = tuple(
        embed_texts([question])[0]
    )

    scored: list[tuple[float, EmbeddedChunk]] = []

    for chunk in kb_index:
        score = score_chunk_embedding(question, question_vector, chunk)
        scored.append((score, chunk))

    scored.sort(key = lambda item: item[0], reverse = True)
    return [chunk for _, chunk in scored[:top_k]]


def format_retrieved_context(chunks: list[EmbeddedChunk], max_chars: int = 12000) -> str:
    """
    Format retrieved chunks for insertion into the agent instructions.
    """
    if not chunks:
        return "No relevant knowledge base excerpts were found."

    sections: list[str] = []
    total_chars = 0

    for chunk in chunks:
        block = f"### Source: {chunk.source}\n{chunk.text.strip()}"
        if total_chars + len(block) > max_chars:
            break
        sections.append(block)
        total_chars += len(block)

    return "\n\n---\n\n".join(sections)


def get_session(session_id: str = "default_service_chat") -> SQLiteSession:
    """
    Return a stable SQLiteSession for a given conversation ID.
    """
    if session_id not in _SESSION_CACHE:
        _SESSION_CACHE[session_id] = SQLiteSession(session_id, str(SESSION_DB_PATH))
    return _SESSION_CACHE[session_id]


def build_agent(question: str) -> Agent:
    """
    Build an agent with only the most relevant knowledge excerpts.
    """
    kb_index = build_embedding_index("knowledge_base")

    if is_list_all_query(question):
        top_k = 15
    elif is_technician_query(question):
        top_k = 8
    else:
        top_k = 4

    relevant_chunks = retrieve_relevant_chunks(question, kb_index, top_k=top_k)
    retrieved_context = format_retrieved_context(relevant_chunks)

    human_instructions = f"""
You are the Service Coordinator Assistant for the Cummins service department.

Your purpose is to help service coordinators perform their work accurately and efficiently by answering questions, explaining procedures, assisting with dispatch decisions, and providing invoicing guidance.

## Knowledge Policy

- The provided knowledge excerpts are the primary source of truth for all Cummins-specific procedures, workflows, terminology, and internal policies.
- If the knowledge excerpts contain the answer, always prioritize them.
- You may use general public knowledge to provide context about external organizations, manufacturers, industry standards, regulations, or technical concepts when the knowledge excerpts do not contain that information.
- If internal knowledge and general knowledge conflict, always follow the knowledge excerpts.
- Never invent procedures, policies, technician qualifications, pricing, customer information, or business rules.
- If the information is unavailable, clearly state what is missing.

## Response Guidelines

- Answer clearly, professionally, and concisely.
- Adapt the amount of detail to the user's question.
- For simple questions (definitions, acronyms, terminology), provide a direct answer.
- For workflow questions (dispatch, invoicing, troubleshooting, scheduling, etc.), guide the user through the appropriate process using the knowledge excerpts.
- When useful, identify missing information before making recommendations.
- Explain your reasoning whenever making recommendations or decisions.
- Suggest practical next steps when appropriate.

## Ambiguity

- If an acronym or term has multiple meanings, present the possible meanings and ask for clarification instead of guessing.
- If a question is ambiguous, ask only the minimum clarification needed.

## Source Transparency

When appropriate, indicate whether your answer is based on:
- the Cummins knowledge base
- general public knowledge
- or a combination of both.

Knowledge excerpts:

{retrieved_context}
""".strip()

    return Agent(
        name = "Service Coordinator Assistant",
        model = "gpt-4o-mini",
        instructions = human_instructions,
    )


# Public function used by the Streamlit application
def ask_service_assistant(question: str, session_id: str = "default_service_chat") -> str:
    """
    Send a question to the Service Coordinator Assistant
    and return the response.
    """
    agent = build_agent(question)
    session = get_session(session_id=session_id)

    result = Runner.run_sync(
        agent,
        question,
        session = session,
    )

    return result.final_output


if __name__ == "__main__":
    print("Service Coordinator Assistant")
    print("Type 'quit' to exit.\n")

    terminal_session_id = "terminal_chat"

    while True:
        question = input("Ask a service question: ").strip()

        if question.lower() in {"quit", "exit", "q"}:
            break

        if not question:
            continue

        print()
        print(ask_service_assistant(question, session_id = terminal_session_id))
        print()