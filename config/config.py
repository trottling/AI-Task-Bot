from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Токен
ADMINS = list(map(int, env.list("ADMINS")))
AI_API_KEY = env.str("AI_API_KEY")
AI_API_MODEL = env.str("AI_API_MODEL")
AI_API_URL = env.str("AI_API_URL") # ChatGPT, deepseek or local model
AI_PROXY_URL = env.str("AI_PROXY_URL")
AI_MODE= env.str("AI_MODE")

with open("./config/schema.json", mode="r", encoding="utf-8", errors="ignore") as f:
    AI_SCHEMA = f.read()

with open("./config/system_prompt.txt", mode="r", encoding="utf-8", errors="ignore") as f:
    AI_SYSTEM_PROMPT = f.read()

with open("./config/system_prompt.txt", mode="r", encoding="utf-8", errors="ignore") as f:
    AI_USER_PROMPT = f.read()