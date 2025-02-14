# -*- coding: utf-8 -*-
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021 davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import mock
import pytest

from hikari import channels
from hikari import snowflakes
from hikari import traits
from hikari import undefined
from hikari.interactions import bases
from hikari.interactions import commands


@pytest.fixture()
def mock_app():
    return mock.Mock(traits.CacheAware, rest=mock.AsyncMock())


class TestCommand:
    @pytest.fixture()
    def mock_command(self, mock_app):
        return commands.Command(
            app=mock_app,
            id=snowflakes.Snowflake(34123123),
            application_id=snowflakes.Snowflake(65234123),
            name="Name",
            description="very descript",
            options=[],
            guild_id=snowflakes.Snowflake(31231235),
        )

    @pytest.mark.asyncio()
    async def test_fetch_self(self, mock_command, mock_app):
        result = await mock_command.fetch_self()

        assert result is mock_app.rest.fetch_application_command.return_value
        mock_app.rest.fetch_application_command.assert_awaited_once_with(65234123, 34123123, 31231235)

    @pytest.mark.asyncio()
    async def test_fetch_self_when_guild_id_is_none(self, mock_command, mock_app):
        mock_command.guild_id = None

        result = await mock_command.fetch_self()

        assert result is mock_app.rest.fetch_application_command.return_value
        mock_app.rest.fetch_application_command.assert_awaited_once_with(65234123, 34123123, undefined.UNDEFINED)

    @pytest.mark.asyncio()
    async def test_edit_without_optional_args(self, mock_command, mock_app):
        result = await mock_command.edit()

        assert result is mock_app.rest.edit_application_command.return_value
        mock_app.rest.edit_application_command.assert_awaited_once_with(
            65234123,
            34123123,
            31231235,
            name=undefined.UNDEFINED,
            description=undefined.UNDEFINED,
            options=undefined.UNDEFINED,
        )

    @pytest.mark.asyncio()
    async def test_edit_with_optional_args(self, mock_command, mock_app):
        mock_option = object()
        result = await mock_command.edit(name="new name", description="very descrypt", options=[mock_option])

        assert result is mock_app.rest.edit_application_command.return_value
        mock_app.rest.edit_application_command.assert_awaited_once_with(
            65234123, 34123123, 31231235, name="new name", description="very descrypt", options=[mock_option]
        )

    @pytest.mark.asyncio()
    async def test_edit_when_guild_id_is_none(self, mock_command, mock_app):
        mock_command.guild_id = None

        result = await mock_command.edit()

        assert result is mock_app.rest.edit_application_command.return_value
        mock_app.rest.edit_application_command.assert_awaited_once_with(
            65234123,
            34123123,
            undefined.UNDEFINED,
            name=undefined.UNDEFINED,
            description=undefined.UNDEFINED,
            options=undefined.UNDEFINED,
        )

    @pytest.mark.asyncio()
    async def test_delete(self, mock_command, mock_app):
        await mock_command.delete()

        mock_app.rest.delete_application_command.assert_awaited_once_with(65234123, 34123123, 31231235)

    @pytest.mark.asyncio()
    async def test_delete_when_guild_id_is_none(self, mock_command, mock_app):
        mock_command.guild_id = None

        await mock_command.delete()

        mock_app.rest.delete_application_command.assert_awaited_once_with(65234123, 34123123, undefined.UNDEFINED)


class TestCommandInteraction:
    @pytest.fixture()
    def mock_command_interaction(self, mock_app):
        return commands.CommandInteraction(
            app=mock_app,
            id=snowflakes.Snowflake(2312312),
            type=bases.InteractionType.APPLICATION_COMMAND,
            channel_id=snowflakes.Snowflake(3123123),
            guild_id=snowflakes.Snowflake(5412231),
            member=object(),
            user=object(),
            token="httptptptptptptptp",
            version=1,
            application_id=snowflakes.Snowflake(43123),
            command_id=snowflakes.Snowflake(3123123),
            command_name="OKOKOK",
            options=[],
            resolved=None,
        )

    def test_build_response(self, mock_command_interaction, mock_app):
        mock_app.rest.interaction_message_builder = mock.Mock()
        builder = mock_command_interaction.build_response()

        assert builder is mock_app.rest.interaction_message_builder.return_value
        mock_app.rest.interaction_message_builder.assert_called_once_with(bases.ResponseType.MESSAGE_CREATE)

    def test_build_deferred_response(self, mock_command_interaction, mock_app):
        mock_app.rest.interaction_deferred_builder = mock.Mock()
        builder = mock_command_interaction.build_deferred_response()

        assert builder is mock_app.rest.interaction_deferred_builder.return_value
        mock_app.rest.interaction_deferred_builder.assert_called_once_with(bases.ResponseType.DEFERRED_MESSAGE_CREATE)

    @pytest.mark.asyncio()
    async def test_fetch_channel(self, mock_command_interaction, mock_app):
        mock_app.rest.fetch_channel.return_value = mock.Mock(channels.TextChannel)
        assert await mock_command_interaction.fetch_channel() is mock_app.rest.fetch_channel.return_value

        mock_app.rest.fetch_channel.assert_awaited_once_with(3123123)

    def test_get_channel(self, mock_command_interaction, mock_app):
        mock_app.cache.get_guild_channel.return_value = mock.Mock(channels.GuildTextChannel)

        assert mock_command_interaction.get_channel() is mock_app.cache.get_guild_channel.return_value

        mock_app.cache.get_guild_channel.assert_called_once_with(3123123)

    def test_get_channel_without_cache(self, mock_command_interaction):
        mock_command_interaction.app = mock.Mock(traits.RESTAware)

        assert mock_command_interaction.get_channel() is None

    @pytest.mark.asyncio()
    async def test_fetch_command_for_guild_command(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = 342123

        assert await mock_command_interaction.fetch_command() is mock_app.rest.fetch_application_command.return_value

        mock_app.rest.fetch_application_command.assert_awaited_once_with(
            application=43123, command=2312312, guild=342123
        )

    @pytest.mark.asyncio()
    async def test_fetch_command_for_dm_command(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = None

        assert await mock_command_interaction.fetch_command() is mock_app.rest.fetch_application_command.return_value

        mock_app.rest.fetch_application_command.assert_awaited_once_with(
            application=43123, command=2312312, guild=undefined.UNDEFINED
        )

    @pytest.mark.asyncio()
    async def test_fetch_guild(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = 43123123

        assert await mock_command_interaction.fetch_guild() is mock_app.rest.fetch_guild.return_value

        mock_app.rest.fetch_guild.assert_awaited_once_with(43123123)

    @pytest.mark.asyncio()
    async def test_fetch_guild_for_dm_interaction(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = None

        assert await mock_command_interaction.fetch_guild() is None

        mock_app.rest.fetch_guild.assert_not_called()

    def test_get_guild(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = 874356

        assert mock_command_interaction.get_guild() is mock_app.cache.get_guild.return_value

        mock_app.cache.get_guild.assert_called_once_with(874356)

    def test_get_guild_for_dm_interaction(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = None

        assert mock_command_interaction.get_guild() is None

        mock_app.cache.get_guild.assert_not_called()

    def test_get_guild_when_cacheless(self, mock_command_interaction, mock_app):
        mock_command_interaction.guild_id = 321123
        mock_command_interaction.app = mock.Mock(traits.RESTAware)

        assert mock_command_interaction.get_guild() is None

        mock_app.cache.get_guild.assert_not_called()
