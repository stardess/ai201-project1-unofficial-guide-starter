# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Rate My Professors (RMP) reviews for Notre Dame CSE (Computer Science & Engineering) and IT/Analytics department professors. Official course descriptions and university websites say nothing about actual teaching style, exam difficulty, workload, or grading fairness — yet those factors determine whether a student has a productive semester or a miserable one. Students currently rely on word-of-mouth or manually scrolling through RMP pages one professor at a time. This system makes that distributed student knowledge instantly searchable and answerable in plain language.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | RMP – Daniel Cedre | RMP professor page (14 reviews, CSE10001 & CSE20110) | https://www.ratemyprofessors.com/professor/2935650 |
| 2 | RMP – Shreya Kumar | RMP professor page (10 reviews, CSE10001, EG10118, CSE30332, CSE40793) | https://www.ratemyprofessors.com/professor/2551877 |
| 3 | RMP – Daniel Rehberg | RMP professor page (1 review, CSE20232) | https://www.ratemyprofessors.com/professor/3152860 |
| 4 | RMP – Douglas Thain | RMP professor page (4 reviews, CSE30341 & CSE40771) | https://www.ratemyprofessors.com/professor/2441081 |
| 5 | RMP – Katherine Walden | RMP professor page (5 reviews, CDT30010) | https://www.ratemyprofessors.com/professor/2748451 |
| 6 | RMP – Ramzi Bualuan | RMP professor page (7 reviews, CSE20311) | https://www.ratemyprofessors.com/professor/2647156 |
| 7 | RMP – Peter Bui | RMP professor page (15 reviews, CSE20289 & CSE30341) | https://www.ratemyprofessors.com/professor/2539366 |
| 8 | RMP – Tijana Milenkovic | RMP professor page (6 reviews, CSE20110 & CSE20111) | https://www.ratemyprofessors.com/professor/2054522 |
| 9 | RMP – Matthew Morrison | RMP professor page (12 reviews, CSE20312, CSE20133, CSE30321) | https://www.ratemyprofessors.com/professor/2484735 |
| 10 | RMP – Fred Nwanganga | RMP professor page (15 reviews, ITAO20210) | https://www.ratemyprofessors.com/professor/2675949 |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Each RMP review is a self-contained opinion block — typically 100–500 characters of opinion text plus a few metadata lines (course, grade, attendance). A 500-character chunk is large enough to hold one complete review in most cases, keeping the student's full opinion together with its context. Going smaller (e.g., 150 chars) would separate the metadata header from the opinion body, producing uninterpretable fragments. Going larger (e.g., 1,000 chars) would merge two reviews into one chunk, muddying attribution and diluting retrieval signal. The 50-character overlap catches reviews that straddle a boundary, ensuring neither resulting chunk loses the end of a key sentence. Every chunk is prefixed with `[Professor: X | Course: Y]` during ingestion to guarantee attribution even for overflow chunks (those that start mid-review after a split).

**Final chunk count:** 131 chunks across 10 documents (89 source reviews). Short reviews produce 1 chunk; longer reviews produce 2 via the overlap splitter.

**Sample chunks:**

1. `[Professor: Katherine Walden | Course: CDT30010] ... Her class was very casual and I am so happy I get to have her again next semester. Each assignment was pass/fail and you get two tries per assignment with feedback from the TAs. The number of "fails" you have at the end determines your grade. Sometimes she brings her dog to class too. Tags: ACCESSIBLE OUTSIDE CLASS, GRADED BY FEW THINGS, CARING`

2. `[Professor: Peter Bui | Course: CSE20289] ... Systems is the hardest class Bui teaches and the exams are pretty difficult. OS and Programming Challenges are both easier (PC easiest). That being said, Bui is the best prof I've had and he is so willing to support his students. His instructions are super clear and it's easy to get 100% on all homeworks. He cares about you as a per`

3. `[Professor: Daniel Cedre | Course: CSE10001] Course: CSE10001 Date: Nov 14th, 2025 Attendance: Not Mandatory Grade: B Textbook: N/A  The lectures were impossible to follow, the problem sets were REALLY hard in general, and the class structure was incredibly unorganized. AVOID HIM!`

4. `[Professor: Tijana Milenkovic | Course: CSE20110] ... Getting very small things wrong can cost you a lot of points, especially in the first half of the class. Tags: TOUGH GRADER`

