INTENTS: list[dict[str, str | list[str]]] = [
    {
        "intent_name": "recommendation",
        "intent": "Klient powinien zostać zachęcony przez agenta do polecenia biura innym",
        "examples": [
            "Czy może Pan polecić nasze biuro znajomym?",
            "W najnowszej promocji możecie Państwo zarobić pieniądze za polecenie nas innym",
            "Czy chce Pani wziąć udział w naszym programie poleceń?",
        ],
    },
    {
        "intent_name": "greeting",
        "intent": "Agent powinen się przedstawić z imienia i nazwiska a także podać nazwę firmy",
        "examples": [
            "Dzień dobry, nazywam się Karol Jaworski dzwonię z firmy Eurotax",
            "Witam z tej strony Hanna Szewczyk firma Callminer w czym mogę pomóc",
        ],
    },
    {
        "intent_name": "client_identity_confirmation",
        "intent": "Agent powinien potwierdzić tożsamość klienta",
        "examples": [
            "Czy rozmawiam z Panią Joanną?",
            "Dzień dobry czy mam przyjemność rozmawiać z Panem Grzegorzem Gibą?",
        ],
    },
]
