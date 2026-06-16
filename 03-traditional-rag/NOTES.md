# Traditional RAG — Durable Reference

A personal reference distilled from building a basic RAG system end to end:
document loading → chunking → embedding → semantic search → generation. Organized
by concept, not by notebook order. The code in `notebooks/` cross-references these
sections (`01-document-loaders.ipynb` → §1; `02-rag-pipeline.ipynb` → §2–7).

---

## 1. Document Loaders & the `Document` object

Every LangChain loader (text, PDF, Excel, SQL, web...) normalizes any source into a
uniform list of `Document` objects. That's the loader's whole job: make the rest of the
pipeline source-agnostic.

A `Document` has two main properties:

| Property       | Type  | Holds                                              |
|----------------|-------|----------------------------------------------------|
| `page_content` | `str` | The actual text — this is what gets embedded       |
| `metadata`     | `dict`| Info *about* the text (source, page, author, ...)  |

(Plus an optional `id`, often `None`, used by vector stores.)

**`page_content`** = plain string. Loaders preserve raw formatting (`\n`, blank lines,
extra whitespace) — they don't clean it. Cleaning/splitting comes later.

**`metadata`** varies by loader:
- Text / Directory → minimal, usually `{'source': '<path>'}`
- PDF → richer: `source`, `page`, `total_pages`, title, author, creation date
- DataFrame / Excel → every column *except* the content column becomes metadata
- SQL → you choose which columns form the text vs. the metadata

**Granularity (how many Documents you get):**
- TextLoader → 1 per file
- DirectoryLoader → 1 per matching file
- PDF → **1 per page**
- DataFrame / Excel → **1 per row**
- SQL → **1 per row**

Why it matters for RAG: `page_content` gets embedded & retrieved; `metadata` rides along
untouched for filtering, citations, and tracing answers back to the source.

---

## 2. Chunking — `RecursiveCharacterTextSplitter`

### Core idea: "recursive" = hierarchical separators
Given an ordered separator list (most → least preferred):
```python
separators=["\n\n", "\n", " ", ""]
```
It splits on the first separator (paragraphs). If a piece is still bigger than
`chunk_size`, it recursively re-splits *that piece* with the next separator (lines, then
words, then characters). This keeps semantically related text together — it only breaks
paragraphs/lines when it must. Preferred over the blunt `CharacterTextSplitter`.

### The two knobs
- **`chunk_size=1000`** — a *target ceiling*, not an exact size. Measured in **characters**
  here (`length_function=len`), NOT tokens. Many chunks come out smaller because it stops
  at natural boundaries. (269 pages → 440 chunks in this run.)
- **`chunk_overlap=200`** — each chunk repeats the last ~200 chars of the previous one, so
  a sentence split across a boundary isn't lost. Rule of thumb: overlap ≈ 10–20% of
  `chunk_size` (200/1000 = 20%, reasonable).

### Crucial, easy-to-miss points
1. Chunk size is a **precision/context tradeoff**: smaller = more precise matches but less
   context; larger = more context but "blurry" embeddings (one vector averaging many
   topics → worse similarity scores).
2. `split_documents()` **preserves metadata** — every chunk inherits its parent page's
   metadata. This is what powers citations. (Use it instead of `split_text`, which loses
   metadata.)
3. It splits **each Document independently** → with page-based PDF loading, it never merges
   across pages. A paragraph spanning two pages becomes two chunks.
4. The final `""` separator can break **mid-word** if a single token exceeds `chunk_size`
   (rare in prose; relevant for code/URLs/tables).

Tuning tip: chunk config is the cheapest place to win retrieval quality. Try
`chunk_size=500, chunk_overlap=100` and compare scores.

---

## 3. Embeddings

### NumPy
The numerical substrate — fast, multi-dimensional arrays (`ndarray`). Vectors = 1D,
matrices = 2D. Used because it's vectorized (C-speed), has shape/math semantics built in,
and is the common language across sentence-transformers, scikit-learn, and ChromaDB.

### SentenceTransformer
Loads a pretrained model that maps text → a single fixed-length vector capturing meaning.
`all-MiniLM-L6-v2` → 384-dim vectors. Similar meanings land close together — the
foundation of semantic search.

`.encode()`:
- single string → `(384,)`
- list of strings → `(N, 384)`
- The base sentence-transformers models are **text-only**. Other modalities need different
  checkpoints — e.g. **CLIP** (`clip-ViT-B-32`) encodes images *and* text into the **same**
  space (search images with a text query). Same `.encode()` API, different model.
