BLOCKED_KEYWORDS = [
    "как переделать",
    "как обойти закон",
    "как скрыть",
    "как использовать против",
    "как нанести вред",
    "самодельн",
    "модифицировать оружие",
    "переделать оружие",
]


def is_blocked_message(message: str) -> bool:
    text = message.lower()
    return any(keyword in text for keyword in BLOCKED_KEYWORDS)