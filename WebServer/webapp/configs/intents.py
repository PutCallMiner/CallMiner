from typing import TypedDict


class Intent(TypedDict):
    intent_name: str
    intent_full_name: str
    intent: str
    examples: list[str]


PREDEFINED_INTENTS: list[Intent] = [
    {
        "intent_name": "recommendation",
        "intent_full_name": "Recommendation",
        "intent": "Klient powinien zostać zachęcony przez agenta do polecenia biura innym",
        "examples": [
            "Czy może Pan polecić nasze biuro znajomym?",
            "W najnowszej promocji możecie Państwo zarobić pieniądze za polecenie nas innym",
            "Czy chce Pani wziąć udział w naszym programie poleceń?",
        ],
    },
    {
        "intent_name": "greeting",
        "intent_full_name": "Greeting",
        "intent": "Agent powinen się przedstawić z imienia i nazwiska a także podać nazwę firmy",
        "examples": [
            "Dzień dobry, nazywam się Karol Jaworski dzwonię z firmy Eurotax",
            "Witam z tej strony Hanna Szewczyk firma Callminer w czym mogę pomóc",
        ],
    },
    {
        "intent_name": "client_identity_confirmation",
        "intent_full_name": "Client's identity confirmation",
        "intent": "Agent powinien potwierdzić tożsamość klienta, pytając go o imię i/lub nazwisko, aby upewnić się, że rozmawia z właściwą osobą.",
        "examples": [
            "Czy rozmawiam z Panią Joanną?",
            "Dzień dobry, czy mam przyjemność rozmawiać z Panem Andrzejem Kowalskim?",
            "Czy to Pani Agnieszka Kowalska?",
            "Czy z tej strony jest pan Karłowski?"
            "Czy dobrze rozumiem, że rozmawiam z Panem Janem Nowakiem?",
        ],
    },
    {
        "intent_name": "contact_for_questions",
        "intent_full_name": "Contact for questions",
        "intent": "Agent zachęca klienta do kontaktu w przypadku jakichkolwiek pytań",
        "examples": [
            "Jeśli ma Pan pytania, proszę dzwonić na ten numer.",
            "W razie pytań, zapraszam do kontaktu mailowego lub telefonicznego.",
            "Proszę się ze mną kontaktować, jeśli pojawią się dodatkowe pytania.",
            "W razie jakichkolwiek pytań, jestem do dyspozycji.",
            "W razie potrzeby proszę dzwonić lub pisać do nas.",
            "Jakby pojawiły się jakieś pytania, to proszę do nas dzwonić albo pisać maile.",
        ],
    },
]
