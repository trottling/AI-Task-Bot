from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Токен
ADMINS = list(map(int, env.list("ADMINS")))
AI_API_KEY = env.str("AI_API_KEY")
AI_API_MODEL = env.str("AI_API_MODEL")
AI_API_URL = env.str("AI_API_URL") # Chat gpt or deepseek
