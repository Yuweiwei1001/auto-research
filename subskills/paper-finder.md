---
name: paper-finder
description: "Finds and organizes research papers based on textual descriptions and keywords. Searches across arxiv, Google Scholar, Semantic Scholar, and top venues. Maintains a persistent memory bank of discovered papers, a mind-graph linking papers to topics, individual paper summaries, and BibTeX entries. Use this skill whenever the user wants to find papers, search for related work, build a literature review, discover what exists on a topic, compare papers, organize references, generate BibTeX, or manage a research paper collection. Also use when the user mentions 'find me papers on...', 'what papers exist about...', 'related work for...', 'literature search', 'paper survey', or references any conference/venue by name."
---

# Paper Finder

Research paper discovery and organization agent. Find relevant papers across any domain, organize them into a persistent knowledge base, and connect them across topics.

Designed as a companion skill for [auto-research](../SKILL.md) — invoked during Phase 1 (Innovation Source Search) to systematically discover papers that inform hypothesis generation.

## Directory Structure

Each search/topic gets its own folder. The folder name should be a short, descriptive kebab-case name for the search topic (e.g., `multimodal-federated-learning/`, `knowledge-distillation-survey/`). The user may also specify a custom folder name. Create on first use:

```
<topic-name>/
  memory-bank.md        # Master list of all discovered papers
  mind-graph.md         # Topic-paper connection graph
  summaries/            # Per-paper .md files
  references.bib        # Combined BibTeX for all papers
  pdfs/                 # Downloaded PDFs (only when user asks)
  discussions/          # Paper comparison logs
```

If the user references an existing folder (e.g., `@multimodal-federated-learning/`), operate within that folder. If starting a new search without a specified folder, derive a descriptive name from the search query.

## Searching for Papers

### Web search is mandatory

Use WebSearch and WebFetch for every search. Training knowledge alone misses recent papers. If web tools are denied, retry once, then tell the user you need web access and explain what you'd search for.

### Search strategy

Run 2-3 parallel searches per query:

1. **Semantic Scholar API** via WebFetch:
   ```
   https://api.semanticscholar.org/graph/v1/paper/search?query=<query>&limit=20&fields=title,authors,year,venue,abstract,externalIds,citationCount,url
   ```
2. **WebSearch** with queries like `<topic> paper <venue> <year>` — good for Google Scholar results
3. **Venue-specific** when relevant: `<topic> NeurIPS 2025`, `<topic> site:openreview.net`
4. **Follow citations** on Semantic Scholar for highly relevant papers:
   ```
   https://api.semanticscholar.org/graph/v1/paper/<paper_id>/citations?limit=20&fields=title,authors,year,venue,abstract,citationCount
   https://api.semanticscholar.org/graph/v1/paper/<paper_id>/references?limit=20&fields=title,authors,year,venue,abstract,citationCount
   ```

### Relevant venues by field

| Field | Venues |
|-------|--------|
| ML/AI | NeurIPS, ICML, ICLR, AAAI, IJCAI, COLM |
| CV | CVPR, ECCV, ICCV, WACV, BMVC |
| NLP | ACL, EMNLP, NAACL, COLING |
| Data Mining | KDD, WWW, SIGIR, CIKM |
| Robotics | CoRL, RSS, ICRA, IROS |
| Medical | MICCAI, ISBI |
| Graphics | SIGGRAPH, SIGGRAPH Asia, 3DV |
| Systems | OSDI, SOSP, MLSys, MobiSys |
| Federated/Distributed | IEEE TMC, Information Fusion, AISTATS |
| Preprints | arXiv (cs.LG, cs.CV, cs.CL, cs.AI, cs.DC) |

### Multi-angle search (mandatory)

A single concept can be described using very different vocabulary depending on the angle. After the initial direct-concept searches, you MUST run at least one additional search round covering these three angles. Skipping these is the #1 cause of missed papers.

1. **Cross-domain synonyms**: The same idea often has established names in adjacent fields. Before searching, brainstorm 2-3 alternative terms from related domains. For example, "modality imputation" in ML maps to "missing data reconstruction" in statistics, "sensor fusion with dropout" in IoT, or "incomplete multimodal learning" in CV. Search using these alternative vocabularies.

2. **Enabling mechanisms / building blocks**: Search for the specific technical components needed to *implement* the concept — not just the concept itself. Every novel method requires specific loss functions, attention mechanisms, aggregation strategies, etc. For example, "cross-modal knowledge transfer" requires prototype alignment, contrastive distillation, or feature reconstruction losses. Search for these mechanism-level terms.

