"""Seed bait modules from the persona directories in scammer_soundboard/.

Each persona directory becomes a module: top-level .wav files become
ordered script steps, and early_question_responses/tier_N/ files become
tiered fillers. For Walter Nelson, the step order and expected durations
are carried over from the legacy voice_search_baiter.py script so the
seeded module is a faithful, editable version of the original.
"""

import re
from pathlib import Path

from sqlalchemy import select

from ..config import settings
from ..database import async_session
from ..models import BaitModule, ModuleClip

# (filename, expected_duration) in call order, from voice_search_baiter.py.
WALTER_SCRIPT: list[tuple[str, float]] = [
    ("Oh, that sounds fantastic! I had no idea this was an option..wav", 37.5),
    ("Wow, only two I’m lucky you called!.wav", 15),
    ("Sure thing, what do you need to know.wav", 7.5),
    ("Yes, that's perfect. That's exactly how it should be..wav", 10),
    ("Yep, that's me. Ready to make any decisions needed!.wav", 5),
    ("It's Walter Nelson. N as in Pneumonia..wav", 5),
    ("Absolutely, that's the best one for customers to reach me at..wav", 10),
    ("Just city and state.wav", 10),
    ("1670 Goldcliff Circle.wav", 12.5),
    ("Sure, it’s walter nelson at gmail.com..wav", 7.5),
    (
        "Definitely, that’s amazing to hear. I can’t believe that many "
        "searches! Yes, it’s making sense..wav",
        30,
    ),
    ("Hmm, not sure what other keywords. whatever you recommend.wav", 15),
    (
        "Oh yes, I know them. They're the big names around here. I’ve always "
        "wanted to get ahead of them somehow..wav",
        25,
    ),
    (
        "Well, I'd say 10 miles is good. That’s where most of my customers "
        "come from anyway..wav",
        15,
    ),
    (
        "I see, it’s all about getting in the door, huh Ok then, let's go "
        "ahead and get that application in. What do we do next.wav",
        50,
    ),
    (
        "No, I haven't put in any application before. This is the first time I'm "
        "hearing about this opportunity. Let's make sure it gets done right!.wav",
        50,
    ),
    (
        "That sounds great! I’m looking forward to seeing how it all comes "
        "together. Just let me know when the appointment is scheduled..wav",
        50,
    ),
    (
        "Oh, that's wonderful news! And the price is really reasonable, "
        "especially with the discount.wav",
        50,
    ),
    ("That's a great price! And no contract Even better..wav", 10),
]

WALTER_DESCRIPTION = (
    "Google-listing scam bait persona, migrated from the legacy "
    "voice_search_baiter.py script. Script steps play in order; fillers "
    "cover off-script questions (tier 1 quick acks, tier 2 deference, "
    "tier 3 stalling stories)."
)

_TIER_RE = re.compile(r"tier[_ ]?(\d+)", re.IGNORECASE)


def _script_order(persona: str, persona_dir: Path) -> list[tuple[Path, float | None]]:
    """Top-level wavs in call order: known script order first, extras after."""
    known: list[tuple[str, float]] = (
        WALTER_SCRIPT if persona == "Walter Nelson" else []
    )
    ordered: list[tuple[Path, float | None]] = []
    seen: set[str] = set()

    for filename, duration in known:
        path = persona_dir / filename
        if path.exists():
            ordered.append((path, duration))
            seen.add(filename)

    for wav in sorted(persona_dir.glob("*.wav")):
        if wav.name not in seen:
            ordered.append((wav, None))

    return ordered


async def seed_modules() -> None:
    soundboard_dir = Path(settings.soundboard_dir)
    if not soundboard_dir.exists():
        return

    async with async_session() as session:
        existing = await session.execute(select(BaitModule.id).limit(1))
        if existing.scalar() is not None:
            return

        for persona_dir in sorted(soundboard_dir.iterdir()):
            if not persona_dir.is_dir():
                continue
            persona = persona_dir.name

            module = BaitModule(
                name=persona,
                description=(
                    WALTER_DESCRIPTION if persona == "Walter Nelson" else None
                ),
            )
            session.add(module)
            await session.flush()

            for position, (wav, duration) in enumerate(
                _script_order(persona, persona_dir)
            ):
                session.add(
                    ModuleClip(
                        module_id=module.id,
                        kind="script",
                        label=wav.stem,
                        file_path=f"/soundboard-files/{persona}/{wav.name}",
                        expected_duration=duration,
                        position=position,
                    )
                )

            early_dir = persona_dir / "early_question_responses"
            if early_dir.exists():
                for tier_dir in sorted(early_dir.iterdir()):
                    if not tier_dir.is_dir():
                        continue
                    match = _TIER_RE.search(tier_dir.name)
                    if not match:
                        continue
                    tier = int(match.group(1))
                    for position, wav in enumerate(sorted(tier_dir.glob("*.wav"))):
                        session.add(
                            ModuleClip(
                                module_id=module.id,
                                kind="filler",
                                label=wav.stem,
                                file_path=(
                                    f"/soundboard-files/{persona}/"
                                    f"early_question_responses/"
                                    f"{tier_dir.name}/{wav.name}"
                                ),
                                tier=tier,
                                position=position,
                            )
                        )

        await session.commit()
