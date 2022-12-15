import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal, Optional
from discord.ext.commands import Greedy, Context
import openai
import time

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = Bot()

# Tree syncer
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

openai.organization = "org-ml3jQpNQbsZ9wAD3ZEeDhGX6"
openai.api_key = "openai_key"

@bot.tree.command()
async def chat(interaction: discord.Interaction, question: str):
    try:
        await interaction.response.send_message("Wait a bit as I request the response from ChatGPT! After that it will be 10 seconds before you can make another request in order to avoid my API key blowing up. If you'd like to use your own api key, use the code over at https://github.com/DuhonDoesCode/ChatGPT-Discord-Bot ", ephemeral=True)
        completion = openai.Completion.create(
            engine="text-davinci-002",
            prompt=question,
            max_tokens=1024,
            temperature=0.5,
        )
        time.sleep(10)
        await interaction.followup.send(completion.choices[0].text)
        time.sleep(9)
    except:
        await interaction.followup.send("My API key is overloaded (probably), try again later!")
        
    

bot.run('bot_key')
