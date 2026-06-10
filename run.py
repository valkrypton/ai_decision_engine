#!/usr/bin/env python3
import argparse
import time
from dotenv import load_dotenv

load_dotenv()

_ALL_DOMAINS = ["carddeals", "hirestream", "leadfinder", "travelplanner", "auto"]


def main():
    parser = argparse.ArgumentParser(description="AI Decision Engine")
    parser.add_argument(
        "--domain",
        default="auto",
        choices=_ALL_DOMAINS,
        help="Domain to query. Default: auto (detect from input).",
    )
    parser.add_argument("--input", help="User query (text mode)")
    parser.add_argument("--audio", help="Path to audio file (voice mode)")
    parser.add_argument("--verbose", action="store_true", help="Show pipeline internals")
    args = parser.parse_args()

    if not args.input and not args.audio:
        parser.error("Provide --input or --audio")

    from ai_decision_engine.pipeline.graph import pipeline
    from ai_decision_engine.state import DecisionState

    user_input = args.input
    if args.audio:
        from ai_decision_engine.stt import WhisperSTTProvider
        stt = WhisperSTTProvider()
        user_input = stt.transcribe(args.audio)
        print(f"[Transcribed] {user_input}")

    domain = args.domain
    if domain == "auto":
        from ai_decision_engine.pipeline.router import detect_domain
        domain = detect_domain(user_input)
        print(f"[Auto-detected domain] {domain}")

    print(f"\n[Query]  {user_input}")
    print(f"[Domain] {domain}\n")

    initial_state = DecisionState(input=user_input, domain=domain)
    start = time.perf_counter()
    final_state = pipeline.invoke(initial_state)
    elapsed = time.perf_counter() - start

    if args.verbose:
        print(f"[Intent]     {final_state['intent']}")
        print(f"[Entities]   {final_state['entities']}")
        print(f"[Candidates] {len(final_state['candidates'])} found")
        print(f"[Ranked]     {len(final_state['ranked'])} results\n")

    print("=" * 60)
    print(final_state["final_response"])
    print("=" * 60)
    print(f"\n[Latency] {elapsed:.2f}s")


if __name__ == "__main__":
    main()
