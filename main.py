
from enum import Enum

import ollama
from pydantic import BaseModel, Field
import re
from datetime import date, datetime, timedelta


class Category(str, Enum):
    CALENDAR = "calendar"
    RESTAURANT = "restaurant"
    STUDY = "study"
    TODO = "todo"
    NOTE = "note"
    OTHER = "other"



class InboxItem(BaseModel):
    category: Category
    summary: str
    event_date: date | None = None
    event_time: str | None = None
    location: str | None = None
    deadline: date | None = None
    confidence: float = Field(ge=0, le=1)
    needs_clarification: bool = False



def extract_date_and_time(message: str) -> tuple[date | None, str | None]:
    today = date.today()
    text = message.lower()

    weekdays = {
        "lundi": 0,
        "mardi": 1,
        "mercredi": 2,
        "jeudi": 3,
        "vendredi": 4,
        "samedi": 5,
        "dimanche": 6,
    }

    months = {
        "janvier": 1,
        "février": 2, "fevrier": 2,
        "mars": 3,
        "avril": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "août": 8, "aout": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12, "decembre": 12,
    }

    event_date = None
    event_time = None

    # Une échéance ne doit pas être interprétée comme une date d'événement.
    deadline_intent = any(
        phrase in text
        for phrase in (
            "avant ",
            "à rendre", "a rendre",
            "rendre ",
            "remettre ",
            "déposer ", "deposer ",
            "échéance", "echeance",
            "deadline",
            "d'ici ", "d’ici ",
        )
    )

    if not deadline_intent:
        # 1. Dates relatives
        if re.search(r"\baujourd'hui\b|\baujourd’hui\b", text):
            event_date = today
        elif re.search(r"\baprès-demain\b|\bapres-demain\b", text):
            event_date = today + timedelta(days=2)
        elif re.search(r"\bdemain\b", text):
            event_date = today + timedelta(days=1)

        # 2. Dates explicites : 12/12 ou 12/12/2026
        if event_date is None:
            match = re.search(
                r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b",
                text,
            )

            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3) or today.year)

                try:
                    candidate = date(year, month, day)

                    # Sans année, une date passée est interprétée
                    # comme appartenant à l'année suivante.
                    if match.group(3) is None and candidate < today:
                        candidate = date(year + 1, month, day)

                    event_date = candidate
                except ValueError:
                    pass

        # 3. Dates en toutes lettres : 12 décembre
        if event_date is None:
            month_pattern = "|".join(
                sorted(months.keys(), key=len, reverse=True)
            )

            match = re.search(
                rf"\b(\d{{1,2}})\s+({month_pattern})"
                rf"(?:\s+(\d{{4}}))?\b",
                text,
            )

            if match:
                day = int(match.group(1))
                month = months[match.group(2)]
                year = int(match.group(3) or today.year)

                try:
                    candidate = date(year, month, day)

                    if match.group(3) is None and candidate < today:
                        candidate = date(year + 1, month, day)

                    event_date = candidate
                except ValueError:
                    pass

        # 4. Jours de la semaine
        if event_date is None:
            for day_name, day_number in weekdays.items():
                if re.search(rf"\b{day_name}\b", text):
                    days_ahead = (
                        day_number - today.weekday()
                    ) % 7

                    event_date = today + timedelta(days=days_ahead)
                    break

    # Extraction d'une heure explicite : 14 h, 14h30, 14:30
    match = re.search(
        r"\b(\d{1,2})\s*h(?:\s*(\d{2}))?\b"
        r"|\b(\d{1,2}):(\d{2})\b",
        text,
    )

    if match:
        if match.group(1) is not None:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
        else:
            hour = int(match.group(3))
            minute = int(match.group(4))

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            event_time = f"{hour:02d}:{minute:02d}"

    return event_date, event_time




def extract_deadline(message: str) -> date | None:
    """Extrait une échéance explicite, sans la confondre avec un événement."""
    text = message.lower()
    today = date.today()

    # Dates relatives simples
    if re.search(r"\bdemain\b", text):
        return today + timedelta(days=1)

    if re.search(r"\baujourd'hui\b|\baujourdhui\b", text):
        return today

    weekdays = {
        "lundi": 0,
        "mardi": 1,
        "mercredi": 2,
        "jeudi": 3,
        "vendredi": 4,
        "samedi": 5,
        "dimanche": 6,
    }

    # Indices indiquant que le jour mentionné est une échéance.
    deadline_intent = any(
        phrase in text
        for phrase in (
            "avant ",
            "à rendre",
            "a rendre",
            "rendre ",
            "remettre ",
            "déposer ",
            "deposer ",
            "échéance",
            "echeance",
            "deadline",
            "d'ici ",
        )
    )

    if deadline_intent:
        for day_name, day_number in weekdays.items():
            if re.search(rf"\b{day_name}\b", text):
                days_ahead = (day_number - today.weekday()) % 7
                return today + timedelta(days=days_ahead)

    return None



