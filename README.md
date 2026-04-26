# Wino-Logic Infrastructure Pipeline

A scalable, reliable, and intelligent AI-Agent pipeline designed to detect, explain, and remediate infrastructure anomalies. Built for the SentnelOps assessment.

## How to Run the Project (Test Guide for Reviewers)

### 1. Prerequisites
Ensure you have Python 3.9+ installed. Clone or extract the project directory.

### 2. Environment Setup
It is recommended to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Provide Groq API Key
This project uses **Llama-3.1-8b-instant** on Groq for ultra-low latency inference, fully bridging OpenAI SDK compatibility.
Export your API key:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```
*(Note: If no API key is provided, the system gracefully falls back to a purely deterministic Mock-LLM mode.)*

### 4. Execute the Pipeline
Run the testing harness, which will automatically evaluate 5 diverse infrastructure inputs:
```bash
python test_wino_logic.py
```
This will print out the JSON pipeline results to your terminal and generate a `sample_outputs.json` file.

---

## Approach Chosen
I developed the **"Wino-Logic 3-Stage Pipeline"**. Instead of forcing all data through an expensive and slow LLM directly, the system operates in three isolated layers:
1. **Data Ingestion Layer**: Safely unmarshals JSON metrics. Handles absent or ambiguous keys gracefully without hard-crashing.
2. **Heuristic Engine (The Gatekeeper)**: Fast, traditional Python rules (e.g. CPU > 90% \& Network > 50%) compute a predictable `0.0` to `1.0` confidence score over the raw telemetry. 
3. **Reasoning Layer (LLM)**: Analyzes *only* the telemetry flagged as anomalous by the Heuristic Engine.

## Why This Approach?
- **Speed & Cost Control**: In a fleet of 10,000 servers, 9,500 are normally healthy. Evaluating all 10k via an LLM API would incur excessive latency and API cost. By placing a heuristic rule-engine in front, the LLM is completely bypassed (Fast-path execution) for healthy nodes (Score: `0.0`).
- **Explainability**: By restricting the LLM to only returning a `"reason"` and a `"suggested_action"`, and keeping the actual risk score computation deterministic via rules, we maintain perfect Explainability. We know *exactly why* a node got scored 0.78, but we let the AI generate the human-readable remediation steps.

## Handling Ambiguity & Imperfect Signals
Real-world infrastructure data is rarely clean (telemetry agents drop packets, some features get updated).
- **Graceful Defaults**: The system uses `.get("feature", 0.0)` for all metrics. If an entire section of telemetry is missing (e.g. Test Scenario #5: "i-ghost-node"), it defaults to a healthy baseline baseline instead of throwing a `KeyError`.
- **Fault-Tolerant LLM Integration**: The API integrations are wrapped in tight `try-except` blocks. If the Groq API throws a 429 Rate Limit error or a network interruption occurs, the code falls back to deterministic rule-based messages so the downstream systems (dashboards/alerts) don't break. 

## Tradeoffs
1. **Maintenance of Static Rules**: Currently, the heuristic logic (`cpu_avg < 5.0 && memory > 60.0`) is hard-coded. These thresholds can become stale.
2. **Loss of "Latent" AI Discovery**: Because the heuristic engine is a strict gatekeeper, if an anomaly exists that falls entirely outside the pre-programmed mathematical thresholds, the LLM will not see it, limiting purely generative "Zero-Day" anomaly discovery.

## What I Would Improve With More Time
1. **Rule Engine Dynamism**: Connect the heuristic engine's thresholds to standard deviation metrics or dynamic historical baselines (e.g., Anomaly detection via Z-Score calculation instead of static `> 90%` caps).
2. **Small Language Models (SLMs)**: Instead of routing context out to Groq/OpenAI, host an on-device quantization model locally using `vLLM` to bring costs strictly down to zero and entirely resolve data privacy/compliance issues.
3. **Continuous Actions Integration**: Expand the `suggested_action` JSON output to include a verifiable, executable Python/Terraform automation script that could be verified and executed by an automated remediation agent.

## Bonus Comparisons: Rule-Based vs ML vs LLM
- **Pure Rule-Based**: The fastest and cheapest. Zero hallucination. However, terrible context awareness (cannot provide plain English explanations of cross-service impact to junior engineers).
- **Machine Learning (Isolation Forests / XGBoost)**: Excellent for dynamic zero-day anomaly detection. But fundamentally a "Black Box" that generates a boolean `[Is_Anomaly = True]` with very poor explainability on the *Why*.
- **LLM/Generative AI**: Superb for contextual reasoning, identifying nuanced security footprints, and remediation drafting. But slow, incredibly expensive, non-deterministic, and prone to formatting hallucinations.
- **The Wino-Logic Approach (Hybrid)**: Extracts the determinism and speed from Rule-Based filtering with the reasoning and articulation strengths of an LLM.
