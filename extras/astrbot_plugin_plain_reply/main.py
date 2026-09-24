import re

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star, register


def _normalize_text(text: str) -> str:
    if not text:
        return text
    # remove markdown bold/italic markers
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"_+", "", text)
    text = re.sub(r"`+", "", text)
    # remove dashes often used as separators
    text = text.replace("——", "，").replace("--", "，")
    # collapse all whitespace/newlines into single spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


@register(
    "astrbot_plugin_plain_reply",
    "local",
    "Force plain single-line replies",
    "0.1.0",
)
class Main(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        if not result or not result.chain:
            return

        plain_parts = []
        other_comps = []
        for comp in result.chain:
            if isinstance(comp, Plain):
                if comp.text:
                    plain_parts.append(comp.text)
            else:
                other_comps.append(comp)

        if not plain_parts:
            return

        merged = _normalize_text(" ".join(plain_parts))
        result.chain = [*other_comps, Plain(merged)] if other_comps else [Plain(merged)]
        logger.debug(f"[plain_reply] normalized to: {merged[:80]}")
