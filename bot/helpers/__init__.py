# DO NOT DELETE the imports, as they're used to initialize the discord client
# and would give 'run command not found' error when running grace
# Main purpose is to streamline/simplify importing of the logging functions
# that are separated into multiple modules
from bot.helpers.error_helper import *
from bot.helpers.log_helper import *
