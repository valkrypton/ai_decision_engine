#!/usr/bin/env python3
import argparse
import time
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="AI Decision Engine")
    parser.add_argument("--domain", required=True, choices=["carddeals"], help="Domain to query")
    parser.add_argument("--input", required=True, help="User query")
    parser.add_argument("--verbose", action="store_true", help="Show pipeline state at each step")
    args = parser.parse_args()

    from ai_decision_engine.pipeline.graph import pipeline
    from ai_decision_engine.state import DecisionState

    initial_state = DecisionState(input=args.input, domain=args.domain)

    print(f"\n[Query] {args.input}")
    print(f"[Domain] {args.domain}\n")

    start = time.perf_counter()
    final_state = pipeline.invoke(initial_state)
    elapsed = time.perf_counter() - start

    if args.verbose:
        print(f"[Intent]   {final_state['intent']}")
        print(f"[Entities] {final_state['entities']}")
        print(f"[Candidates] {len(final_state['candidates'])} found")
        print(f"[Ranked]   {len(final_state['ranked'])} results\n")

    print("=" * 60)
    print(final_state["final_response"])
    print("=" * 60)
    print(f"\n[Latency] {elapsed:.2f}s")


if __name__ == "__main__":
    main()
