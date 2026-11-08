"""Cross-topic themes for the 'By theme' view, and each dot point's primary theme.

The syllabus lists themes and challenges separately for each topic. Several recur under
the same name in more than one topic, so the map merges them into eight cross-topic
themes. Each dot point is given ONE primary theme for the view; DRAFT for teacher review.
"""

THEMES = [
    {"k": "just", "label": "Justice & competing interests",
     "full": "Law, justice and society; balancing the interests of victims, offenders and society",
     "colour": "#0F6E6E", "from": "Year 11 'law, justice & society'; Crime 'balancing victims, offenders & society'"},
    {"k": "val", "label": "Values & ethics",
     "full": "Law as a reflection of values, moral and ethical standards and changing community values",
     "colour": "#6B3FA0", "from": "Year 11 values; Crime 'moral & ethical standards'; Human Rights, Family and Shelter values"},
    {"k": "comp", "label": "Compliance & non-compliance",
     "full": "Why people comply with law, why they do not, and what happens when they do not",
     "colour": "#8A6A00", "from": "Crime, Human Rights, Family and Shelter"},
    {"k": "ref", "label": "Law reform",
     "full": "The role of law reform in achieving just outcomes",
     "colour": "#A31545", "from": "Year 11 'Changing the law'; Crime, Human Rights, Family and Shelter"},
    {"k": "eff", "label": "Legal & non-legal effectiveness",
     "full": "The effectiveness of legal and non-legal measures in achieving justice",
     "colour": "#1F3864", "from": "Every topic"},
    {"k": "coop", "label": "Cooperation & conflict resolution",
     "full": "The role of law in encouraging cooperation and resolving conflict",
     "colour": "#0E7490", "from": "Family and Shelter"},
    {"k": "disc", "label": "Discretion",
     "full": "The role of discretion in the criminal justice system",
     "colour": "#B45309", "from": "Crime"},
    {"k": "sov", "label": "State sovereignty & human rights",
     "full": "The changing relationship between state sovereignty and human rights",
     "colour": "#5B2A86", "from": "Human Rights; the global legal system in Year 11"},
]

# section default -> theme; PER_POINT overrides win
SECTION_DEFAULT = {
    "inv.1": "just", "inv.2": "val", "inv.3": "val", "inv.4": "eff", "inv.5": "just", "inv.6": "sov", "inv.7": "just",
    "dis.1": "just", "dis.2": "just", "dis.3": "eff",
    "chg.1": "val", "chg.2": "eff", "chg.3": "ref", "chg.4": "eff", "chg.5": "ref", "chg.6": "ref",
    "exp.1": "just", "exp.2": "eff", "exp.3": "eff", "exp.4": "just", "exp.5": "eff", "exp.6": "eff",
    "crime.1": "val", "crime.2": "disc", "crime.3": "just", "crime.4": "disc", "crime.5": "just", "crime.6": "sov",
    "hr.1": "val", "hr.2": "eff", "hr.3": "comp",
    "fam.1": "val", "fam.2": "coop", "fam.3": "ref",
    "shel.1": "val", "shel.2": "coop", "shel.3": "ref",
}

PER_POINT = {
    "dis.1.7": "eff", "dis.2.7": "eff", "dis.3.1": "just", "dis.3.2": "just", "dis.3.8": "just",
    "chg.1.4": "sov",
    "crime.1.2": "just", "crime.1.3": "just", "crime.1.4": "just", "crime.1.6": "just", "crime.1.7": "just",
    "crime.1.8": "comp", "crime.1.9": "comp",
    "crime.2.2": "comp", "crime.2.3": "just", "crime.2.6": "just",
    "crime.3.3": "disc", "crime.3.4": "disc", "crime.3.5": "eff", "crime.3.8": "val",
    "crime.4.2": "val", "crime.4.4": "just", "crime.4.5": "just", "crime.4.6": "eff", "crime.4.7": "eff", "crime.4.8": "just",
    "crime.5.1": "val", "crime.5.5": "eff",
    "hr.2.1": "sov", "hr.2.7": "comp", "hr.2.8": "sov", "hr.2.9": "eff", "hr.2.14": "ref",
    "fam.1.2": "coop", "fam.1.5": "comp", "fam.2.4": "comp", "fam.2.6": "eff", "fam.2.7": "eff",
    "fam.3.1": "val", "fam.3.4": "comp",
    "shel.1.3": "comp", "shel.2.3": "comp", "shel.2.8": "comp", "shel.2.9": "eff", "shel.2.10": "eff",
    "shel.3.2": "val",
}

# Short labels for chips: anything not here is cut at the first ' - ' / em dash.
SHORT = {
    "inv.1.3": "Ways to classify the law",
    "inv.2.2": "Elders and traditional dispute resolution",
    "inv.6.3": "Responsibilities of states, incl. Australia's",
    "dis.1.8": "Justice concepts in a criminal case",
    "dis.2.8": "Justice concepts in a civil case",
    "dis.3.7": "Royal commission findings",
    "dis.3.8": "Justice concepts in a dispute with the state",
    "chg.2.1": "Ways to influence change",
    "chg.6.1": "Overview of the area of law reform",
    "exp.1.3": "Issues from contact with the law",
    "exp.2.4": "Alternative approaches to justice",
    "exp.2.3": "Contact with police and the Children's Court",
    "exp.5.3": "Contact with legal processes",
    "hr.2.4": "Courts, tribunals and statutory authorities",
    "hr.2.14": "A Charter of Rights: for and against",
    "hr.3.1": "A contemporary issue",
    "shel.2.2": "Leasing: landlords' and tenants' rights",
    "fam.1.5": "Rights and obligations of parents and children",
    "crime.2.6": "Detention, interrogation and suspects' rights",
    "crime.4.3": "Factors affecting a sentencing decision",
    "fam.2.2": "Separation: consequences for children",
    "fam.2.3": "Separation: consequences for property",
}