def requires_clarification(
    message: str,
    result: InboxItem,
) -> bool:
    text = message.lower()

    # Réservation : vérifier les informations essentielles
    if result.category == Category.RESTAURANT:
        reservation_intent = any(
            word in text
            for word in (
                "réserver",
                "reserver",
                "réservation",
                "reservation",
        )
        )

        if reservation_intent:
            has_party_size = bool(
                re.search(
                    r"\b(?:pour|nous sommes|on est)\s+\d+\b",
                    text,
                )
            )

            # Une réservation sans nombre de personnes
            # nécessite une clarification.
            if not has_party_size:
                return True

            # "Samedi soir" ne précise pas une heure exacte.
            if (
                result.event_date is not None
                and result.event_time is None
                and any(
                    word in text
                    for word in ("soir", "matin", "midi", "après-midi")
                )
            ):
                return True


    # Tâche liée à un contrôle/examen dont la date est inconnue
    if result.category == Category.TODO:
        mentions_exam = any(
            word in text
            for word in (
                "contrôle",
                "controle",
                "examen",
                "partiel",
                "interro",
            )
        )

        if mentions_exam and result.deadline is None:
            return True

    
    # Événements ambigus ou dont la date reste imprécise
    if result.category == Category.CALENDAR:
        if "la semaine prochaine" in text:
            return True

        if re.search(
            r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)"
            r"\s+ou\s+"
            r"(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b",
            text,
        ):
            return True
    # Tâche avec une échéance imprécise
    if result.category == Category.TODO:
        if re.search(r"\b(bientôt|prochainement|rapidement)\b", text):
            return True

    # Intention d'apprentissage trop vague
    if result.category == Category.STUDY:
        if "progresser en" in text and not any(
            word in text
            for word in ("comment", "explique", "apprendre", "réviser", "revoir")
        ):
            return True


    return result.needs_clarification


def classify_message(message: str) -> InboxItem:
    today = date.today()

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": f"""
You are LifeInbox, an intelligent personal message organizer.

Your task is to interpret a user's message, classify its primary intent, extract relevant information, and determine whether clarification is needed.

Today's date is {today.isoformat()}.
The message may be written in French or another language. Always write the summary in the same language as the user's message.

## 1. Classification

Choose exactly one category based on the user's primary intent.

- **calendar**: A scheduled event or appointment, such as a meeting, exam, trip, or interview.
- **restaurant**: Finding, recommending, remembering, or booking a restaurant.
- **study**: Requesting educational assistance, such as an explanation, a worked example, or learning material.
- **todo**: A concrete action the user intends or needs to perform.
- **note**: Information or an idea the user explicitly wants to preserve for future reference.
- **other**: Conversation, opinions, vague intentions, or messages that do not fit another category.

### Classification principles

Classify the underlying intent, not isolated words or topics. Determine what the user wants to achieve before selecting a category.

When several categories seem plausible, apply these distinctions:

- **calendar vs. todo**: Use `calendar` for the scheduled event itself and `todo` for an action to prepare for or follow up on it.
- **study vs. todo**: Use `study` when the user requests educational assistance. Use `todo` when the user intends to study independently or complete an academic task without requesting that assistance.
- **restaurant vs. todo**: Use `restaurant` when the primary intent concerns restaurant discovery, recommendations, remembered restaurants, or reservations, even when booking involves an action.
- **note vs. other**: Use `note` when preserving information is the primary intent, not merely because the message contains facts.
- **todo vs. other**: Use `todo` only when an identifiable action is expressed or clearly intended. A vague intention without an identifiable action belongs to `other`.
- **other**: Prefer this category when no more specific category captures the primary intent.

For scheduled transportation, classify a specific planned departure or arrival as `calendar`.

A restaurant-related question remains `restaurant` even when the necessary previous context is unavailable. A conversational remark, compliment, or opinion is `other` unless the user explicitly asks to preserve it.

Examples of the main distinctions:

