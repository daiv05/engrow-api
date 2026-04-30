import json

from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.models.activity_tip import ActivityTip
from app.models.default_resource import DefaultResource
from app.models.user import User

_DEFAULT_RESOURCES = [
    ("Daily Life", "BBC Learning English", "https://www.bbc.co.uk/learningenglish", ["listening", "reading", "general"], 0),
    ("Daily Life", "VOA Learning English", "https://learningenglish.voanews.com", ["listening", "reading", "news"], 1),
    ("Daily Life", "News in Levels", "https://www.newsinlevels.com", ["reading", "news", "leveled"], 2),
    ("Daily Life", "TED Talks", "https://www.ted.com/talks", ["listening", "speaking", "ideas"], 3),
    ("Daily Life", "Merriam-Webster", "https://www.merriam-webster.com", ["vocabulary", "reference", "dictionary"], 4),
    ("Tech & Dev", "MDN Web Docs", "https://developer.mozilla.org", ["reading", "tech", "reference"], 0),
    ("Tech & Dev", "CSS-Tricks", "https://css-tricks.com", ["reading", "tech", "css"], 1),
    ("Tech & Dev", "freeCodeCamp", "https://www.freecodecamp.org", ["reading", "tech", "tutorials"], 2),
    ("Tech & Dev", "Dev.to", "https://dev.to", ["reading", "tech", "community"], 3),
    ("Tech & Dev", "Hacker News", "https://news.ycombinator.com", ["reading", "tech", "news"], 4),
    ("Podcasts", "6 Minute English (BBC)", "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english", ["listening", "podcast", "general"], 0),
    ("Podcasts", "English Learning for Curious Minds", "https://www.leonardoenglish.com/podcasts", ["listening", "podcast", "intermediate"], 1),
    ("Podcasts", "Syntax.fm", "https://syntax.fm", ["listening", "podcast", "tech"], 2),
    ("Podcasts", "The Changelog", "https://changelog.com/podcast", ["listening", "podcast", "tech"], 3),
    ("Podcasts", "The English We Speak (BBC)", "https://www.bbc.co.uk/learningenglish/english/features/the-english-we-speak", ["listening", "vocabulary", "idioms"], 4),
    ("Grammar & Reference", "Cambridge Dictionary", "https://dictionary.cambridge.org", ["vocabulary", "reference", "grammar"], 0),
    ("Grammar & Reference", "Grammarly Blog", "https://www.grammarly.com/blog", ["writing", "grammar", "tips"], 1),
    ("Grammar & Reference", "British Council Grammar", "https://www.britishcouncil.org/english/grammar", ["grammar", "exercises", "reference"], 2),
    ("Grammar & Reference", "Oxford Learner's Dictionaries", "https://www.oxfordlearnersdictionaries.com", ["vocabulary", "reference", "dictionary"], 3),
    ("YouTube", "English with Lucy", "https://www.youtube.com/@EnglishWithLucy", ["listening", "speaking", "general"], 0),
    ("YouTube", "Learn English with TV Series", "https://www.youtube.com/@LearnEnglishWithTVSeries", ["listening", "vocabulary", "entertainment"], 1),
    ("YouTube", "TED", "https://www.youtube.com/@TED", ["listening", "ideas", "education"], 2),
    ("YouTube", "Crash Course", "https://www.youtube.com/@crashcourse", ["listening", "education", "varied"], 3),
]


def seed_superadmin(db: Session) -> None:
    existing = db.query(User).filter_by(email=settings.superadmin_email).first()
    if existing:
        if not existing.is_superadmin:
            existing.is_superadmin = True
            db.commit()
        return

    superadmin = User(
        email=settings.superadmin_email,
        password_hash=hash_password(settings.superadmin_password),
        display_name="Superadmin",
        is_active=True,
        is_superadmin=True,
    )
    db.add(superadmin)
    db.commit()


def seed_default_resources(db: Session) -> None:
    if db.query(DefaultResource).count() > 0:
        return
    for category_name, title, url, tags, sort_order in _DEFAULT_RESOURCES:
        db.add(DefaultResource(
            category_name=category_name,
            title=title,
            url=url,
            tags_json=json.dumps(tags),
            sort_order=sort_order,
        ))
    db.commit()


_DEFAULT_ACTIVITY_TIPS = [
    (
        "Listening",
        "Play audio or video at a comfortable pace. Focus on understanding the gist first, then rewind for details. Avoid reading subtitles unless you're stuck.",
        [
            "Use English subtitles (not your native language) to reinforce spelling.",
            "Pause and repeat sentences you didn't catch - shadowing builds fluency fast.",
            "Watch the same episode twice: once for story, once for language.",
            "Note down new phrases in context, not just isolated words.",
        ],
        0,
    ),
    (
        "Reading",
        "Read continuously for the planned time without stopping to look up every word. Underline unknowns and review them afterward.",
        [
            "Read slightly above your level - discomfort is where growth happens.",
            "Read aloud occasionally to link written and spoken forms.",
            "Summarize each paragraph in your head to check comprehension.",
            "Keep a vocabulary log with the sentence you found the word in.",
        ],
        1,
    ),
    (
        "Writing",
        "Write without self-censoring for the first draft. Focus on getting ideas out, then revise for grammar and word choice.",
        [
            "Use the Writing Mode to track time and word count.",
            "Pick a specific topic or prompt rather than writing freely - constraints improve quality.",
            "Read your draft aloud to catch unnatural phrasing.",
            "Aim for variety: vary sentence length and starting words.",
        ],
        2,
    ),
    (
        "Speaking",
        "Record yourself or practice with a partner. Focus on fluency over accuracy during the session, then review for corrections.",
        [
            "Talk to yourself in English while doing daily tasks (cooking, commuting).",
            "Use conversation prompts: describe a picture, retell a story, explain a concept.",
            "Record a 2-minute monologue and listen back for filler words and hesitations.",
            "Practice answering questions out loud - timing yourself adds healthy pressure.",
        ],
        3,
    ),
    (
        "Shadowing",
        "Play a short audio clip (10-30 seconds), listen once, then repeat simultaneously with the audio, matching rhythm and intonation as closely as possible.",
        [
            "Choose native-speed content slightly above your level.",
            "Focus on sounds you struggle with - consonant clusters, weak vowels.",
            "Shadow the same clip 3-5 times before moving on.",
            "Use podcasts or news clips, not slow learner content - natural rhythm is the goal.",
        ],
        4,
    ),
    (
        "Vocabulary",
        "Use spaced repetition: review older cards first, then learn new words. Aim to encounter each word in multiple contexts, not just a definition.",
        [
            "Learn words in collocations: not just 'make' but 'make a decision', 'make progress'.",
            "Use the word in a sentence immediately after learning it.",
            "Group words thematically (work vocabulary, emotions, tech terms).",
            "Review flashcards during idle moments - short bursts beat long sessions.",
        ],
        5,
    ),
    (
        "Other",
        "Stay focused on English during this block. Define a clear goal at the start so you can evaluate your session afterward.",
        [
            "Set a specific micro-goal: 'I will finish chapter 3' or 'I will practice 10 new words'.",
            "Remove distractions - phone on silent, notifications off.",
            "Log what you did in the activity tracker afterward.",
        ],
        6,
    ),
]


def seed_activity_tips(db: Session) -> None:
    if db.query(ActivityTip).count() > 0:
        return
    for activity_type, how, tips, sort_order in _DEFAULT_ACTIVITY_TIPS:
        db.add(ActivityTip(
            activity_type=activity_type,
            how=how,
            tips_json=json.dumps(tips),
            sort_order=sort_order,
        ))
    db.commit()
