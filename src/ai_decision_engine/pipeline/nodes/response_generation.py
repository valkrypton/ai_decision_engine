from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from ai_decision_engine.state import DecisionState

_llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=512)


def response_generation_node(state: DecisionState) -> dict:
    if not state.ranked:
        return {"final_response": "No results found matching your query."}

    results_text = _format_ranked(state.domain, state.intent, state.ranked)
    prompt = (
        f"The user asked: \"{state.input}\"\n\n"
        f"Here are the top ranked results:\n{results_text}\n\n"
        "Write a concise, helpful response (2-4 sentences) recommending these options. "
        "Be specific about the best option and why it stands out."
    )

    response = _llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": response.content}


def _format_ranked(domain: str, intent: str, ranked: list[dict]) -> str:
    if domain == "carddeals":
        return _fmt_carddeals(ranked)
    if domain == "hirestream":
        return _fmt_hirestream(intent, ranked)
    if domain == "leadfinder":
        return _fmt_leadfinder(ranked)
    if domain == "travelplanner":
        return _fmt_travelplanner(ranked)
    return "\n".join(f"{i}. {r}" for i, r in enumerate(ranked, 1))


def _fmt_carddeals(ranked: list[dict]) -> str:
    lines = []
    for i, r in enumerate(ranked, 1):
        deal = r.get("best_deal", {})
        lines.append(
            f"{i}. {r['name']} ({r['cuisine'].title()}) — "
            f"{deal.get('discount_pct', 0)}% off with {deal.get('card_type', 'your card').upper()} — "
            f"Rating: {r['rating']}/5 — {r['distance_km']} km away — "
            f"{deal.get('description', '')}"
        )
    return "\n".join(lines)


def _fmt_hirestream(intent: str, ranked: list[dict]) -> str:
    lines = []
    if intent == "find_jobs":
        for i, r in enumerate(ranked, 1):
            skills = ", ".join(r.get("required_skills", []))
            lines.append(
                f"{i}. {r['title']} at {r['company']} — {r.get('salary_range', 'N/A')} — "
                f"Required: {skills} — {r['location']} — Skill match: {r.get('skill_match', 0):.0%}"
            )
    else:
        for i, r in enumerate(ranked, 1):
            skills = ", ".join(r.get("skills", [])[:4])
            lines.append(
                f"{i}. {r['name']} — {r['role'].title()} — {r['experience_years']} yrs — "
                f"Skills: {skills} — {r['location'].title()} — "
                f"Available: {r.get('availability', 'unknown')} — Skill match: {r.get('skill_match', 0):.0%}"
            )
    return "\n".join(lines)


def _fmt_leadfinder(ranked: list[dict]) -> str:
    lines = []
    for i, r in enumerate(ranked, 1):
        lines.append(
            f"{i}. {r['name']} — {r['industry'].title()} — {r['company_size']} employees — "
            f"{r['location'].title()} — {r.get('funding_stage', 'unknown').title()} — "
            f"ICP score: {r.get('icp_score', 0):.0%} — {r.get('description', '')}"
        )
    return "\n".join(lines)


def _fmt_travelplanner(ranked: list[dict]) -> str:
    lines = []
    for i, r in enumerate(ranked, 1):
        tags = ", ".join(r.get("tags", [])[:3])
        lines.append(
            f"{i}. {r['name']}, {r['country']} — "
            f"Est. cost: ${r.get('total_estimated_cost_usd', 0):,.0f} — "
            f"Flight: ${r['flight_price_usd']} — Hotel: ${r['hotel_per_night_usd']}/night — "
            f"Rating: {r['rating']}/5 — Best for: {tags}"
        )
    return "\n".join(lines)
