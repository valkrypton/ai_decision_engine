from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from ai_decision_engine.state import DecisionState
from ai_decision_engine.config import load_domain_config


class _Entity(BaseModel):
    key: str
    value: str


class _IntentResult(BaseModel):
    intent: str
    entities: list[_Entity]


_llm = ChatAnthropic(model="claude-haiku-4-5", max_tokens=512)
_structured_llm = _llm.with_structured_output(_IntentResult)


def input_understanding_node(state: DecisionState) -> dict:
    config = load_domain_config(state.domain)
    system = (
        f"You are an intent classifier for {config['display_name']}.\n"
        f"Valid intents: {config['intents']}\n"
        f"Entities to extract (if present): {config['entities']}\n"
        "If an entity is not mentioned, omit it."
    )
    result = _structured_llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=state.input),
    ])
    return {"intent": result.intent, "entities": {e.key: e.value for e in result.entities}}
