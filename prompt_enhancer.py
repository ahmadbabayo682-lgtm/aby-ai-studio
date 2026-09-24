import re


_ENHANCEMENT_SUFFIX = (
    "Create a high-quality, detailed image with clear composition, natural lighting, "
    "and visually coherent elements."
)
_HAUSA_TERMS = (
    "hausa",
    "northern nigeria",
    "niger",
    "kano",
    "sokoto",
    "zaria",
    "katsina",
)
_CLOTHING_TERMS = (
    "dress",
    "clothing",
    "robe",
    "kaftan",
    "gown",
    "outfit",
)
_MALE_PERSON_TERMS = ("man", "men", "boy", "boys", "father", "fathers")
_FEMALE_PERSON_TERMS = ("woman", "women", "girl", "girls", "mother", "mothers")
_PERSON_TERMS = _MALE_PERSON_TERMS + _FEMALE_PERSON_TERMS + ("person", "people", "family")
_CAP_TERMS = ("cap", "hat", "hula", "kufi", "fez")
_ARCHITECTURE_TERMS = (
    "architecture",
    "building",
    "compound",
    "house",
    "home",
    "mosque",
    "courtyard",
)
_MARKET_TERMS = ("market", "bazaar", "stall", "trader", "vendor")
_VILLAGE_TERMS = ("village", "rural", "countryside", "settlement")
_NAMING_TERMS = ("naming ceremony", "suna ceremony", "aqiqah")
_DURBAR_TERMS = ("durbar", "horse parade", "horse riders", "mounted riders", "emir")
_TEA_TERMS = ("tea", "chai", "tea service")
_FAMILY_TERMS = ("family", "families", "household", "relatives")
_ISLAMIC_TERMS = (
    "islamic",
    "muslim",
    "mosque",
    "prayer",
    "ramadan",
)


def _contains_term(prompt: str, terms: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(term)}\b", prompt) for term in terms)


def _cultural_guidance(prompt: str) -> str:
    lowered_prompt = prompt.casefold()
    guidance = []

    if _contains_term(lowered_prompt, _HAUSA_TERMS):
        guidance.append(
            "Use a specific Hausa/Sahelian visual context from northern Nigeria or Niger, "
            "with authentic local materials, proportions, and restrained regional detail "
            "rather than a generic pan-African appearance."
        )
        has_male_person = _contains_term(lowered_prompt, _MALE_PERSON_TERMS)
        has_female_person = _contains_term(lowered_prompt, _FEMALE_PERSON_TERMS)
        if _contains_term(lowered_prompt, _PERSON_TERMS):
            guidance.append(
                "Keep the person naturally varied and realistic, with culturally appropriate "
                "styling and no caricatured ethnic features."
            )
        if has_male_person and not has_female_person:
            guidance.append(
                "For traditional Hausa clothing, show a flowing babban riga robe over matching "
                "trousers, with natural fabric drape and restrained geometric embroidery at "
                "the neckline, chest, and cuffs."
            )
        elif has_female_person:
            guidance.append(
                "For a Hausa woman, use culturally appropriate modest feminine attire such as a "
                "colorful wrapper or long dress with a matching blouse, shawl, or hijab, using "
                "rich textile patterns and natural fabric drape; do not use masculine babban riga "
                "and trouser styling unless explicitly requested."
            )
        elif _contains_term(lowered_prompt, _CLOTHING_TERMS):
            guidance.append(
                "Use culturally appropriate modest Hausa clothing with natural fabric drape, "
                "subtle geometric embroidery, and regionally plausible textile patterns."
            )
        if _contains_term(lowered_prompt, _CAP_TERMS):
            guidance.append(
                "For a Hausa cap, show a structured rounded or cylindrical hula with plausible "
                "geometric embroidery and a well-defined fit on the head."
            )

    if _contains_term(lowered_prompt, ("white", "ivory")) and _contains_term(
        lowered_prompt, _CLOTHING_TERMS
    ):
        guidance.append(
            "Render the clothing as clean white or ivory cotton with visible folds and subtle "
            "embroidery, not as an undefined white garment."
        )
    if _contains_term(lowered_prompt, ("brown", "earth brown")) and _contains_term(
        lowered_prompt, _CAP_TERMS
    ):
        guidance.append(
            "Render the cap in a warm earth-brown tone with visible woven or embroidered texture."
        )
    if _contains_term(lowered_prompt, _ARCHITECTURE_TERMS):
        guidance.append(
            "Use Sahelian Hausa architecture where appropriate: earthen adobe or mud-plaster "
            "walls, flat roofs, shaded courtyards, practical openings, and hand-finished texture."
        )
    if _contains_term(lowered_prompt, _MARKET_TERMS):
        guidance.append(
            "Use a believable northern Nigerian open-air market with shaded fabric stalls, "
            "woven baskets, locally made goods, dusty pathways, and varied modest clothing."
        )
    if _contains_term(lowered_prompt, _VILLAGE_TERMS):
        guidance.append(
            "Use a Sahelian village with earth-colored compounds, courtyards, dusty paths, "
            "woven materials, sparse greenery, and regionally plausible homes."
        )
    if _contains_term(lowered_prompt, _NAMING_TERMS):
        guidance.append(
            "For a Hausa naming ceremony or suna, show a respectful family gathering in a "
            "shaded courtyard with the newborn and parents, seated guests, woven mats, colorful "
            "textiles, modest festive clothing, and tea or serving trays where appropriate."
        )
    if _contains_term(lowered_prompt, _DURBAR_TERMS):
        guidance.append(
            "For a northern Nigerian Durbar, show a ceremonial procession of mounted horsemen in "
            "embroidered robes and turbans, decorated horses with detailed bridles, dignified "
            "riders, and spectators along a dusty parade route; keep it historical and ceremonial, "
            "not fantasy or generic equestrian imagery."
        )
    if _contains_term(lowered_prompt, _TEA_TERMS) and _contains_term(
        lowered_prompt, _FAMILY_TERMS
    ) and _contains_term(lowered_prompt, ("courtyard", "shaded", "home", "house")):
        guidance.append(
            "For a Hausa family tea scene, place relatives together on woven mats in a shaded "
            "courtyard, with small tea glasses, a metal teapot and serving tray, earthen walls, "
            "and relaxed respectful interaction."
        )
    if _contains_term(lowered_prompt, _ISLAMIC_TERMS):
        guidance.append(
            "Use a respectful Islamic setting with modest clothing, restrained geometric motifs, "
            "and a mosque courtyard, minaret, prayer mats, or ablution area only when the scene calls for them."
        )

    return " ".join(guidance)


def enhance_prompt(prompt: str) -> str:
    try:
        if not isinstance(prompt, str):
            return prompt

        normalized_prompt = prompt.strip()
        if not normalized_prompt:
            return prompt

        punctuation = "" if normalized_prompt.endswith((".", "!", "?")) else "."
        cultural_guidance = _cultural_guidance(normalized_prompt)
        guidance = " ".join(filter(None, (cultural_guidance, _ENHANCEMENT_SUFFIX)))
        return f"{normalized_prompt}{punctuation} {guidance}"
    except Exception:
        return prompt