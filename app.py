"""Grounded Biotechnology Study Assistant — simple, no API key required."""
import re
from knowledge import KNOWLEDGE

OFF_TOPIC_TERMS = {
    "politics", "election", "celebrity gossip", "dating advice", "stock price",
    "football score", "write malware", "make a bomb", "hack someone's account"
}
UNSAFE_PATTERNS = [
    r"\bmake (a )?bomb\b",
    r"\bbuild (a )?weapon\b",
    r"\bhack (someone|somebody|my friend's|another person's) account\b",
    r"\bsteal passwords?\b",
]

def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))

def estimated_tokens(text: str) -> int:
    """Rough estimate only; not an exact model tokenizer or billed usage."""
    return max(1, (len(text) + 3) // 4) if text.strip() else 0

def answer_question(question: str) -> dict:
    q = question.strip()
    if not q:
        return {"answer": "Please enter a question.", "status": "empty", "sources": [], "input_tokens_est": 0, "output_tokens_est": 0}

    q_lower = q.lower()
    if any(re.search(p, q_lower) for p in UNSAFE_PATTERNS):
        answer = "I can’t help with harmful or unsafe instructions. I can help with safe, educational biotechnology topics instead."
        return _result(answer, "refused_unsafe", [], q)

    if any(term in q_lower for term in OFF_TOPIC_TERMS):
        answer = "That request is outside my remit. I only answer questions using the built-in biotechnology study notes."
        return _result(answer, "refused_off_topic", [], q)

    q_terms = tokenize(q)
    ranked = []
    for item in KNOWLEDGE:
        body_terms = tokenize(item["title"] + " " + item["content"] + " " + " ".join(item["keywords"]))
        overlap = len(q_terms & body_terms)
        if overlap:
            ranked.append((overlap / max(1, len(q_terms)), item))
    ranked.sort(key=lambda x: x[0], reverse=True)

    if not ranked or ranked[0][0] < 0.12:
        answer = "I can’t find enough support for that in my built-in notes, so I won’t guess. Please ask about PCR, DNA, or basic microbiology covered by this assistant."
        return _result(answer, "no_grounding", [], q)

    top_score = ranked[0][0]
    selected = [item for score, item in ranked if score >= max(0.12, top_score * 0.75)][:2]
    answer = "\n\n".join(f"{item['title']}: {item['content']}" for item in selected)
    return _result(answer, "answered", [item["source"] for item in selected], q)

def _result(answer, status, sources, question):
    return {
        "answer": answer,
        "status": status,
        "sources": sources,
        "input_tokens_est": estimated_tokens(question),
        "output_tokens_est": estimated_tokens(answer),
        "total_tokens_est": estimated_tokens(question) + estimated_tokens(answer),
    }

def main():
    try:
        import streamlit as st
    except ImportError:
        print("Streamlit is not installed. Run: pip install -r requirements.txt")
        return
    st.set_page_config(page_title="Grounded Bio Assistant", page_icon="🧬")
    st.title("🧬 Grounded Biotechnology Study Assistant")
    st.caption("Answers only from the small built-in notes. No external model/API is used.")
    st.info("Scope: introductory PCR, DNA, and microbiology. Off-topic or unsupported questions are refused rather than guessed.")
    question = st.text_area("Ask a biotechnology study question", placeholder="What are the main PCR cycles?")
    if st.button("Get answer"):
        result = answer_question(question)
        st.write(result["answer"])
        st.caption(f"Status: {result['status']}")
        if result["sources"]:
            st.write("Sources:", ", ".join(result["sources"]))
        st.caption(f"Estimated tokens — input: {result['input_tokens_est']}, output: {result['output_tokens_est']}, total: {result['total_tokens_est']} (rough character-based estimate, not billed usage)")
    with st.expander("Try a test question"):
        st.write("What are the main PCR cycles?")
        st.write("Who won the football match?")
        st.write("How do I make a bomb?")

if __name__ == "__main__":
    main()
