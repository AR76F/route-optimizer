"""
Service Coordinator Assistant
Version 0.9.0
Author: UD016

Prototype AI assistant for Cummins Service Operations

Change log:

v0.9.0
- Switched temporary uploads from OCR to native OpenAI vision inputs.
    - Images and PDF pages are now passed to the model directly as temporary vision context.
    - Text-based uploads remain temporary conversation context only.
    - Uploaded content still stays separate from the knowledge base and persistent memory.
- Retained embedding-based retrieval and session memory.

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
- Specified GPT model in the agent function.
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
import base64
import io
import pickle
import re
import json
from typing import Any, Iterable, BinaryIO, Protocol

from agents import Agent, Runner, SQLiteSession
from openai import OpenAI

try:
    from PIL import Image, ImageOps
except Exception:  # pragma: no cover - optional dependency import guard
    Image = None  # type: ignore[assignment]
    ImageOps = None  # type: ignore[assignment]

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - optional dependency import guard
    fitz = None  # type: ignore[assignment]

try:
    import pytesseract
except Exception:  # pragma: no cover - optional dependency import guard
    pytesseract = None  # type: ignore[assignment]

    from typing import Any, Dict

# Set virtual environment (python -m venv [your environment name])
# Set API Key (in PowerShell or PC environment)

OPENAI_CLIENT = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"
KNOWLEDGE_BASE_PATH = Path("knowledge_base")
CACHE_DIR = Path(".cache")
EMBEDDING_CACHE_PATH = CACHE_DIR / "service_assistant_embedding_index.pkl"
SESSION_DB_PATH = Path("service_assistant_sessions.sqlite3")
_SESSION_CACHE: dict[str, SQLiteSession] = {}

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".log", ".json", ".xml", ".yaml", ".yml"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}

OCR_MAX_PAGE_PIXELS_SCALE = 2
OCR_MIN_TEXT_LENGTH_BEFORE_FALLBACK = 40

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


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str
    token_set: frozenset[str]


@dataclass(frozen=True)
class EmbeddedChunk:
    source: str
    text: str
    token_set: frozenset[str]
    vector: tuple[float, ...]


class UploadLike(Protocol):
    """
    Minimal protocol for uploaded file objects, including Streamlit UploadedFile.
    """

    name: str

    def read(self) -> bytes | str: ...
    def seek(self, __offset: int, __whence: int = 0) -> Any: ...


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
        match = re.search(pattern, question, flags=re.IGNORECASE)
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
    """
    A compact signature used to invalidate cached embeddings when files change.
    """
    stat = file_path.stat()
    return (str(file_path.relative_to(KNOWLEDGE_BASE_PATH)), stat.st_mtime_ns, stat.st_size)


@lru_cache(maxsize=1)
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
            text = file.read_text(encoding="utf-8")
        except Exception:
            continue

        relative_source = str(file.relative_to(kb_path))
        file_stem = file.stem

        for chunk_text in split_markdown_into_chunks(text):
            searchable_text = f"{relative_source}\n{file_stem}\n{chunk_text}"
            chunks.append(
                Chunk(
                    source=relative_source,
                    text=chunk_text,
                    token_set=frozenset(tokenize(searchable_text)),
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
            model=EMBEDDING_MODEL,
            input=batch,
            encoding_format="float",
        )

        ordered = sorted(response.data, key=lambda item: item.index)
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
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
            source=chunk.source,
            text=chunk.text,
            token_set=chunk.token_set,
            vector=vector,
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

    question_vector = tuple(embed_texts([question])[0])

    scored: list[tuple[float, EmbeddedChunk]] = []

    for chunk in kb_index:
        score = score_chunk_embedding(question, question_vector, chunk)
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
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


def _read_source_bytes(source: Any) -> tuple[bytes, str, str]:
    """
    Return raw bytes, a lower-case file suffix, and a display name for an input source.

    Supports:
    - filesystem paths
    - Streamlit UploadedFile objects
    - file-like objects that expose read()
    """
    if isinstance(source, Path):
        data = source.read_bytes()
        return data, source.suffix.lower(), source.name

    if isinstance(source, str):
        path = Path(source)
        data = path.read_bytes()
        return data, path.suffix.lower(), path.name

    if hasattr(source, "read"):
        raw = source.read()
        if isinstance(raw, str):
            raw_bytes = raw.encode("utf-8", errors="ignore")
        else:
            raw_bytes = bytes(raw)

        name = getattr(source, "name", "uploaded_file")
        suffix = Path(str(name)).suffix.lower()

        if hasattr(source, "seek"):
            try:
                source.seek(0)
            except Exception:
                pass

        return raw_bytes, suffix, str(name)

    raise TypeError(
        "Unsupported upload source. Expected a file path, Streamlit UploadedFile, or file-like object."
    )

def _bytes_to_data_url(raw_bytes: bytes, suffix: str) -> str:
    """
    Convert raw bytes into a data URL that can be passed to the OpenAI vision input.
    """
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }
    mime = mime_map.get(suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _pdf_pages_to_vision_items(raw_bytes: bytes, display_name: str, max_pages: int = 8) -> list[dict[str, Any]]:
    """
    Convert a PDF into a small set of image input items for native vision processing.
    """
    if fitz is None:
        raise RuntimeError(
            f"PDF vision is unavailable because PyMuPDF is not installed for {display_name!r}."
        )

    items: list[dict[str, Any]] = []
    try:
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
    except Exception as exc:
        raise RuntimeError(f"Could not open PDF source {display_name!r}: {exc}") from exc

    try:
        for page_number, page in enumerate(doc, start=1):
            if page_number > int(max_pages):
                break
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                png_bytes = pix.tobytes("png")
            except Exception as exc:
                raise RuntimeError(
                    f"Could not render PDF page {page_number} for {display_name!r}: {exc}"
                ) from exc

            items.append({
                "type": "input_image",
                "image_url": _bytes_to_data_url(png_bytes, ".png"),
                "detail": "high",
            })
    finally:
        doc.close()

    return items
def _normalize_ocr_image(image: Any) -> Any:
    """
    Light preprocessing to improve OCR quality.
    """
    if Image is None or ImageOps is None:
        return image

    try:
        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        image = ImageOps.grayscale(image)
        image = ImageOps.autocontrast(image)
        return image
    except Exception:
        return image


def extract_text_from_image_source(source: Any) -> str:
    """
    OCR an image source into plain text.
    """
    if pytesseract is None or Image is None:
        raise RuntimeError(
            "OCR is unavailable because Pillow or pytesseract is not installed."
        )

    raw_bytes, _, display_name = _read_source_bytes(source)

    try:
        image = Image.open(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise RuntimeError(f"Could not open image source {display_name!r}: {exc}") from exc

    image = _normalize_ocr_image(image)

    try:
        text = pytesseract.image_to_string(image, lang="eng")
    except Exception as exc:
        raise RuntimeError(
            f"OCR failed for image source {display_name!r}: {exc}"
        ) from exc

    cleaned = text.strip()
    return cleaned


def _render_pdf_page_for_ocr(page: Any) -> Any:
    """
    Render a PDF page to an image for OCR.
    """
    if Image is None or fitz is None:
        raise RuntimeError("PDF OCR is unavailable because Pillow or PyMuPDF is not installed.")

    matrix = fitz.Matrix(OCR_MAX_PAGE_PIXELS_SCALE, OCR_MAX_PAGE_PIXELS_SCALE)
    pix = page.get_pixmap(matrix=matrix, alpha=False)

    mode = "RGB"
    image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    image = _normalize_ocr_image(image)
    return image


def extract_text_from_pdf_source(source: Any) -> str:
    """
    Extract text from a PDF source using native PDF text extraction only.

    Vision for scanned PDFs is handled separately by passing rendered PDF pages
    to the model as image inputs.
    """
    if fitz is None:
        raise RuntimeError(
            "PDF handling is unavailable because PyMuPDF is not installed."
        )

    raw_bytes, _, display_name = _read_source_bytes(source)

    try:
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
    except Exception as exc:
        raise RuntimeError(f"Could not open PDF source {display_name!r}: {exc}") from exc

    page_texts: list[str] = []

    try:
        for page_number, page in enumerate(doc, start=1):
            extracted = page.get_text("text").strip()
            if extracted:
                page_texts.append(f"[Page {page_number}]\n{extracted}")
    finally:
        doc.close()

    return "\n\n".join(page_texts).strip()

def extract_text_from_text_source(source: Any) -> str:
    """
    Read a plain text source.
    """
    raw_bytes, _, display_name = _read_source_bytes(source)

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("utf-8", errors="ignore")

    cleaned = text.strip()
    if not cleaned:
        raise RuntimeError(f"Text source {display_name!r} was empty.")

    return cleaned


def extract_text_from_uploaded_source(source: Any) -> str:
    """
    Extract temporary conversation text from an uploaded file-like source.

    Supported formats:
    - PDFs (native text extraction only; vision is handled separately)
    - plain text files

    Image files are not converted to text here because they are passed directly
    to GPT vision as temporary input items.
    """
    _, suffix, display_name = _read_source_bytes(source)

    if suffix in SUPPORTED_PDF_EXTENSIONS:
        text = extract_text_from_pdf_source(source)
        return f"### Uploaded file: {display_name}\n{text}".strip() if text.strip() else ""

    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        text = extract_text_from_text_source(source)
        return f"### Uploaded file: {display_name}\n{text}".strip()

    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        # Images are handled as vision input items, not as text.
        return ""

    # Unknown file types are treated as text when possible.
    try:
        text = extract_text_from_text_source(source)
        return f"### Uploaded file: {display_name}\n{text}".strip()
    except Exception as exc:
        raise RuntimeError(
            f"Unsupported file type for {display_name!r}. Supported types are images, PDFs, and text files."
        ) from exc


def build_temporary_context(
    temporary_context: str | None = None,
    uploaded_sources: Iterable[Any] | None = None,
) -> str | None:
    """
    Build a temporary context block from direct text and/or uploaded sources.

    This context is for the current conversation only and is never stored in the knowledge base.
    """
    sections: list[str] = []

    if temporary_context and temporary_context.strip():
        sections.append(
            "### Direct temporary context\n"
            + temporary_context.strip()
        )

    if uploaded_sources:
        for source in uploaded_sources:
            try:
                extracted = extract_text_from_uploaded_source(source)
            except Exception as exc:
                extracted = f"### Uploaded file could not be processed\n{type(exc).__name__}: {exc}"
            if extracted:
                sections.append(extracted)

    if not sections:
        return None

    return "\n\n---\n\n".join(sections)


def build_uploaded_vision_input_items(uploaded_sources: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    """
    Build OpenAI vision input items from uploaded images and scanned PDFs.

    This is temporary conversation context only and is never stored in the knowledge base.
    """
    items: list[dict[str, Any]] = []
    if not uploaded_sources:
        return items

    for source in uploaded_sources:
        try:
            raw_bytes, suffix, display_name = _read_source_bytes(source)
        except Exception:
            continue

        if suffix in SUPPORTED_IMAGE_EXTENSIONS:
            items.append(
                {
                    "type": "input_image",
                    "image_url": _bytes_to_data_url(raw_bytes, suffix),
                    "detail": "high",
                }
            )
            continue

        if suffix in SUPPORTED_PDF_EXTENSIONS:
            try:
                items.extend(_pdf_pages_to_vision_items(raw_bytes, display_name, max_pages=8))
            except Exception:
                # If a PDF cannot be rendered, fall back to text context only.
                continue

    return items


def build_user_input(
    question: str,
    uploaded_sources: Iterable[Any] | None = None,
) -> str | list[dict[str, Any]]:
    """
    Build the actual Runner input.

    If images/PDF pages are present, return a Responses API-style input list so the
    model can use OpenAI vision natively. Otherwise return a plain text string.
    """
    vision_items = build_uploaded_vision_input_items(uploaded_sources)
    if not vision_items:
        return question

    content: list[dict[str, Any]] = [
        {"type": "input_text", "text": question},
        *vision_items,
    ]
    return [{"role": "user", "content": content}]


def get_session(session_id: str = "default_service_chat") -> SQLiteSession:
    """
    Return a stable SQLiteSession for a given conversation ID.
    """
    if session_id not in _SESSION_CACHE:
        _SESSION_CACHE[session_id] = SQLiteSession(session_id, str(SESSION_DB_PATH))
    return _SESSION_CACHE[session_id]

def build_agent(
    question: str,
    temporary_context: str | None = None,
    uploaded_sources: Iterable[Any] | None = None,
) -> Agent:
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
    temp_context = build_temporary_context(
        temporary_context=temporary_context,
        uploaded_sources=uploaded_sources,
    )

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
- Temporary uploaded-file context may help interpret the current conversation, but it must never be converted into permanent knowledge.

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
- temporary uploaded-file context
- or a combination of these

Knowledge excerpts:

{retrieved_context}

Temporary uploaded-file context:

{temp_context or "None"}
""".strip()

    return Agent(
        name="Service Coordinator Assistant",
        model="gpt-5.6-luna",
        instructions=human_instructions,
    )


# Public function used by the Streamlit application
def ask_service_assistant(
    question: str,
    session_id: str = "default_service_chat",
    temporary_context: str | None = None,
    uploaded_sources: Iterable[Any] | None = None,
) -> str:
    """
    Send a question to the Service Coordinator Assistant
    and return the response.

    Use temporary_context for OCR text or other transient evidence.
    Use uploaded_sources for file-like objects or uploaded file handles.
    """

    # Normal assistant path for everything else
    agent = build_agent(
        question,
        temporary_context=temporary_context,
        uploaded_sources=uploaded_sources,
    )
    session = get_session(session_id=session_id)
    user_input = build_user_input(
        question,
        uploaded_sources=uploaded_sources,
    )

    result = Runner.run_sync(
        agent,
        user_input,
        session=session,
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
        print(ask_service_assistant(question, session_id=terminal_session_id))
        print()