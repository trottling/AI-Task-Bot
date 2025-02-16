from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Токен
ADMINS = list(map(int, env.list("ADMINS")))
