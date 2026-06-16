# 03-traditional-rag — Retrieval-Augmented Generation from scratch

A basic RAG system built end to end, without a high-level chain abstraction: load
documents from many sources → chunk → embed → store in ChromaDB → semantic search →
feed top chunks to a local LLM to generate a grounded, cited answer. The conceptual
backbone for everything here is this folder's [`NOTES.md`](./NOTES.md) — start there.

## Notebooks (`notebooks/`)

| Notebook                      | Topic                                                                                         | NOTES.md ref |
| ----------------------------- | --------------------------------------------------------------------------------------------- | ------------ |
| `01-document-loaders.ipynb`   | The `Document` object + loaders: `TextLoader`, `DirectoryLoader`, `PyPDFLoader`/`PyMuPDFLoader`, `DataFrameLoader` (Excel), `SQLDatabaseLoader` | §1           |
| `02-rag-pipeline.ipynb`       | Full pipeline: chunking (`RecursiveCharacterTextSplitter`) → embeddings (`SentenceTransformer`) → ChromaDB vector store → retriever → LLM generation | §2–7         |

The diagram [`1-langchain-document-components.svg`](./1-langchain-document-components.svg)
illustrates the `Document` / loader components from notebook `01`.

## Data (`data/`)

Sample corpora the notebooks load from (all referenced as `../data/...`):

| Path                  | Used by              | Contents                                  |
| --------------------- | -------------------- | ----------------------------------------- |
| `text_files/`         | text / directory loaders | small `.txt` samples                  |
| `pdf_files/`          | PDF loaders, pipeline    | a sample PDF (System Design Interview) |
| `excel_files/`        | Excel / DataFrame loader | `products.xlsx`                        |
| `db/company.db`       | SQL loader               | a small SQLite database                |
| `vector_store/`       | the RAG pipeline         | persisted ChromaDB index (regenerable by re-running `02`) |

## Setup

Environment is shared at the repo root — see the [root README](../README.md). After
`uv sync`, open `notebooks/*.ipynb` and select the root `.venv` kernel. Generation uses
a local [Ollama](https://ollama.com/) model; embeddings download `all-MiniLM-L6-v2` from
Hugging Face on first run.
