# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Rate My Professors reviews for Notre Dame CSE (Computer Science & Engineering) department professors. This knowledge is valuable because official course descriptions and university websites say nothing about actual teaching style, workload, exam difficulty, grading fairness, or how accessible a professor is outside class — yet those factors have a huge impact on a student's semester. Students rely on word-of-mouth or hours of scrolling RMP; this system makes that distributed knowledge instantly searchable and answerable.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | RMP – Daniel Cedre | 14 reviews across CSE10001 (Intro to CS) and CSE20110 (Discrete Math). Overall 2.4/5. | https://www.ratemyprofessors.com/professor/2935650 |
| 2 | RMP – Shreya Kumar | 10 reviews across CSE10001, EG10118, CSE30332, CSE40793, EG10112. Overall 3.2/5. | https://www.ratemyprofessors.com/professor/2551877 |
| 3 | RMP – Daniel Rehberg | 1 review for CSE20232 (Data Structures). Overall 1/5. | https://www.ratemyprofessors.com/professor/3152860 |
| 4 | RMP – Douglas Thain | 4 reviews across CSE30341 (OS) and CSE40771 (Distributed Systems). Overall 4/5. | https://www.ratemyprofessors.com/professor/2441081 |
| 5 | RMP – Katherine Walden | 5 reviews for CDT30010 (Computing & Digital Technologies). Overall 5/5. | https://www.ratemyprofessors.com/professor/2748451 |
| 6 | RMP – Ramzi Bualuan | 7 reviews for CSE20311 (Fundamentals of Computing). Overall 5/5. | https://www.ratemyprofessors.com/professor/2647156 |
| 7 | RMP – Peter Bui | 15 reviews across CSE20289 (Systems Programming) and CSE30341 (OS). Overall 4.5/5. | https://www.ratemyprofessors.com/professor/2539366 |
| 8 | RMP – Tijana Milenkovic | 6 reviews across CSE20110 (Discrete Math) and CSE20111 (Algorithms). Overall 2.3/5. | https://www.ratemyprofessors.com/professor/2054522 |
| 9 | RMP – Matthew Morrison | 12 reviews across CSE20312, CSE20133, CSE30321, CSE40462. Overall 3.1/5. | https://www.ratemyprofessors.com/professor/2484735 |
| 10 | RMP – Fred Nwanganga | 15 reviews for ITAO20210 (Intro to Python, Mendoza). Overall 4.4/5. | https://www.ratemyprofessors.com/professor/2675949 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
