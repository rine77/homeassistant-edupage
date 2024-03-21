def subject_long(subject_short):
    subject_dict = {
        "De": "Deutsch",
        "Sw": "Schwimmen",
        "Ma": "Mathematik",
        "HSK": "Heimat- und Sachkunde",
        "Mu": "Musik",
        "En": "Englisch",
        "We": "Werken",
        "Eth": "Ethik",
        "Ku": "Kunst",
        "Sp": "Sport"
        # Füge hier weitere Kürzel und ihre entsprechenden Wörter hinzu
    }

    return subject_dict.get(subject_short, "Unbekanntes Kürzel")