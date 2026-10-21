# Grounded Biotechnology Study Assistant

A small capstone project demonstrating a bounded assistant, guardrails, an evaluation set, scored results, and token-usage measurement.

## Scope
This assistant answers introductory questions only from its built-in notes about PCR, DNA, and microbiology. It refuses known unsafe requests, declines off-topic requests, and says when the notes do not support an answer. It does not use an external LLM or API.

## Files
- `app.py` — Streamlit interface and answer/guardrail logic
- `knowledge.py` — the source notes used to ground answers
- `data/evaluation_set.json` — evaluation cases and expected behavior
- `evaluate.py` — runs tests and scores results
- `results/` — generated JSON and CSV scores

## Run locally
1. Install Python 3.10 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Run evaluation: `python evaluate.py`
4. Launch app: `streamlit run app.py`

## Evaluation
Run `python evaluate.py`. It checks expected response status and required answer phrases, then writes `results/evaluation_results.json` and `results/evaluation_results.csv`.

## Token/cost measurement
The app records a rough character-based token estimate for the user question and answer (about one token per four characters). This is only a lightweight usage proxy, not an exact tokenizer measurement. The project uses no paid LLM API, so billed model-token cost is zero.

## Limitations and decisions
This is a deliberately small demonstration. Guardrails are keyword/pattern based and can miss paraphrases or produce false positives. Retrieval uses lexical overlap rather than semantic embeddings. Do not treat it as a safety-critical system.