- "Mon train part vendredi à 18h." → `calendar`
- "Pense à revoir le chapitre 3." → `todo`
- "Explique-moi les méthodes de Monte-Carlo." → `study`
- "On pourrait essayer ce restaurant." → `restaurant`
- "Mon idée : créer une application de tri de messages." → `note`
- "Il faut que je fasse quelque chose pour ce problème." → `other`

## 2. Information extraction

Extract only information explicitly stated or reliably implied by the message. Never invent missing details.

- **summary**: A concise description of the main intent or content.
- **event_date**: The date of a scheduled event, if identifiable.
- **event_time**: The explicit time of a scheduled event, formatted as `HH:MM` using the 24-hour clock.
- **location**: A location explicitly provided or reliably identifiable from the message or available context.
- **deadline**: The date by which an action must be completed, if identifiable.
- **confidence**: A subjective estimate of confidence in the overall interpretation and extraction, between 0 and 1.
- **needs_clarification**: Whether additional information is required to proceed reliably.

### Date and time rules

- Use today's date to resolve relative dates and return dates in `YYYY-MM-DD` format.
- Interpret a weekday as its next occurrence, including today when appropriate to the context.
- Resolve relative expressions such as "today" and "tomorrow" when their meaning is clear.
- Infer a missing year only when it can be determined reliably from the current date and context.
- Convert explicit times to `HH:MM` (for example, `9h30` becomes `09:30`).
- Do not invent an exact time from expressions such as "Saturday evening" or "around lunchtime".
- Distinguish event dates from deadlines according to their meaning, not simply the presence of a date.
- Do not assign a date to the wrong field. If a date or time has materially different plausible interpretations, leave the uncertain field as `null` and request clarification when necessary.

## 3. Clarification policy

Set `needs_clarification` to `true` only when missing, conflicting, ambiguous, or unavailable information materially affects the ability to fulfil the user's intent reliably.

Consider:
- What the user is trying to achieve.
- Which information is essential for the next action.
- What relevant context is genuinely available.
- The consequences of making an incorrect assumption.

Request clarification when the intended action cannot be identified, essential information is missing, conflicting details cannot be resolved, or the request depends on unavailable context.

Do not request clarification merely because a message is broad, a general goal is expressed, or optional details are missing. If the action is clear, classify it as `todo` even when its deadline is unknown.

Distinguish an actual request from a tentative idea or conversational remark. Do not assume that every suggestion implies a commitment to act.

### Restaurant-specific rules

Apply the general clarification policy to restaurant requests:

- **Discovery and recommendations**: Ask only when missing information prevents a useful recommendation. Use available, reliable context where possible.
- **Interest in a restaurant**: Do not infer a reservation request from a statement of interest.
- **Reservations**: Consider which details are essential for the requested booking, such as the restaurant, date, time, and party size. Ask when a missing detail prevents reliable progress.
- **Previous context**: If the user asks about a restaurant mentioned previously and that information is unavailable, set `needs_clarification` to `true`. Never invent the restaurant's name.

The category must remain `restaurant` when clarification is needed.

Use location or personal context only if it is genuinely available to the application. Never claim access to information that is unavailable.

## 4. Output requirements

Return only structured data matching the requested schema.

- Use `null` for unavailable optional fields.
- Ensure that categories, dates, times, and field types conform to the schema.
- Do not invent information to make the output appear complete.
- Determine `needs_clarification` independently of the selected category.
- Base `confidence` on the reliability of the overall interpretation and extraction, not merely on whether optional fields are missing.
- Write the summary in the same language as the user's message.
- Do not include explanations outside the structured output.
""",
            },
            {"role": "user", "content": message},
        ],
        format=InboxItem.model_json_schema(),
        options={"temperature": 0},
    )

    result = InboxItem.model_validate_json(response.message.content)

    
    extracted_date, extracted_time = extract_date_and_time(message)
    extracted_deadline = extract_deadline(message)

    updates = {}

    if extracted_date is not None:
        updates["event_date"] = extracted_date

    if extracted_time is not None:
        updates["event_time"] = extracted_time

    if extracted_deadline is not None:
        updates["deadline"] = extracted_deadline


    result = result.model_copy(update=updates)

    clarification_needed = requires_clarification(
        message,
        result,
    )

    return result.model_copy(
        update={"needs_clarification": clarification_needed}
    )


if __name__ == "__main__":
    message = input("Ton message : ")
    result = classify_message(message)

    print("\n--- Résultat LifeInbox ---")
    print(result.model_dump_json(indent=2))
