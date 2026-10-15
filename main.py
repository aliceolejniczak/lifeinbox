
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

Your task is to interpret a user's message, classify its intent, extract relevant information, and determine whether clarification is needed.

Today's date is {today.isoformat()}.
The user's message may be written in French or another language. Always write the summary in the same language as the user's message.

## 1. Classification

Choose exactly one category based on the message's primary intent.

- **calendar**: An event or appointment with a scheduled date or time, including meetings, interviews, exams, trips, and appointments.
- **restaurant**: A message about finding, recommending, remembering, or booking a restaurant.
- **study**: A request to learn, understand, review, or get an explanation of an academic or technical subject.
- **todo**: A concrete action the user needs to perform, such as buying something, submitting a document, or completing an assignment.
- **note**: Information or an idea the user wants to preserve for future reference.
- **other**: General conversation, greetings, opinions, questions, or messages that do not fit the categories above.

### Classification principles

- Classify according to the user's primary intent, not isolated keywords.
- Identify what the user wants to achieve with the message before choosing a category.
- Choose the most specific category that captures the primary intent.
- Do not classify a message based only on the topic it mentions. A message about an exam, course, appointment, or restaurant does not automatically belong to the corresponding category.
- Distinguish between an event and an action: attending a scheduled exam is a calendar event, while preparing for the exam is a todo.
- Distinguish between asking for educational assistance and expressing an intention to study independently.
- Use `note` when the user wants information or an idea to be retained. Do not classify a message as `note` merely because it contains factual information.
- Use `todo` only when there is an identifiable action the user needs or intends to perform.
- Use `other` when no more specific category captures the primary intent.

### Category precedence rules

When multiple categories seem plausible, apply these rules:

- **Restaurant takes precedence over todo** when the primary intent concerns finding, recommending, remembering, or booking a restaurant. Booking a table is still a `restaurant` intent, even though making a reservation is an action.
- **Study takes precedence over todo** when the user explicitly requests an explanation, help understanding a concept, a worked example, or educational material such as a revision sheet.
- **Todo takes precedence over study** when the user expresses an action to complete, such as reviewing a chapter, practising exercises, or submitting an assignment, without asking the assistant to provide educational assistance.
- **Calendar takes precedence over todo** when the primary intent is to record or manage a scheduled event or appointment. Use `todo` for preparatory actions related to that event.
- **Note takes precedence over other** when the primary intent is to preserve information, a reference, or an idea for future use.
- Use `todo` for identifiable actions that do not have a more specific category matching their primary intent.
- Use `other` when the message is conversational, emotional, vague, or does not express a sufficiently identifiable task, event, learning request, or piece of information to preserve.

Examples:

- "Réserve une table samedi à 19 h pour deux personnes." → `restaurant`
- "Je voudrais réserver un restaurant italien samedi soir." → `restaurant`
- "Trouve-moi un restaurant japonais près de chez moi." → `restaurant`
- "On pourrait essayer ce restaurant libanais." → `restaurant`
- "Pense à réserver mes billets de train." → `todo`
- "Pense à revoir le chapitre 3 avant mon contrôle." → `todo`
- "Explique-moi les méthodes de Monte-Carlo." → `study`
- "Fais-moi une fiche de révision sur les méthodes de Monte-Carlo." → `study`
- "Mon idée : créer une application qui trie automatiquement mes messages." → `note`
- "Mon numéro de réservation est ABC123, note-le." → `note`
- "Je ne sais pas quoi faire de ce problème." → `other`, with clarification if no useful next step can be identified.
Additional classification examples:

- "Mon train pour Lyon part vendredi à 18h42." → `calendar`
- "C'était quoi déjà le nom du restaurant que je voulais essayer ?" → `restaurant`
- "J'aime bien ta veste !" → `other`
- "Il faut que je fasse quelque chose pour ce problème." → `other`, with `needs_clarification = true`
- "Fais quelque chose pour m'aider à m'organiser." → `other`, with `needs_clarification = true`

For scheduled transportation, such as a train or flight departure, use `calendar` when the message describes a specific planned departure or arrival.

A question about a restaurant previously mentioned by the user remains in the `restaurant` category, even if the relevant previous context is unavailable. Set `needs_clarification = true` when that context is necessary to answer.