5. `[Professor: Ramzi Bualuan | Course: CSE20311] Course: CSE20311 Date: Jan 17th, 2025 ... Great at building the foundations for new programmers. Tags: CLEAR GRADING CRITERIA, LECTURE HEAVY`

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs entirely locally — no API key, no rate limits, no cost).

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is well-suited for this corpus: it handles informal, colloquial English (student slang like "goated," "impossible," "war crime") reasonably well, runs in seconds on CPU, and fits within the 256-token context limit for our ~125-token chunks. For a real deployment I would weigh four tradeoffs: (1) **Accuracy vs. speed** — `all-mpnet-base-v2` scores ~5% higher on semantic similarity benchmarks but is 3× slower; the gain may not justify the latency for an interactive tool. (2) **Domain specificity** — a model fine-tuned on educational review text would embed phrases like "tough grader" or "accessible outside class" more precisely than a general-purpose model, likely improving retrieval for exactly those common student queries. (3) **Context length** — `all-MiniLM-L6-v2`'s 256-token limit is sufficient here but would truncate longer source documents (syllabi, course wikis); a model like `nomic-embed-text` (8,192 tokens) would be necessary for that. (4) **Local vs. API** — OpenAI `text-embedding-3-small` offers strong quality at low cost, but adds network latency, a dependency on API availability, and per-token costs that scale with usage; local is more resilient for a student tool with variable traffic.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt passed to `llama-3.3-70b-versatile` contains the following hard rules:

> *"Answer ONLY using information from the provided student reviews below. Do not use any outside knowledge. If the reviews do not contain enough information to answer the question, respond with exactly: 'I don't have enough information in the available reviews to answer that.' Never invent, assume, or extrapolate facts not stated in the reviews."*

The temperature is set to `0.2` to minimize hallucination and keep the model close to retrieved text. The retrieved chunks are numbered and labeled with professor name and course code before being injected into the user message, making it easy for the model to cite which review it is drawing from.

**How source attribution is surfaced in the response:** Source attribution is **programmatically guaranteed** — it never depends on the LLM. After generation, `generator.py` extracts the `source` field from each retrieved chunk's metadata dictionary and appends the deduplicated list to the response. Even if the LLM omitted citations or fabricated a source name, the displayed attribution would still reflect the actual retrieved files. The Gradio interface shows these source filenames in a dedicated "Retrieved from" panel, separate from the answer text.

**Sample grounded response:**
> Query: *"What is Katherine Walden's grading system in CDT30010?"*
> Answer: *"According to Reviews 2–4 for Katherine Walden's CDT30010, her grading system involves signing a contract for the desired grade, pass/fail assignments with two attempts each, and the number of fails at the end of the semester determining the final grade. No traditional exams."*
> Source: `prof_Walden_rmp.txt`

**Sample out-of-scope refusal:**
> Query: *"What is the best restaurant near Notre Dame campus?"*
> Answer: *"I don't have enough information in the available reviews to answer that."*
> Source: (retrieval pulled unrelated chunks, but the LLM correctly refused to answer from them)

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is Katherine Walden's grading system in CDT30010? | Contract grading: students commit to a grade, pass/fail assignments with 2 attempts, number of fails determines grade, no exams. | Correctly described contract grading, pass/fail assignments with two tries, fails determining final grade. Cited Reviews 2–4. | Relevant — all 5 chunks from Walden's file | Accurate |
| 2 | How hard are Peter Bui's exams in Systems Programming (CSE20289)? | Very hard / "impossible" even with open notes; 60 pts total; ~1 letter grade drop per 10 pts lost; extra credit strongly recommended. | Correctly synthesized "pretty difficult," "impossible," "very difficult tests" from multiple reviews. Did not mention the 60-point scale or grade-per-10-pts detail (not in retrieved chunks). | Relevant — top 4 chunks directly about Systems exams | Partially accurate (correct sentiment, missing numeric grading detail) |
| 3 | Does Daniel Cedre require office hours to pass CSE10001? | Yes — homework cannot be completed from lectures alone; students must attend office hours. | Correctly identified that problem sets "could only be done in office hours." Appropriately hedged that the reviews don't explicitly say office hours are required *to pass*. Retrieved 1 off-topic Morrison chunk (rank 4). | Partially relevant — 1 of 5 chunks from wrong professor | Partially accurate (correct core answer, over-hedged due to irrelevant chunk) |
| 4 | What do students say about Tijana Milenkovic's grading strictness in Discrete Math? | Harsh grader, penalizes small notation errors heavily, no extra credit to recover points. | Correctly quoted "getting very small things wrong can cost you a lot of points" and "you won't ever have the opportunity to get them back." Also tagged TOUGH GRADER. One Cedre chunk appeared in sources but did not pollute the answer. | Partially relevant — 1 of 5 chunks from wrong professor (Cedre) | Accurate (correct answer despite off-target chunk in retrieval) |
| 5 | Is Ramzi Bualuan recommended for students with no prior CS experience in CSE20311? | Yes — accessible, engaging, builds foundations well; class is project-heavy but manageable. | Correctly cited "Great at building the foundations for new programmers." However, only surfaced one review; missed the richer endorsements in other retrieved chunks. | Relevant — all 5 chunks from Bualuan's file | Partially accurate (correct conclusion, underutilized retrieved context) |

