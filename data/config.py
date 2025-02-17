from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Токен
DEEPSEEK_KEY = env.str("DEEPSEEK_KEY")  # Токен
ADMINS = list(map(int, env.list("ADMINS")))
