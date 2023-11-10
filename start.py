from bot import TOKEN, bot
from main.tickets import *
from main.utils import *
from main.utils.banner import *
import sys

sys.dont_write_bytecode = True

bot.run(TOKEN)
