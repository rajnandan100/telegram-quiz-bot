import os
import json
from docx import Document
from telegram import Bot

# === CONFIGURATION ===
DOCX_FILE = 'mcqs.docx'   # Your .docx file name
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'
PROGRESS_FILE = 'progress.json'
QUIZ_BATCH_SIZE = 15
STEP = 5

# === TELEGRAM BOT ===
bot = Bot(token=BOT_TOKEN)

# === Load or Initialize Progress ===
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"current_group": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

# === Parse .docx File ===
def extract_questions_from_docx(path):
    doc = Document(path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    questions = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("Q"):
            question_text = lines[i].split(". ", 1)[1]
            if (i + 5) < len(lines) and lines[i + 1].startswith("Options:"):
                options = [
                    lines[i + 2].split("). ", 1)[1],
                    lines[i + 3].split("). ", 1)[1],
                    lines[i + 4].split("). ", 1)[1],
                    lines[i + 5].split("). ", 1)[1]
                ]
                if (i + 6) < len(lines) and lines[i + 6].lower().startswith("answer:"):
                    correct_letter = lines[i + 6].split(":")[1].strip().upper()
                    correct_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_letter, -1)
                    if correct_index != -1:
                        questions.append({
                            "question": question_text,
                            "options": options,
                            "correct_index": correct_index
                        })
                i += 7
            else:
                i += 1
        else:
            i += 1
    return questions

# === Create Quiz Batch as per Pattern ===
def get_quiz_batch(questions, group_no, step, batch_size):
    batch = []
    start_index = group_no
    count = 0
    index = start_index
    while count < batch_size:
        if index >= len(questions):
            break
        batch.append(questions[index])
        index += step
        count += 1
    return batch

# === Send Quizzes via Telegram ===
def send_quiz_batch(quiz_batch):
    for q in quiz_batch:
        bot.send_poll(
            chat_id=CHAT_ID,
            question=q["question"],
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct_index"],
            is_anonymous=False
        )

# === MAIN EXECUTION ===
def main():
    progress = load_progress()
    group_no = progress["current_group"]

    print(f"Using group #{group_no}...")

    questions = extract_questions_from_docx(DOCX_FILE)
    quiz_batch = get_quiz_batch(questions, group_no, STEP, QUIZ_BATCH_SIZE)

    if not quiz_batch:
        print("No more questions left in this group.")
        return

    send_quiz_batch(quiz_batch)

    # Save progress
    progress["current_group"] += 1
    save_progress(progress)
    print(f"Group {group_no} completed. Progress saved.")

if __name__ == "__main__":
    main()