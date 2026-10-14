
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

    event_date = None
    event_time = None

    # Extraction du prochain jour de la semaine mentionné
    for day_name, day_number in weekdays.items():
        if re.search(rf"\b{day_name}\b", text):
            days_ahead = (day_number - today.weekday()) % 7
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

            # "Près de chez moi" ne fournit pas une localisation
            # exploitable si l'adresse n'est pas connue.
            if (
                any(
                    phrase in text
                    for phrase in (
                        "près de chez moi",
                        "pres de chez moi",
                        "à côté de chez moi",
                        "a cote de chez moi",
                    )
                )
                and result.location is None
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

    return result.needs_clarification


def classify_message(message: str) -> InboxItem:
    today = date.today()

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": f"""
You are LifeInbox, a personal message organizer.

Today's date is {today.isoformat()}.
The user's message may be in French.
Always write the summary in the same language as the user.

Choose exactly one category:
- calendar: a scheduled event with a date or time, including exams
- restaurant: restaurant recommendations or reservation requests
- study: course information or learning content without a scheduled event
- todo: an action the user needs to perform
- note: information to remember
- other: anything else

Rules:
1. Extract only facts supported by the message.
2. Resolve relative dates such as Friday or Saturday using today's date.
3. Return dates as YYYY-MM-DD.
4. Return explicit times as HH:MM, using 24-hour format.
5. Do not invent an exact time for expressions like "Saturday evening".
6. Do not invent a physical address for "near my home".
7. Set needs_clarification to true when essential information
   is missing for the intended action.
8. A task about studying is todo when the user asks to do something.
   A scheduled exam is calendar.
9. Do not treat your own confidence as a probability.
10. Return only the requested structured data.

11. For a restaurant reservation, if the user says
    "Saturday evening", resolve the date to the next Saturday,
    but leave event_time null unless an exact time is given.
12. Set needs_clarification to true if the user wants to make
    a reservation but has not specified essential details
    such as the exact time or the number of guests.
13. For a task with a deadline such as "before my exam",
    set needs_clarification to true if the exam date is unknown.
14. Set confidence to a value between 0 and 1 reflecting
    your subjective certainty. Do not always return 1.0.

Additional classification rules:

- note: use this category when the user explicitly asks to
  save or remember information, such as an address.
  Example: "Garde cette adresse : 12 rue Victor Hugo, Paris."
  -> note

- todo: use this category when there is an identifiable
  action to perform, such as buying something or reviewing
  a chapter.

- other: use this category when the message expresses only
  a vague intention or concern without an identifiable task.
  Example: "Il faut que je fasse quelque chose pour ce problème."
  -> other

Do not classify a message as todo merely because it contains
the words "il faut" or "faire quelque chose".

Clarification rules:

- Set needs_clarification to true when the user's intention is too vague to identify a concrete action or a useful piece of information to store.
- Examples:
  - "Il faut que je fasse quelque chose pour ce problème." -> needs_clarification = true
  - "Je dois m'organiser pour les examens." -> needs_clarification = true, unless a specific task or event is identified.
- Do not request clarification when the intended action is clear and the message contains enough information to process it.
- A message can belong to the "other" category and still require clarification.
Additional classification rules:

- study: use this category when the user wants to learn, understand, revise, or get an explanation of an academic or technical concept.
  Examples:
  - "Je veux comprendre la descente de gradient." -> study
  - "Explique-moi les réseaux de neurones." -> study
  - "Je dois apprendre les bases de SQL." -> study

- note: use this category when the user wants to save, remember, or keep information for later.
  Examples:
  - "Garde cette adresse : 12 rue Victor Hugo, Paris." -> note
  - "Note que mon numéro de réservation est 12345." -> note

Do not classify a message as note merely because it mentions information or a concept.

""",
            },
            {"role": "user", "content": message},
        ],
        format=InboxItem.model_json_schema(),
        options={"temperature": 0},
    )

    result = InboxItem.model_validate_json(response.message.content)

    extracted_date, extracted_time = extract_date_and_time(message)

    updates = {}

    if extracted_date is not None:
        updates["event_date"] = extracted_date

    if extracted_time is not None:
        updates["event_time"] = extracted_time

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