3. **Motivating applications / problem framing**: Papers solving the same technical problem may frame it as a different goal. Search from the perspective of *why* someone would build this (robustness, efficiency, privacy, hardware constraints). For example, "modality-agnostic representation" and "heterogeneous client aggregation" both address missing modalities in FL, but from different framings.

After initial results come in, also **follow the citation graph**: fetch the related-work section of 1-2 top-relevance papers and scan for references you haven't found yet.

### Understand the concept precisely

Before searching, understand the exact technical distinction the user cares about. If they describe a specific mechanism (e.g., "prototype alignment for missing modalities in federated learning"), search for that literal property — don't broaden to superficially similar but technically different work (e.g., general federated aggregation, standard knowledge distillation).

### Filtering

- **Prioritize algorithmic contributions** over architecture/engineering/systems papers
- **Prioritize recent work** (2024-2026) — skip well-known basics unless directly relevant
- **Note citation counts** when available
- **Tier results** by relevance to the user's specific concept:
  - Tier 1: Directly addresses the exact problem
  - Tier 2: Addresses a closely related problem or provides key building blocks
  - Tier 3: Tangentially related or provides context

## Memory Bank (`memory-bank.md`)

Master record of all discovered papers. Append new entries, never overwrite. Read existing file before searching to avoid duplicates.

```markdown
# Paper Memory Bank
Last updated: YYYY-MM-DD

### [short-id] Paper Title
- **Authors**: Author list
- **Venue**: Conference/Journal, Year
- **URL**: Link to paper
- **Citations**: N (if known)
- **Status**: discovered | summarized | analyzed
- **Topics**: topic1, topic2
- **Abstract**: 1-2 sentence description
- **Key technique**: Core technical contribution
- **Notes**: Relevance observations
---
```

## Mind Graph (`mind-graph.md`)

Topic-centric hierarchy — NOT pairwise paper comparisons. Each topic has 1-3 umbrella/landmark papers plus other relevant work.

```markdown
# Mind Graph
Last updated: YYYY-MM-DD

### Topic Name
- **Description**: One-line description
- **Related topics**: [other topic], [other topic]
- **Key papers**:
  - [short-id] Paper Title (Venue Year) — why it's key for this topic
- **Other relevant papers**:
  - [short-id] Paper Title — one-line note
- **Open questions**:
  - What hasn't been solved yet in this topic?
```

## BibTeX (`references.bib`)

Write a single combined `references.bib` file with all papers. Use `@inproceedings` for conferences, `@article` for journals, `@misc` for arXiv preprints. Citation key = short-id.

## Paper Summaries and Comparisons

- **Summaries**: Save to `summaries/<short-id>.md`. Include: problem, method, key results, limitations, relevance to current research.
- **Comparisons**: Read existing summaries first, save discussion to `discussions/<descriptive-name>.md`.
- **References to known papers**: Search summaries and memory bank first. Only re-search if the user explicitly asks.

## PDF Management

Do NOT download PDFs unless the user explicitly asks. When asked:

1. **Read `references.bib`** to extract the arXiv eprint ID or URL for each paper.
2. Construct the PDF URL from the arXiv ID: `https://arxiv.org/pdf/<eprint-id>`
3. Download and save to `pdfs/<short-id>.pdf`
4. Only fall back to memory-bank.md or web search if a paper has no entry in references.bib.

## Integration with Auto-Research

When invoked from the auto-research loop (Phase 1):

1. Read `experiments/research_domain.yaml` → `literature_references` for known papers
2. Read `experiments/loop_contract.md` → current bottleneck and待探索方向
3. Search for papers addressing the current bottleneck
4. Output: ranked paper list + extracted techniques that could inform new hypotheses
5. Update `literature_references` in research_domain.yaml with newly discovered papers

### Output format for auto-research integration

```json
{
  "search_query": "描述搜索了什么",
  "papers_found": 12,
  "top_papers": [
    {
      "title": "Paper Title",
      "venue": "NeurIPS 2025",
      "year": 2025,
      "citations": 42,
      "key_technique": "核心技术描述",
      "relevance": "与当前瓶颈的关系",
      "usable_modules": ["可提取用于假设的技术模块"]
    }
  ],
  "suggested_hypotheses": [
    "基于发现论文提出的实验假设"
  ]
}
```

## Interaction Flow

1. **Search**: Run parallel web searches, present ranked list (title, venue, year, citations, one-line description)
2. **Record**: Add papers to memory-bank.md, update mind-graph.md, write references.bib
3. **Ask**: Whether user wants deeper analysis of any specific papers
4. **Connect**: If running within auto-research, map findings to actionable hypotheses
