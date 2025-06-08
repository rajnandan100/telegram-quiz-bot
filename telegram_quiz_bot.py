import os
import json
import docx
import logging
from telegram import Bot, Poll

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DOCX_FILE = "mcqs.docx"
PROGRESS_FILE = "progress.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_questions_from_docx(docx_path):
    doc = docx.Document(docx_path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    questions = []

    i = 0
    while i < len(lines):
        if lines[i].startswith("Q") and ". " in lines[i]:
            try:
                question_text = lines[i].split(". ", 1)[1]
                options = []
                for j in range(1, 5):
                    options.append(lines[i + j].split("). ", 1)[1])
                answer_line = lines[i + 5]
                answer = answer_line.split(":")[1].strip()
                questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': answer
                })
                i += 6
            except Exception as e:
                logger.warning(f"Skipping malformed question at line {i}: {e}")
                i += 1
        else:
            i += 1
    return questions


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"offset": 0}


def save_progress(offset):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"offset": offset}, f)


def send_quiz(bot, chat_id, question, options, correct_option_id):
    bot.send_poll(
        chat_id=chat_id,
        question=question,
        options=options,
        type=Poll.QUIZ,
        correct_option_id=correct_option_id,
        is_anonymous=False
    )


def main():
    bot = Bot(token=BOT_TOKEN)
    questions = extract_questions_from_docx(DOCX_FILE)
    progress = load_progress()
    offset = progress["offset"]

    total_questions = len(questions)
    batch_size = 15
    indexes = [i for i in range(offset, total_questions) if i % 5 == offset % 5][:batch_size]

    for idx in indexes:
        q = questions[idx]
        correct_option_id = ord(q['answer'].upper()) - ord('A')
        send_quiz(bot, CHAT_ID, q['question'], q['options'], correct_option_id)

    new_offset = (offset + 1) % 5
    save_progress(new_offset)


if __name__ == "__main__":
    main()
