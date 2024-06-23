import discord
from discord.ext import commands
from openai import AsyncOpenAI

# Укажите ваш Discord токен и OpenAI API ключ здесь
DISCORD_TOKEN=""
OPENAI_API_KEY=""

# Настройка намерений (intents) для бота
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Инициализация клиента Discord и асинхронного клиента OpenAI
bot = commands.Bot(command_prefix="/", intents=intents)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Глобальный словарь для хранения истории сообщений
chat_history = {}

# Функция для добавления сообщения в историю
def add_to_history(user_id, role, content):
    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append({"role": role, "content": content})

# Слеш-команда для отправки вопроса в ChatGPT
@bot.tree.command(name="вопрос", description="Отправить вопрос в ChatGPT")
async def slash_ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()  # Отложенный ответ
    user_id = interaction.user.id
    add_to_history(user_id, "user", question)

    # Формирование истории сообщений для запроса
    messages = chat_history[user_id][-10:]  # Ограничиваем историю последними 10 сообщениями

    # Отправка запроса в ChatGPT
    response = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )

    if response.choices:
        answer = response.choices[0].message.content
        add_to_history(user_id, "assistant", answer)
    else:
        answer = "Извините, не смог получить ответ."

    # Отправка окончательного ответа
    await interaction.followup.send(answer)

# Обработка ответов на сообщения бота
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.reference and message.reference.resolved:
        if message.reference.resolved.author == bot.user:
            user_id = message.author.id
            add_to_history(user_id, "user", message.content)

            messages = chat_history[user_id][-10:]

            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages
            )

            if response.choices:
                answer = response.choices[0].message.content
                add_to_history(user_id, "assistant", answer)
                await message.reply(answer)
            else:
                await message.reply("Извините, не смог получить ответ.")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    await bot.tree.sync()  # Синхронизация команд на всех серверах
    print(f"{bot.user} is ready and online!")

# Запуск бота
bot.run(DISCORD_TOKEN)
