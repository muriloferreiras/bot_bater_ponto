import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio


class bot_on(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
    #faz com que os botões funcionem mesmo reiniciando o bot
    async def setup_hook(self):
        self.add_view(botaoinicio())
        self.add_view(botaoparar())

client = bot_on()


@client.command()
async def ponto(ctx: commands.Context):
    emb = discord.Embed(
        title='Para iniciar o bate-ponto'
              ' clique no botão iniciar abaixo, será '
              'criado um canal com sua hora de inicio e lá'
              ' você encerrará suas horas.',
        colour=5763719    
    )
    emb.set_thumbnail(url=ctx.guild.icon)
    emb.set_footer(text=f"Atenciosamente {ctx.guild.name}")
    await ctx.channel.purge(limit=1)
    #deleta a mensagem do comando envia o embed e o botao de inicio
    await ctx.channel.send(embed=emb)
    await ctx.channel.send(view=botaoinicio())


class botaoinicio(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Iniciar', custom_id='botao', style=discord.ButtonStyle.success)
    async def botao(self, ctx: discord.Interaction, button, logs_ponto='logs_ponto'):
        current_time = datetime.now()
        username = ctx.user.nick
        start_time_str = current_time.strftime("%H:%M %d/%m")
        guild = ctx.guild
        new_channel = await guild.create_text_channel(name=f"Point-{username}-{start_time_str}")
        await new_channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await new_channel.set_permissions(ctx.user, read_messages=True)  
        #canal de logs se quiser add  
        log_channel = guild.get_channel('coloque o id do canal de logs caso queira')
        if log_channel:
            await log_channel.send(f'Ponto iniciaod de {ctx.user.mention}: {start_time_str}')
        #no novo canal a mensagem e o botão para encerrar
        await new_channel.send(f'Olá {ctx.user.mention}, suas horas estão sendo contadas clique em **Parar** para encerralas.')
        await new_channel.send(view=botaoparar())

class botaoparar(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Parar', custom_id='parar', style=discord.ButtonStyle.red)
    async def p(self, interact: discord.Interaction, button2, logs_ponto='logs_ponto',
                horas_registradas='horas_registradas'): 
        hora_fim = datetime.now()
        creation_time = interact.channel.created_at
        horario_ajustado = creation_time - timedelta(hours=3)
        #pega a hora de fim quando aperta o botao e o horario que o canal foi criado para calcular (o horario ajustado é para o fuso horario de brasilia)
        fim = hora_fim.strftime("%H:%M:%S-%d/%m")
        inicio = horario_ajustado.strftime("%H:%M:%S-%d/%m")
        try:
            await interact.channel.send(f'{interact.user.mention}, ponto encerrado em: ``{fim}``')
            guild = interact.guild
            #canal de logs se quiser add  
            log_channel = guild.get_channel('coloque o id do canal de logs caso queira')
            if log_channel:
                await log_channel.send(f'End time recorded for {interact.user.mention}: {fim}') 
            horas_registradas = guild.get_channel('canal para por as horas registradas')       
            if horas_registradas:
                horario_ajustado = datetime.strptime(inicio, "%H:%M:%S-%d/%m")
                hora_fim = datetime.strptime(fim, "%H:%M:%S-%d/%m")

                tempo_total = hora_fim - horario_ajustado
                hours, remainder = divmod(tempo_total.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
                embed=discord.Embed(
                title=f'Horas de {interact.user.name}',
                description=f'{interact.user.mention}')
                embed.add_field(name='',value=f'Hora de inicio ```{inicio}```',inline=False)
                embed.add_field(name='',value=f'Hora de fim ```{fim}```',inline=False)
                embed.add_field(name='',value=f'Tempo total ```{formatted_time}```',inline=False)
                await horas_registradas.send(embed=embed)
            else:
                await interact.channel.send('É preciso informar o canal de horas registradas para envia-las')
            await interact.channel.send(f'Suas horas serão enviadar em {horas_registradas.mention}')   
            await asyncio.sleep(8)
            await interact.channel.delete()
        except discord.NotFound:
            pass

client.run('seu token')
