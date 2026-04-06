from typing import List


MOCK_FACTS: List[str] = [
    "Data-center water accounting depends on location, season, and cooling infrastructure.",
    "Token counts are a practical proxy, but not a direct physical measurement.",
    "Awareness tools help compare scenarios rather than claim exact footprints.",
    "Small efficiency changes per prompt can add up over long usage sessions.",
]


class MockAssistant:
    def generate(self, user_message: str, turn_index: int) -> str:
        cleaned = user_message.strip()
        if not cleaned:
            return "Could you share a bit more so I can help?"

        fact = MOCK_FACTS[turn_index % len(MOCK_FACTS)]
        return (
            f"Here is a quick take on your prompt: '{cleaned[:120]}'. "
            "I can help you iterate, summarize, or refine it next. "
            f"FYI: {fact}"
        )
