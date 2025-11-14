Librarian
---------------------------
Command line tool and library for managing your vector store

Features:

- **Deduplication**: Automatically avoid re-importing the same file using content hashing
- **Command-line interface**: Manage your vector store with the `librarian` CLI tool
- **Multiple collections**: Organize documents into separate collections for different projects
- **File format support**: Import text, markdown, PDF, and EPUB files

Components
---------------------------
- Qdrant - vector store backend, files will be chunked, text, vector and metadata will be stored
- sqlite - to track imported files and avoid re-import the same file

Setup uv environment
---------------------------

- For first-time use run `uv run python -m librarian.setup.setup_pandoc`.
- Pandoc is required for converting EPUB files to text for processing



### For development 
```bash
uv venv 
uv sync --extra mcp
```

- use `--extra mcp` to install MCP support



### For Application
```bash
uv tool install -e .
```



Add librarian MCP
---------------------------

## Claude connect librarian MCP

```bash
claude mcp add librarian \
  -- uv run librarian-mcp
```

## Codex connect librarian MCP

```bash
codex mcp add librarian \
  --env QDRANT_DATA_PATH=/your-qdrant-home \
  -- uv run librarian-mcp
```

- codex mcp will NOT use env variables from your shell, so you need to set QDRANT_DATA_PATH here

Environment Variables
---------------------------

- QDRANT_DATA_PATH: path to store qdrant vector db data





Librarian Usage
---------------------------
`librarian` command line tool helps import files to vector store


## Status

`librarian` have important state `collection`, mostly command will operate on current collection.
Use `status` to check current collection and use `checkout` to switch collection.


```bash
> librarian status

                   Qdrant Configuration
 Qdrant Path      /home/kk/.local/opt/re-mind/qdrant-data
 Collection Name  trading

Collections:
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Collection Name        ┃ Points Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ __default_collection__ │            0 │
│ novel                  │        15508 │
│ tmp                    │          432 │
│ trading                │        54885 │
└────────────────────────┴──────────────┘


> librarian checkout novel
```



## Import file
`librarian add <path>` command will import file to vector store
`path` can be file or directory, directory will be imported recursively.
file type supported: .txt, .md, .pdf, .epub

```bash
> librarian add ~/books/


# use `ls` to see

```

Use `ls` to see imported files

```bash
❯ librarian ls
            Showing latest 10 documents (out of 15 total)
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Hash ID        ┃ File Name                   ┃ Created At          ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 2f3f620d5c4204 │ book.pdf                    │ 2025-11-14 12:41:41 │
│ ab67ad67d89309 │ irbookonlinereading.pdf     │ 2025-11-14 12:40:43 │
│ 20355ed64b3df2 │ RW.pdf                      │ 2025-11-14 12:39:36 │
│ 34d1945bacde62 │ 031013.pdf                  │ 2025-11-14 12:38:57 │
│ 1bc0e20a2f4bc0 │ thebook.pdf                 │ 2025-11-14 12:37:07 │
│ b9452a7e64809f │ casi_corrected_03052021.pdf │ 2025-11-14 12:36:38 │
│ 8d3e57fdeb3138 │ appdatasci.pdf              │ 2025-11-14 12:21:58 │
│ eea64b94a34d75 │ ADAfaEPoV.pdf               │ 2025-11-14 12:21:48 │
│ d9429e870b90e8 │ pg84-images-3.epub          │ 2025-11-14 12:19:38 │
│ f14c93a96b5aa2 │ pg5199-images.epub          │ 2025-11-14 12:19:22 │
└────────────────┴─────────────────────────────┴─────────────────────┘
```