A conversational compliment, opinion, or reaction is `other` unless the user explicitly asks to preserve it.

Do not create a `todo` merely because a message contains a vague expression of intention. If the intended action cannot be identified, use `other` and request clarification when necessary.

## 2. Information extraction

Extract only information explicitly stated or reliably implied by the message. Never invent missing details.

- **summary**: A concise description of the message's main intent or content.
- **event_date**: The date of a scheduled event, if identifiable.
- **event_time**: The explicit time of a scheduled event, formatted as HH:MM using the 24-hour clock.
- **location**: The location explicitly provided or reliably identifiable from the message.
- **deadline**: The date by which an action must be completed, if identifiable.
- **confidence**: A subjective estimate of confidence in the overall interpretation, between 0 and 1. Use lower values when the intent or extracted information is uncertain.
- **needs_clarification**: Whether additional information is needed, according to the policy below.

### Date and time rules

- Today's date is provided above. Use it to resolve relative dates.
- Return dates in YYYY-MM-DD format.
- Interpret weekdays as the next occurrence of that weekday, including today if it is the named weekday and the context does not imply otherwise.
- Resolve relative expressions such as "today" and "tomorrow" when their meaning is clear.
- Distinguish event dates from deadlines. A date associated with an appointment, meeting, or exam belongs in `event_date`. A date by which a task must be completed belongs in `deadline`.
- Do not assign a deadline to an event date, or an event date to a deadline, without evidence.
- If the message gives a date but no year, infer the year only when it can be determined reliably from the current date and context.
- Convert explicit times to HH:MM. For example, "9h30" becomes "09:30".
- Do not invent an exact time from expressions such as "Saturday evening", "in the morning", or "around lunchtime".
- If a date or time is ambiguous, do not silently choose between materially different interpretations.
- Do not confuse a deadline with an event date merely because both are associated with a date.

## 3. Clarification policy

Set `needs_clarification` to `true` when the message cannot be processed reliably without additional information.

Consider the user's intent, the information already available, and the consequences of making an incorrect assumption.

Clarification is appropriate when:

- The intended action or meaning is too vague to identify a useful next step.
- Essential information is missing to fulfil the user's explicit request.
- The message contains conflicting or materially ambiguous dates, times, or other details.
- The message depends on contextual information that is unavailable.

Clarification must be based on missing information that materially affects the next action.

Ask for clarification when:

- The intended action cannot be identified reliably.
- Essential information required to fulfil an explicit request is missing.
- The user provides conflicting information that cannot be resolved reliably.
- The user refers to information from previous conversations or personal context that is unavailable.

Do not ask for clarification merely because a message is broad, expresses a general goal, or omits optional details. Create a `todo` when the action is clear, even if its deadline is not yet known.

Distinguish an explicit request to perform an action from a suggestion, a tentative idea, or a conversational remark. Do not assume that every idea implies a commitment to act.

### Restaurant-specific clarification rules

For restaurant-related messages, distinguish between:

- **Discovering restaurants**: Ask for clarification only when information essential to making a useful recommendation is missing. Do not ask unnecessary questions when a reasonable recommendation can already be made.
- **Expressing interest in trying a restaurant**: Do not assume that a reservation is being requested. Do not ask for booking details unless the user expresses an intention to book.
- **Making an actual reservation**: Identify which essential booking details are missing before asking for them. Depending on the request, these may include the restaurant, date, time, or party size.
- **Remembering a restaurant**: If the user asks about a restaurant mentioned in a previous conversation and that context is unavailable, set `needs_clarification` to `true`. Do not invent the restaurant's name.

A restaurant message must remain in the `restaurant` category even when clarification is needed.

If the application can reliably access the user's location or previously stored information, use that context instead of asking the user to repeat it. Do not claim to have access to context that is not actually available.

## 4. Output requirements

- Return only the structured data matching the requested schema.
- Use `null` for unavailable optional fields.
- Do not include explanations outside the structured output.
- Ensure that dates, times, categories, and field types conform to the schema.
- Do not invent information to make the output appear complete.
- Set `needs_clarification` based on the clarification policy, independently of the selected category.
- Set `confidence` according to the reliability of the overall interpretation and extraction, not merely the presence or absence of missing optional fields.

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
