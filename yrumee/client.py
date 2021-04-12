from typing import Dict, List
from yrumee.modules.sora import SoraModule
from yrumee.storage import Storage
import discord

from yrumee.modules import Module
from yrumee.modules.covid19 import COVID19Module
from yrumee.modules.cute import CuteModule
from yrumee.modules.lotto import LottoModule
from yrumee.modules.mbti import MBTIModule
from yrumee.modules.nyang import NyangModule
from yrumee.modules.pingpong import PingpongModule
from yrumee.modules.reaction import ReactionModule
from yrumee.modules.stack import StackModule
from yrumee.modules.yrumee import YrumeeModule


class YrumeeClient(discord.Client):

    modules: Dict[str, List[Module]] = {}
    storage: Storage

    def new_module(self, server_id: str) -> List[Module]:
        return [
            NyangModule(self.storage.of(server_id)),
            LottoModule(self.storage.of(server_id)),
            StackModule(self.storage.of(server_id)),
            MBTIModule(self.storage.of(server_id)),
            YrumeeModule(self.storage.of(server_id)),
            COVID19Module(self.storage.of(server_id)),
            ReactionModule(self.storage.of(server_id)),
            SoraModule(self.storage.of(server_id)),
            # PingpongModule(self.storage),
            # CuteModule(self.storage),
        ]

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def get_helps(self, modules: List[Module], message: discord.Message):
        help_str = ''.join([module.__doc__ or '' for module in modules])
        await message.channel.send("여름이 🐈\n{}".format(help_str))

    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id:  # type: ignore
            return
        print("Message from {0.author}: {0.content}".format(message))

        server_id = str(message.guild.id)

        if server_id not in self.modules:
            self.modules[server_id] = self.new_module(server_id)

        if message.content.startswith("."):
            cp = message.content.split(" ", 1)
            if len(cp) == 1:
                command, payload = cp[0], ""
            else:
                command, payload = cp

            command = command.lstrip(".")
            if command == '도움말':
                await self.get_helps(self.modules[server_id], message)
            else:
                await self.on_command(command, payload, message)
        else:
            await self.on_text(message)

    async def on_command(self, command, payload, message: discord.Message):
        server_id = str(message.guild.id)

        for module in self.modules[server_id]:
            await module.on_command(command, payload, message)

    async def on_text(self, message: discord.Message):
        server_id = str(message.guild.id)

        for module in self.modules[server_id]:
            if await module.on_message(message) is True:
                break
