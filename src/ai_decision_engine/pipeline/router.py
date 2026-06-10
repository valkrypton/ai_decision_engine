"""Multi-domain router: classifies user input into a registered domain."""
import json
import anthropic

_client = anthropic.Anthropic()

REGISTERED_DOMAINS = ["carddeals", "hirestream", "leadfinder", "travelplanner"]

_SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["domain", "confidence"],
    "additionalProperties": False,
}

_DOMAIN_DESCRIPTIONS = {
    "carddeals": "restaurant deals, dining discounts, food offers, card benefits for eating out",
    "hirestream": "hiring candidates, finding jobs, recruitment, career opportunities, job search",
    "leadfinder": "sales leads, company prospecting, B2B leads, ICP scoring, target accounts",
    "travelplanner": "travel plans, flights, hotels, destinations, vacations, trips, itineraries",
}


def detect_domain(user_input: str, available_domains: list[str] | None = None) -> str:
    """Return the best-matching domain for the given query.

    Falls back to 'carddeals' if confidence < 0.5.
    """
    domains = available_domains or REGISTERED_DOMAINS
    domain_list = "\n".join(
        f"- {d}: {_DOMAIN_DESCRIPTIONS.get(d, d)}" for d in domains
    )
    system = (
        "You classify user queries into the correct product domain.\n\n"
        f"Available domains:\n{domain_list}\n\n"
        "Respond with JSON only. Pick the single best domain and a confidence 0-1."
    )
    response = _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=128,
        system=system,
        messages=[{"role": "user", "content": user_input}],
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    result = json.loads(text)
    chosen = result.get("domain", "carddeals")
    if chosen not in domains:
        chosen = domains[0]
    return chosen
