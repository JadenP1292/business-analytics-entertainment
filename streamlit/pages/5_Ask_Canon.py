import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import re

st.set_page_config(page_title="Ask Canon", page_icon="💬", layout="wide")
st.sidebar.title("📊 Canon Intelligence")
st.sidebar.divider()

st.title("💬 Ask Canon")
st.caption("Ask anything about Canon, its competitors, or the imaging industry. Answers come from the project knowledge base.")

WIKI_DIR = Path(__file__).parent.parent.parent / "knowledge" / "wiki"
RAW_DIR  = Path(__file__).parent.parent.parent / "knowledge" / "raw"

@st.cache_resource
def load_knowledge_base():
    docs = []
    for md in sorted(WIKI_DIR.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        docs.append({"source": f"wiki/{md.name}", "text": text, "priority": 0})
    for md in sorted(RAW_DIR.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        docs.append({"source": f"raw/{md.name}", "text": text, "priority": 1})
    return docs

def score(doc: dict, query: str) -> float:
    terms = re.findall(r"\w+", query.lower())
    text_lower = doc["text"].lower()
    hits = sum(text_lower.count(t) for t in terms if len(t) > 2)
    boost = 3.0 if doc["priority"] == 0 else 1.0
    return hits * boost

def retrieve(query: str, docs: list, top_k: int = 3) -> list:
    scored = [(score(d, query), d) for d in docs]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:top_k] if s > 0]

def excerpt(text: str, query: str, window: int = 800) -> str:
    terms = re.findall(r"\w+", query.lower())
    best_pos, best_hits = 0, 0
    for i in range(0, len(text), 200):
        chunk = text[i : i + window].lower()
        hits = sum(chunk.count(t) for t in terms if len(t) > 2)
        if hits > best_hits:
            best_hits, best_pos = hits, i
    return text[best_pos : best_pos + window].strip()

def answer(query: str, docs: list) -> tuple[str, list]:
    hits = retrieve(query, docs)
    if not hits:
        return "No relevant information found in the knowledge base for that question.", []
    parts = []
    for doc in hits:
        snip = excerpt(doc["text"], query)
        parts.append(f"**From `{doc['source']}`:**\n\n{snip}")
    return "\n\n---\n\n".join(parts), [d["source"] for d in hits]

docs = load_knowledge_base()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

EXAMPLES = [
    "What are Canon's main business segments?",
    "How does Canon compete with Sony in cameras?",
    "What is Canon's strategy according to IR sources?",
    "How is Xerox performing compared to Canon?",
    "What did Canon announce at NAB 2026?",
]
st.sidebar.markdown("**Example questions**")
for ex in EXAMPLES:
    if st.sidebar.button(ex, key=ex):
        st.session_state.messages.append({"role": "user", "content": ex})
        resp, sources = answer(ex, docs)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        st.rerun()

if prompt := st.chat_input("Ask about Canon or its competitors..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            resp, sources = answer(prompt, docs)
        st.markdown(resp)
        if sources:
            st.caption(f"Sources: {', '.join(sources)}")
    st.session_state.messages.append({"role": "assistant", "content": resp})
