from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")

def parse_questions(text):
    blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
    result = []

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]

        question = lines[0]
        options = []
        correct = None

        for line in lines[1:]:
            if line.startswith("*"):
                correct = len(options)
                options.append(line[1:].strip())
            else:
                options.append(line)

        if correct is None:
            raise ValueError("Kisi question me * nahi mila.")
        result.append((question, options, correct))

    return result


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "MCQ → Quiz Bot Ready!\n\n"
        "Format:\n"
        "Question line\n"
        "*Correct option\n"
        "Option 2\n"
        "Option 3\n\n"
        "(Blank line = next question)"
    )


async def handle_mcq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text

    # topics / threads ke liye
    chat_id = message.chat_id
    thread_id = message.message_thread_id  # None hoga agar normal group/chat ho

    # Agar text me * hi nahi hai to ignore
    if "*" not in text:
        return

    try:
        quizzes = parse_questions(text)
    except Exception as e:
        await message.reply_text(f"Format Error:\n{e}")
        return

    # Har question ke liye quiz poll
    for q, opts, correct in quizzes:
        kwargs = {
            "chat_id": chat_id,
            "question": q,
            "options": opts,
            "type": "quiz",
            "correct_option_id": correct,
            "is_anonymous": False,
            "explanation": "",
            "allows_multiple_answers": False,
        }
        # Agar topic/ thread ke andar message tha, to wahin poll bhejo
        if thread_id is not None:
            kwargs["message_thread_id"] = thread_id

        await context.bot.send_poll(**kwargs)

    # Original text delete
    try:
        await message.delete()
    except:
        pass

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mcq))

    print("Bot started…")
    app.run_polling()


if __name__ == "__main__":

    main()
