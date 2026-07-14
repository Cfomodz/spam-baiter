"""Reply templates: named sets of lines that can be voiced into a module.

A template line has a short label (shown in the UI), the exact text sent
to TTS, and either an expected duration (script steps) or a tier
(fillers). The built-in template is the Walter Nelson Google-listing
script, with spoken-form text (numbers written out, natural punctuation)
per the repo's voice-line formatting conventions.
"""

from dataclasses import dataclass

from ..models import BaitModule


@dataclass(frozen=True)
class TemplateLine:
    label: str
    text: str
    kind: str  # "script" | "filler"
    expected_duration: float | None = None
    tier: int | None = None


@dataclass(frozen=True)
class ReplyTemplate:
    key: str
    name: str
    description: str
    lines: tuple[TemplateLine, ...]


def _script(label: str, duration: float, text: str | None = None) -> TemplateLine:
    return TemplateLine(
        label=label,
        text=text or label,
        kind="script",
        expected_duration=duration,
    )


def _filler(label: str, tier: int, text: str | None = None) -> TemplateLine:
    return TemplateLine(label=label, text=text or label, kind="filler", tier=tier)


GOOGLE_LISTING_TEMPLATE = ReplyTemplate(
    key="google-listing",
    name="Google Listing Scam (Walter's script)",
    description=(
        "The legacy Walter Nelson call script for fake Google-listing "
        "telemarketers: 19 ordered replies plus tiered off-script fillers."
    ),
    lines=(
        _script("Oh, that sounds fantastic! I had no idea this was an option.", 37.5),
        _script(
            "Wow, only two? I'm lucky you called!",
            15,
        ),
        _script("Sure thing, what do you need to know?", 7.5),
        _script("Yes, that's perfect. That's exactly how it should be.", 10),
        _script("Yep, that's me. Ready to make any decisions needed!", 5),
        _script("It's Walter Nelson. N as in Pneumonia.", 5),
        _script("Absolutely, that's the best one for customers to reach me at.", 10),
        _script("Just city and state?", 10),
        _script(
            "1670 Goldcliff Circle",
            12.5,
            text="Sixteen Seventy Goldcliff Circle.",
        ),
        _script(
            "Sure, it's walter nelson at gmail.com.",
            7.5,
            text="Sure, it's walter nelson, at gmail dot com.",
        ),
        _script(
            "Definitely, that's amazing to hear. I can't believe that many "
            "searches! Yes, it's making sense.",
            30,
        ),
        _script("Hmm, not sure what other keywords... whatever you recommend.", 15),
        _script(
            "Oh yes, I know them. They're the big names around here. I've "
            "always wanted to get ahead of them somehow.",
            25,
        ),
        _script(
            "Well, I'd say ten miles is good. That's where most of my "
            "customers come from anyway.",
            15,
        ),
        _script(
            "I see, it's all about getting in the door, huh? Okay then, let's "
            "go ahead and get that application in. What do we do next?",
            50,
        ),
        _script(
            "No, I haven't put in any application before. This is the first "
            "time I'm hearing about this opportunity. Let's make sure it gets "
            "done right!",
            50,
        ),
        _script(
            "That sounds great! I'm looking forward to seeing how it all "
            "comes together. Just let me know when the appointment is "
            "scheduled.",
            50,
        ),
        _script(
            "Oh, that's wonderful news! And the price is really reasonable, "
            "especially with the discount.",
            50,
        ),
        _script("That's a great price! And no contract? Even better.", 10),
        # Tier 1: quick acknowledgements
        _filler("Yes.", 1),
        _filler("Okay.", 1),
        _filler("Sounds good.", 1),
        _filler("Sure thing.", 1),
        _filler("Right.", 1),
        _filler("Got it.", 1),
        _filler("Mmhmm.", 1),
        _filler("I understand.", 1),
        _filler("That works for me.", 1),
        # Tier 2: deference
        _filler("Let's go with what you think is best.", 2),
        _filler("I trust your judgment on this.", 2),
        _filler("Whatever you recommend.", 2),
        _filler("That sounds like a plan.", 2),
        _filler("You're the expert, so I'll follow your lead.", 2),
        # Tier 3: stalling stories
        _filler(
            "Funny story about business",
            3,
            text=(
                "You know, that reminds me of when I first opened the shop. "
                "My brother told me nobody would ever pay for it, and now he "
                "asks me for loans! Anyway, sorry — what were you saying?"
            ),
        ),
        _filler(
            "Story about my granddaughter",
            3,
            text=(
                "Oh, hold on — my granddaughter set this phone up for me and "
                "I still can't find half the buttons. She's seven! Sharp as a "
                "tack, that one. Okay, sorry, go ahead."
            ),
        ),
        _filler(
            "Interesting question thought",
            3,
            text=(
                "Now that's an interesting question. I was actually wondering "
                "about that myself just the other day, funny you bring it up. "
                "What do you think?"
            ),
        ),
        _filler(
            "Hold that thought",
            3,
            text=(
                "Hold that thought for just one second, someone's at the "
                "door. ... Okay, I'm back. Go ahead."
            ),
        ),
    ),
)

TEMPLATES: dict[str, ReplyTemplate] = {
    GOOGLE_LISTING_TEMPLATE.key: GOOGLE_LISTING_TEMPLATE,
}


def lines_from_module(module: BaitModule) -> list[TemplateLine]:
    """Use an existing module as a template: clip labels become TTS text."""
    lines: list[TemplateLine] = []
    for clip in sorted(module.clips, key=lambda c: (c.kind, c.tier or 0, c.position)):
        lines.append(
            TemplateLine(
                label=clip.label,
                text=clip.label,
                kind=clip.kind,
                expected_duration=clip.expected_duration,
                tier=clip.tier,
            )
        )
    return lines
