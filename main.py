from twitchio.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import add, subtract
import json
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pydub import AudioSegment
from pydub.playback import play


#init cfg file
with open('config.json') as json_config:  
    config = json.load(json_config)

#init application for pywinauto
app = Application().connect(path='F:\SteamLibrary\steamapps\common\GRIS\GRIS.exe')
app_dialog = app.top_window()
app_dialog.maximize()
app_dialog.set_focus()
state = []

#init db
db = TinyDB('twitch.json')
Users = db.table('Users')

#dbfunctions
def User_operator (uname):
    Querydata = Users.get(Query().name == uname)
    if Querydata == None:
        Users.insert({'name': uname, 'Coins': config['Options'].get('Coins_on_follow')})
    else:
        Users.update(add('Coins', config['Options'].get('Coins_per_mes')), Query().name == uname)

#commands hell 
def Commands_operator (uname, command):
    commandobj = config['Commands'].get(command)
    if commandobj != None and Users.get(Query().name == uname).get('Coins') > commandobj.get('cost'):
        if commandobj.get('type') == 'sk':
            #SendKeys
            if 'active' in state and commandobj.get('state') == 'multiple':
                state.clear()
                key_value_up = '{{{} up}}'.format(commandobj.get('value'))
                send_keys(key_value_up)
            elif commandobj.get('state') == 'multiple':
                state.append('active')
                key_value_down = '{{{} down}}'.format(commandobj.get('value'))
                send_keys(key_value_down)
            else:
                key_value = '{{{}}}'.format(commandobj.get('value'))
                send_keys(key_value)
            Users.update(subtract('Coins', commandobj.get('cost')), Query().name == uname)
            return
        elif commandobj.get('type') == 'ws':
            #Playsound
            sound = AudioSegment.from_file('./sounds/' + commandobj.get('file')).apply_gain(commandobj.get('volume'))
            play(sound)
            Users.update(subtract('Coins', commandobj.get('cost')), Query().name == uname)
            return
    return

#MainBot
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token=config['Auth'].get('OAUTH'), client_id=config['Auth'].get('client_id'), nick=config['Auth'].get('d_name'), prefix='!',
                         initial_channels=config['Auth'].get('channel'))

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def event_message(self, message):
        User_operator(message.author.name)
        Commands_operator(message.author.name, message.content)
        await self.handle_commands(message)

    # Commands use a different decorator
    @commands.command(name='test')
    async def my_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')


bot = Bot()
bot.run()

