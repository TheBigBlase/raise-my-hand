import discord 
from discord.ext import commands 
from colorama import Fore 
import rmh_constants as c

class RaiseHand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.raised_hand_users = list() 
        self.raise_your_hand_message = None 
        self.channel = None 
        self.is_asking = False
  

    @commands.command()
    async def q(self, ctx):
        """
        Asks people to raise their hands
        """
        print(Fore.MAGENTA + "[RAISE HAND] : " + Fore.RESET + "q is called")
        #TODO access control if ctx.message.author ==
        if not self.is_asking:
            self.raise_your_hand_message = await ctx.send(c.raise_your_hand_text)
            await self.raise_your_hand_message.add_reaction(c.raised_hand_emoji)
            await ctx.message.delete()
            self.is_asking = True
        else:
            await ctx.send(c.multiple_rmh_messages_error)
   


    @commands.command()
    async def join(self, ctx):
        """
        Connects to the same channel the user is in
        """
        print(Fore.MAGENTA + "[RAISE HAND] : " + Fore.RESET + " joining channel " + Fore.GREEN + ctx.message.author.voice.channel.name + Fore.RESET + " in server  " + Fore.GREEN + ctx.message.guild.name + Fore.RESET)
        if self.channel == None:
            if type(ctx.message.author.voice) == discord.VoiceState and type(ctx.message.author.voice.channel) == discord.VoiceChannel:
                self.channel = ctx.message.author.voice.channel
                await self.channel.connect()
            else:
                await ctx.send("You're not connected to a voice channel")



    @commands.command()
    async def leave(self, ctx):
        """
        Leaves the voice channel
        """
        print(Fore.MAGENTA + "[RAISE HAND] : " + Fore.RESET + " leaving channel " + Fore.GREEN + ctx.message.author.voice.channel.name + Fore.RESET + " in server  " + Fore.GREEN + ctx.message.guild.name + Fore.RESET)
        for client in self.bot.voice_clients:
            await client.disconnect()
        self.channel = None

   

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        When a reaction is added to a message
        """
        if self.is_asking and reaction.message.id == self.raise_your_hand_message.id:
            #async for user in reaction.users():
            if user == self.bot.user:
                pass
            elif reaction.emoji == c.raised_hand_emoji:
                #Then the user has raised his hand
                if not c.raised_hand_prefix in user.display_name:
                    #Rename the user
                    try:
                        await user.edit(nick=c.raised_hand_prefix + user.display_name)
                        print(Fore.MAGENTA + "[RAISE HAND] : " + Fore.RESET + " joining channel" + Fore.GREEN + user.voice.channel.name + Fore.RESET + " in server  " + Fore.GREEN + user.guild.name + Fore.RESET)
                        #add him to the list (tuple)
                        self.raised_hand_users.append((user, user.display_name))
                    except discord.errors.Forbidden:
                        print(Fore.RED + "[RAISE HAND] : " + Fore.RESET + "Tried to rename an admin (%s)" % user.display_name)
                    for client in self.bot.voice_clients:
                        s = discord.FFmpegPCMAudio(c.sound_path, executable='ffmpeg')
                        if not client.is_playing():
                            client.play(s)
            
   

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """
        When a reation is removed from the raise your hand message
        """
        if self.is_asking and reaction.message.id == self.raise_your_hand_message.id:
            if user == self.bot.user:
                pass
            elif reaction.emoji == c.raised_hand_emoji:
                #Rename everyone who removed their reaction
                l = await reaction.users().flatten()
                new_list = list()
                for r_user in self.raised_hand_users:
                    if not r_user[0] in l:
                        #The user is in the stored list bu not in the reaction user list *sigh*
                        #Then rename him and don't add him to the new list
                        try:
                            await r_user[0].edit(nick=r_user[1])
                            print(Fore.MAGENTA + "[RAISE HAND] : " + Fore.CYAN + r_user[1] + Fore.RESET + " has been renamed")
                        except discord.errors.Forbidden:
                            print(Fore.RED + "[RAISE HAND] : " + Fore.RESET + "Tried to rename an admin (%s)" % r_user[1])
                    else:
                        #Don't rename him
                        new_list.append(r_user)
                #Modify the new list
                self.raised_hand_users = new_list



    @commands.command()
    async def e(self, ctx):
        """
        End the struggle
        """
        if self.is_asking:
            self.is_asking = False
            await ctx.message.delete()
            await self.raise_your_hand_message.delete()
            self.raise_your_hand_message = None
            for r_user in self.raised_hand_users:
                if not r_user[0] == self.bot.user:
                    try:
                        await r_user[0].edit(nick=r_user[1])
                    except discord.errors.Forbidden:
                        print(Fore.RED + "[RAISE HAND] : " + Fore.RESET + "Tried to rename an admin (%s)" % r_user[1])
            self.raised_hand_users = list()
            print(Fore.MAGENTA + "[RAISE HAND] : " + Fore.RESET + "everyone has been renamed in server " + Fore.GREEN + ctx.message.guild.name + Fore.RESET)
            
def setup(bot):
    bot.add_cog(RaiseHand(bot))
