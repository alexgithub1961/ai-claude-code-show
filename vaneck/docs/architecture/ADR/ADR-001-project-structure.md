# ADR-001: Project Structure and Architecture

## Status
Accepted

## Context
We need to design a Python-based ETF data downloader system for VanEck that can:
- Scrape fund data from VanEck's ETF finder
- Download relevant data files for each fund
- Store files in an organised manner
- Support resumable downloads with error handling
- Be containerised for easy deployment

## Decision
We will implement a clean architecture with the following structure:
```
vaneck/
├── src/
│   ├── vaneck_downloader/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── scraper.py
│   │   ├── downloader.py
│   │   ├── storage.py
│   │   └── config.py
├── shell/
│   ├── build.sh
│   ├── run.sh
│   └── dev.sh
├── download/
├── docs/
│   └── architecture/
│       └── ADR/
├── tests/
├── pyproject.toml
├── Dockerfile
├── .dockerignore
└── README.md
```

**Key Architectural Decisions:**
1. **Modular Design**: Separate concerns into distinct modules (scraper, downloader, storage)
2. **uv + venv**: Use uv for fast dependency management with virtual environments
3. **Docker Volume Mount**: Mount download/ directory as volume for persistence
4. **Resumable Downloads**: Implement checkpointing for large file downloads
5. **Error Handling**: Comprehensive retry logic with exponential backoff

## Consequences
**Positive:**
- Clear separation of concerns enables easy testing and maintenance
- Docker containerisation ensures consistent deployment
- Resumable downloads prevent data loss on network failures
- Volume mounting preserves data between container runs

**Negative:**
- Additional complexity compared to a single-script solution
- Docker overhead for simple local development
- Need to manage volume permissions and mounting