- `all-MiniLM-L6-v2` max input ≈ 256 tokens; longer text is **silently truncated** — which
  is exactly why chunking matters.

---

## 4. What "shape" means
Dimensions of a NumPy array — "how many of something, each of what size":
- `(440, 384)` → 440 chunks, each a 384-number vector
- `(1, 384)`   → 1 query, 384 numbers
- `(384,)`     → a single vector (1D)

384 is fixed by the model.

---

## 5. Semantic search

Keyword search matches **words**; semantic search matches **meaning**. It can find a
"throttling algorithms" passage from a "rate-limiting techniques" query because it compares
*ideas*, not characters.

**How meaning fits in numbers:** think of each dimension as a "feature" of meaning. Toy 3D
example:
```
"the cat slept"      -> [0.9, 0.0, 0.1]   (animals)
"my dog is hungry"   -> [0.8, 0.0, 0.6]   (animals + food)  ← close to cat
"the server crashed" -> [0.0, 0.9, 0.0]   (tech)            ← far from both
```
Scale that to 384 dims, learned (not human-labeled) from billions of sentences during
training. The model learned a geometric *map* of language — "understanding" is statistical,
not human.

**Query's journey:**
```
query text → encode() → (1, 384) → compare vs all (440, 384) chunk vectors
           → measure closeness (cosine) → keep nearest n → top chunks
```

Mental model: **embedding turns text into a location in meaning-space; semantic search is
finding the nearest neighbors to the query's location.** Search quality is capped by the
embedding model (small MiniLM → modest ~0.4 scores; bigger models separate meanings better).

---

## 6. Cosine similarity / angle

Vectors are **arrows** (direction in space). Cosine measures the **angle** between two
arrows, ignoring their length:
```
cos(θ) = (A · B) / (|A| × |B|)
```
- θ = 0°  → cos = 1.0  → same direction → same meaning
- θ = 90° → cos = 0.0  → unrelated
- θ = 180°→ cos = -1.0 → opposite meaning

(Score 0.39 ≈ 67° apart — partly aligned. 0.9 ≈ 26°, much tighter.)

**Why angle, not Euclidean distance?** Distance is polluted by **magnitude**, which often
encodes text length, not meaning. A one-line summary and a full paragraph on the same topic
point the **same direction** (cosine matches them ✓) even though their arrow tips are far
apart (distance would wrongly say "different" ✗). The `÷ (|A|×|B|)` part normalizes both
arrows to length 1, leaving only direction.

- Most embedding models output already-normalized vectors.
- For length-1 vectors, ranking by cosine == ranking by Euclidean distance → that's why
  ChromaDB returns a distance and the code recovers `similarity = 1 - distance`.
- **Dot product intuition:** high on the *same* dimensions → large product → aligned; high
  on *different* dimensions → near zero → unrelated.

Takeaway: **direction is meaning; length is noise — divide it out.**

---

## 7. Embedding models vs. LLMs — related but distinct

Both are built on the **Transformer** architecture; both turn text into vectors internally.
But they're trained for **opposite goals**:

|                | Embedding model              | LLM                          |
|----------------|------------------------------|------------------------------|
| Job            | Text → **one meaning vector**| Predict **next token** → text|
| Output         | Numbers, e.g. `(384,)`       | Words / an answer            |
| Optimized for  | Similar meanings land close  | Fluent, correct continuations|
| Size           | Small (MiniLM ≈ 22M)         | Large (Qwen3 8B ≈ 8B)        |
| Direction      | Compress meaning             | Expand a prompt              |

Precise relationships:
1. Every LLM has an **embedding layer** inside (token-level vectors) — but that's not the
   same as a whole-sentence embedding.
2. Dedicated embedding models are often a **language model fine-tuned** specifically to
   produce good sentence vectors.
3. You **don't** train one to get the other; in RAG they're two separate tools:
   embedding model = **retrieval** (the librarian), LLM = **generation** (the writer).

Big LLMs *can* embed (often better) but are slow/expensive — so RAG uses a small fast
embedding model for retrieval and saves the big model for the single generation step.
Engineering tradeoff, not a capability law.

---

## Pipeline at a glance
```
load (Documents) → split (chunks, keep metadata) → embed (vectors)
→ store in ChromaDB → query: embed question → cosine nearest-neighbors
→ top chunks as context → LLM writes the answer (with citations)
```
