import sys
sys.dont_write_bytecode = True

from bot import TOKEN, bot

from main.tickets import *
from main.utils import *
from main.utils.banner import *

bot.run(TOKEN)