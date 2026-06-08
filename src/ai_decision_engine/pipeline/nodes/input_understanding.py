import json
import anthropic
from ai_decision_engine.state import DecisionState
from ai_decision_engine.config import load_domain_config

_client = anthropic.Anthropic()

_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "entities": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
    },
    "required": ["intent", "entities"],
    "additionalProperties": False,
}


def input_understanding_node(state: DecisionState) -> dict:
    config = load_domain_config(state.domain)
    intents = config["intents"]
    entities = config["entities"]

    system = (
        f"You are an intent classifier for {config['display_name']}.\n"
        f"Valid intents: {intents}\n"
        f"Entities to extract (if present): {entities}\n"
        "Respond with JSON only. If an entity is not mentioned, omit it."
    )

    response = _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": state.input}],
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
    )

    text = next(b.text for b in response.content if b.type == "text")
    result = json.loads(text)
    return {"intent": result["intent"], "entities": result["entities"]}
