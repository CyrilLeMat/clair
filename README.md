# ✨ Clair

> A minimal, adversarial AI assistant that audits and challenges your internal documentation.

## 💡 What is Clair?

**Clair** is an open-source Python tool designed to test the clarity, consistency, and reliability of your internal knowledge base.

It scans your **Notion and Confluence** documentation (and soon Slack and others) using LLMs to:
- Detect **contradictions** between documents
- Flag **outdated** or unmaintained pages
- Surface **vague** or **ambiguous** phrasing
- Identify misalignment between **docs** and **actual team behavior** (via Slack integration)

Unlike helpful AI assistants, Clair takes an **adversarial** approach—seeking flaws, not answers.

---



## 🔍 Features (MVP)

- Scan Notion and Confluence pages via official APIs
- Vectorize and compare content to find contradictions
- Detect potentially outdated or unused docs
- Score clarity and usefulness using LLM prompts
- Generate a Markdown report (and optionally write back to Notion, Confluence, or Slack)

---

## 🛠️ Tech Stack

- Python 3.10+
- [`notion-client`](https://github.com/ramnes/notion-sdk-py) for Notion integration
- [`atlassian-python-api`](https://github.com/atlassian-api/atlassian-python-api) for Confluence support
- [`openai`](https://github.com/openai/openai-python) or [`llama-index`](https://github.com/jerryjliu/llama_index)
- `faiss` or `chromadb` for vector similarity
- Optional: Slack integration


---

## 🚧 Roadmap

- [ ] CLI (with `typer` or `click`)
- [ ] Export to Markdown + Notion + Confluence
- [ ] Contradiction detection module
- [ ] Outdated/irrelevant page detection
- [ ] Slack divergence detection (optional)
- [ ] Streamlit UI (optional)
- [ ] Full Confluence support: space traversal, content parsing, report writing

---

## 📦 Project Philosophy

Clair is built to challenge—not assist. Its goal is to:
- Stress-test assumptions
- Uncover blind spots in knowledge
- Encourage better writing, clearer thinking, and collective accountability

---

## 🤝 Contributing

1. Fork the repo
2. Create a new branch
3. Open a PR with a clear description and sample results

---

## 📄 License
MIT

---

## 🧬 Author
Cyril Le Mat – Clair was born from a love of clean docs, good questions, and adversarial design thinking.
