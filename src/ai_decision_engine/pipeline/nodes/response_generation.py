import anthropic
from ai_decision_engine.state import DecisionState

_client = anthropic.Anthropic()


def response_generation_node(state: DecisionState) -> dict:
    if not state.ranked:
        return {"final_response": "No results found matching your query."}

    ranked_summary = []
    for i, r in enumerate(state.ranked, 1):
        deal = r.get("best_deal", {})
        ranked_summary.append(
            f"{i}. {r['name']} ({r['cuisine'].title()}) — "
            f"{deal.get('discount_pct', 0)}% off with {deal.get('card_type', 'your card').upper()} — "
            f"Rating: {r['rating']}/5 — {r['distance_km']} km away — "
            f"Deal: {deal.get('description', '')}"
        )

    results_text = "\n".join(ranked_summary)
    prompt = (
        f"The user asked: \"{state.input}\"\n\n"
        f"Here are the top ranked results:\n{results_text}\n\n"
        "Write a concise, helpful response (2-4 sentences) recommending these options. "
        "Be specific about the best deal and why it stands out."
    )

    response = _client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(b.text for b in response.content if b.type == "text")
    return {"final_response": text}