**Retrieval quality key:** Relevant / Partially relevant / Off-target  
**Response accuracy key:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "What do students say about Tijana Milenkovic's grading strictness in Discrete Math?" (Q4) and "Does Daniel Cedre require office hours to pass CSE10001?" (Q3) — both returned one off-target chunk from the wrong professor.

**What the system returned:** For Q4 (Milenkovic), retrieval rank 5 returned a chunk from `prof_Cedre_rmp.txt` (Daniel Cedre's CSE20110 Discrete Math reviews) alongside four correct Milenkovic chunks. For Q3 (Cedre), retrieval rank 4 returned a Morrison chunk. The LLM's answers were still largely correct because the off-target chunks were ranked low and the LLM grounded primarily on the higher-ranked correct chunks — but the source list incorrectly showed a second professor's file.

**Root cause (tied to a specific pipeline stage):** The failure originates in the **chunking + embedding stage**. Both Cedre and Milenkovic teach Discrete Math (CSE20110), so their review chunks contain many of the same terms: "discrete math," "office hours," "homework," "tough grader." The embedding model (`all-MiniLM-L6-v2`) represents these semantically similar chunks close together in vector space, and there is no metadata filter on professor name during retrieval. When a query about Milenkovic's grading is embedded, the cosine similarity between that query vector and a Cedre Discrete Math chunk is high enough to place it in the top-5 — not because the content is relevant, but because the surface vocabulary overlaps. The specific mechanism: both professors are described with "tough grader" tags and "office hours" language, which the general-purpose embedding model treats as strong semantic signals regardless of which professor wrote the reviews.

**What you would change to fix it:** Add a **metadata filter** to `retriever.py` that accepts an optional `professor` parameter and passes it as a ChromaDB `where` clause (e.g., `{"professor": "Tijana Milenkovic"}`). When the query mentions a professor name, extract it and restrict retrieval to only that professor's chunks. This would be straightforward to implement since each chunk already stores `professor` in its metadata. Alternatively, implementing **hybrid search** (BM25 + semantic) would down-rank chunks where the professor name doesn't appear in the text, since keyword match would penalize cross-professor results.

---

## Spec Reflection

**One way the spec helped you during implementation:** The specification's chunking strategy section required me to think through document structure before writing a single line of `ingest.py`. The decision to treat each `---`-delimited review block as the primary unit — and to prepend `[Professor: X | Course: Y]` to every chunk — came directly from writing out the spec. Without that upfront reasoning I would likely have chunked by raw character count without metadata prefixing, which would have produced chunks unreadable in isolation (a reviewer's second sentence with no context about who or what course it concerns). The spec forced me to reason about what a chunk needs to be *useful* before I wrote the splitter logic.

**One way your implementation diverged from the spec, and why:** The spec described storing professor and course as ChromaDB *metadata fields only*, with chunk text being pure review content. The actual implementation also *inlines* the professor and course as a text prefix (`[Professor: X | Course: Y]\n`). This divergence emerged during testing: chunks like "She is great and cares" are uninterpretable when printed in retrieval output with no inline context. Prefixing attribution directly into the text also means the embedding now encodes professor identity as part of the semantic vector, making retrieval slightly more precise for professor-specific queries. The spec assumed metadata would be sufficient; implementation revealed that embedding the attribution directly produces better grounding and more readable outputs.

---

## AI Usage

**Instance 1 — Generating `ingest.py` from the Chunking Strategy spec section:**
I gave GitHub Copilot (Claude Sonnet 4.6 via VS Code Copilot Chat) the full Chunking Strategy section from `planning.md`, which specified 500-char chunks, 50-char overlap, `---`-separated review blocks, and a metadata prefix format. It produced a working `load_and_chunk_documents()` function with a character-level sliding-window splitter. I overrode two things: (1) the original generated code treated the first line of every file as a professor header regardless of content — I directed the AI to add `_parse_professor_name()` to detect the actual `Prof:` header format; (2) the generated code did not skip empty or header-only blocks, producing zero-content chunks — I directed it to add a minimum length guard (`if len(text) < 40: continue`).

**Instance 2 — Generating `retriever.py` from the Retrieval Approach spec section:**
I gave GitHub Copilot the Retrieval Approach section from `planning.md` (model name, vector DB choice, top-k, distance metric, evaluation queries). It produced working `embed_and_store()` and `retrieve()` functions. I directed two additions not in the spec: (1) an idempotent `get_or_build_collection()` wrapper that checks chunk count before re-embedding — important because re-embedding on every import would add 10–20s startup time to `app.py`; (2) using the IDs format `"{source}_chunk_{i}"` for ChromaDB upserts (rather than random UUIDs), making it possible to debug which source a chunk came from directly from the stored ID. Both additions came from me identifying production reliability concerns that the spec didn't surface.
