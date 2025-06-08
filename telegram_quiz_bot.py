import os
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

def parse_mcqs_from_text(text):
    blocks = text.strip().split("\n\n")
    questions = []

    for block in blocks:
        try:
            lines = block.strip().splitlines()
            question = lines[0]
            options = [line.split("). ", 1)[1] for line in lines[1:5]]
            answer_line = lines[5]
            correct_option = answer_line.split(":")[1].strip().upper()
            correct_index = ord(correct_option) - ord('A')
            questions.append((question, options, correct_index))
        except Exception as e:
            print(f"Skipping malformed block: {e}")
            continue

    return questions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me 15 MCQs in the proper format, and I will create Telegram quizzes.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mcq_text = update.message.text
    quizzes = parse_mcqs_from_text(mcq_text)

    if not quizzes:
        await update.message.reply_text("❌ Could not parse your questions. Make sure they follow the correct format.")
        return

    for question, options, correct_index in quizzes:
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            type=Poll.QUIZ,
            correct_option_id=correct_index,
            is_anonymous=False
        )


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.run_polling()
