# -*- coding: utf-8 -*-
# cython: language_level=3
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
"""Models and enums used for Discord's Slash Commands interaction flow."""
from __future__ import annotations

__all__: typing.List[str] = [
    "Command",
    "CommandChoice",
    "CommandInteractionOption",
    "CommandInteraction",
    "CommandOption",
    "COMMAND_RESPONSE_TYPES",
    "CommandResponseTypesT",
    "InteractionChannel",
    "ResolvedOptionData",
    "OptionType",
]

import typing

import attr

from hikari import channels
from hikari import snowflakes
from hikari import traits
from hikari import undefined
from hikari.interactions import bases
from hikari.internal import attr_extensions
from hikari.internal import enums

if typing.TYPE_CHECKING:
    from hikari import guilds
    from hikari import permissions as permissions_
    from hikari import users
    from hikari.api import special_endpoints


COMMAND_RESPONSE_TYPES: typing.Final[typing.AbstractSet[CommandResponseTypesT]] = frozenset(
    [bases.ResponseType.MESSAGE_CREATE, bases.ResponseType.DEFERRED_MESSAGE_CREATE]
)
"""Set of the response types which are valid for a command interaction.

This includes:

* `hikari.interactions.bases.ResponseType.MESSAGE_CREATE`
* `hikari.interactions.bases.ResponseType.DEFERRED_MESSAGE_CREATE`
"""

CommandResponseTypesT = typing.Union[
    typing.Literal[bases.ResponseType.MESSAGE_CREATE],
    typing.Literal[4],
    typing.Literal[bases.ResponseType.DEFERRED_MESSAGE_CREATE],
    typing.Literal[5],
]
"""Type-hint of the response types which are valid for a command interaction.

The following types are valid for this:

* `hikari.interactions.bases.ResponseType.MESSAGE_CREATE`/`4`
* `hikari.interactions.bases.ResponseType.DEFERRED_MESSAGE_CREATE`/`5`
"""


@typing.final
class OptionType(int, enums.Enum):
    """The type of a command option."""

    SUB_COMMAND = 1
    """Denotes a command option where the value will be a sub command."""

    SUB_COMMAND_GROUP = 2
    """Denotes a command option where the value will be a sub command group."""

    STRING = 3
    """Denotes a command option where the value will be a string."""

    INTEGER = 4
    """Denotes a command option where the value will be a int."""

    BOOLEAN = 5
    """Denotes a command option where the value will be a bool."""

    USER = 6
    """Denotes a command option where the value will be resolved to a user."""

    CHANNEL = 7
    """Denotes a command option where the value will be resolved to a channel."""

    ROLE = 8
    """Denotes a command option where the value will be resolved to a role."""

    MENTIONABLE = 9
    """Denotes a command option where the value will be a snowflake ID."""


@attr_extensions.with_copy
@attr.define(hash=False, kw_only=True, weakref_slot=False)
class CommandChoice:
    """Represents the choices set for an application command's argument."""

    name: str = attr.field(repr=True)
    """The choice's name (inclusively between 1-100 characters)."""

    value: typing.Union[str, int] = attr.field(repr=True)
    """Value of the choice (up to 100 characters if a string)."""


@attr_extensions.with_copy
@attr.define(hash=False, kw_only=True, weakref_slot=False)
class CommandOption:
    """Represents an application command's argument."""

    type: typing.Union[OptionType, int] = attr.field(repr=True)
    """The type of command option this is."""

    name: str = attr.field(repr=True)
    r"""The command option's name.

    !!! note
        This will match the regex `^[a-z0-9_-]{1,32}$`.
    """

    description: str = attr.field(repr=False)
    """The command option's description.

    !!! note
        This will be inclusively between 1-100 characters in length.
    """

    is_required: bool = attr.field(repr=False)
    """Whether this command """

    choices: typing.Optional[typing.Sequence[CommandChoice]] = attr.field(default=None, repr=False)
    """A sequence of up to (and including) 25 choices for this command.

    This will be `builtins.None` if the input values for this option aren't
    limited to specific values or if it's a subcommand or subcommand-group type
    option.
    """

    options: typing.Optional[typing.Sequence[CommandOption]] = attr.field(default=None, repr=False)
    """Sequence of up to (and including) 25 of the options for this command option."""


@attr_extensions.with_copy
@attr.define(hash=True, kw_only=True, weakref_slot=False)
class Command(snowflakes.Unique):
    """Represents an application command on Discord."""

    app: traits.RESTAware = attr.field(eq=False, hash=False, repr=False)
    """The client application that models may use for procedures."""

    id: snowflakes.Snowflake = attr.field(hash=True, repr=True)
    # <<inherited docstring from Unique>>.

    application_id: snowflakes.Snowflake = attr.field(eq=False, hash=False, repr=True)
    """ID of the application this command belongs to."""

    name: str = attr.field(eq=False, hash=False, repr=True)
    r"""The command's name.

    !!! note
        This will match the regex `^[a-z0-9_-]{1,32}$`.
    """

    description: str = attr.field(eq=False, hash=False, repr=False)
    """The command's description.

    !!! note
        This will be inclusively between 1-100 characters in length.
    """

    options: typing.Optional[typing.Sequence[CommandOption]] = attr.field(eq=False, hash=False, repr=False)
    """Sequence of up to (and including) 25 of the options for this command."""

    guild_id: typing.Optional[snowflakes.Snowflake] = attr.field(eq=False, hash=False, repr=False)
    """ID of the guild this command is in.

    This will be `builtins.None` if this is a global command.
    """

    async def fetch_self(self) -> Command:
        """Fetch an up-to-date version of this command object.

        Returns
        -------
        hikari.interactions.commands.Command
            Object of the fetched command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the target command.
        hikari.errors.NotFoundError
            If the command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
        return await self.app.rest.fetch_application_command(
            self.application_id, self.id, undefined.UNDEFINED if self.guild_id is None else self.guild_id
        )

    async def edit(
        self,
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        options: undefined.UndefinedOr[typing.Sequence[CommandOption]] = undefined.UNDEFINED,
    ) -> Command:
        """Edit this command.

        Other Parameters
        ----------------
        guild : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.guilds.PartialGuild]]
            Object or ID of the guild to edit a command for if this is a guild
            specific command. Leave this as `hikari.undefined.UNDEFINED` to delete
            a global command.
        name : hikari.undefined.UndefinedOr[builtins.str]
            The name to set for the command. Leave as `hikari.undefined.UNDEFINED`
            to not change.
        description : hikari.undefined.UndefinedOr[builtins.str]
            The description to set for the command. Leave as `hikari.undefined.UNDEFINED`
            to not change.
        options : hikari.undefined.UndefinedOr[typing.Sequence[hikari.interactions.commands.CommandOption]]
            A sequence of up to 10 options to set for this command. Leave this as
            `hikari.undefined.UNDEFINED` to not change.

        Returns
        -------
        hikari.interactions.commands.Command
            The edited command object.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the application's commands.
        hikari.errors.NotFoundError
            If the application or command isn't found.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
        return await self.app.rest.edit_application_command(
            self.application_id,
            self.id,
            undefined.UNDEFINED if self.guild_id is None else self.guild_id,
            name=name,
            description=description,
            options=options,
        )

    async def delete(self) -> None:
        """Delete this command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the application's commands.
        hikari.errors.NotFoundError
            If the application or command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
        await self.app.rest.delete_application_command(
            self.application_id, self.id, undefined.UNDEFINED if self.guild_id is None else self.guild_id
        )


@attr_extensions.with_copy
@attr.define(hash=True, kw_only=True, weakref_slot=False)
class InteractionChannel(channels.PartialChannel):
    """Represents partial channels returned as resolved entities on interactions."""

    permissions: permissions_.Permissions = attr.field(eq=False, hash=False, repr=True)
    """Permissions the command's executor has in this channel."""


@attr_extensions.with_copy
@attr.define(hash=False, kw_only=True, weakref_slot=False)
class ResolvedOptionData:
    """Represents the resolved objects of entities referenced in a command's options."""

    users: typing.Mapping[snowflakes.Snowflake, users.User] = attr.field(repr=False)
    """Mapping of snowflake IDs to the resolved option user objects."""

    members: typing.Mapping[snowflakes.Snowflake, bases.InteractionMember] = attr.field(repr=False)
    """Mapping of snowflake IDs to the resolved option member objects."""

    roles: typing.Mapping[snowflakes.Snowflake, guilds.Role] = attr.field(repr=False)
    """Mapping of snowflake IDs to the resolved option role objects."""

    channels: typing.Mapping[snowflakes.Snowflake, InteractionChannel] = attr.field(repr=False)
    """Mapping of snowflake iDs to the resolved option partial channel objects."""


@attr_extensions.with_copy
@attr.define(hash=False, kw_only=True, weakref_slot=False)
class CommandInteractionOption:
    """Represents the options passed for a command interaction."""

    name: str = attr.field(repr=True)
    """Name of this option."""

    type: typing.Union[OptionType, int] = attr.field(repr=True)
    """Type of this option."""

    value: typing.Optional[typing.Sequence[typing.Union[str, int, bool]]] = attr.field(repr=True)
    """Value provided for this option.

    Either `CommandInteractionOption.value` or `CommandInteractionOption.options`
    will be provided with `value` being provided when an option is provided as a
    parameter with a value and `options` being provided when an option donates a
    subcommand or group.
    """

    options: typing.Optional[typing.Sequence[CommandInteractionOption]] = attr.field(repr=True)
    """Options provided for this option.

    Either `CommandInteractionOption.value` or `CommandInteractionOption.options`
    will be provided with `value` being provided when an option is provided as a
    parameter with a value and `options` being provided when an option donates a
    subcommand or group.
    """


@attr_extensions.with_copy
@attr.define(hash=True, kw_only=True, weakref_slot=False)
class CommandInteraction(bases.MessageResponseMixin[CommandResponseTypesT]):
    """Represents a command interaction on Discord."""

    channel_id: snowflakes.Snowflake = attr.field(eq=False, hash=False, repr=True)
    """ID of the channel this command interaction event was triggered in."""

    guild_id: typing.Optional[snowflakes.Snowflake] = attr.field(eq=False, hash=False, repr=True)
    """ID of the guild this command interaction event was triggered in.

    This will be `builtins.None` for command interactions triggered in DMs.
    """

    member: typing.Optional[bases.InteractionMember] = attr.field(eq=False, hash=False, repr=True)
    """The member who triggered this command interaction.

    This will be `builtins.None` for command interactions triggered in DMs.

    !!! note
        This member object comes with the extra field `permissions` which
        contains the member's permissions in the current channel.
    """

    user: users.User = attr.field(eq=False, hash=False, repr=True)
    """The user who triggered this command interaction."""

    command_id: snowflakes.Snowflake = attr.field(eq=False, hash=False, repr=True)
    """ID of the command being invoked."""

    command_name: str = attr.field(eq=False, hash=False, repr=True)
    """Name of the command being invoked."""

    options: typing.Optional[typing.Sequence[CommandInteractionOption]] = attr.field(eq=False, hash=False, repr=True)
    """Parameter values provided by the user invoking this command."""

    resolved: typing.Optional[ResolvedOptionData] = attr.field(eq=False, hash=False, repr=False)
    """Mappings of the objects resolved for the provided command options."""

    def build_response(self) -> special_endpoints.InteractionMessageBuilder:
        """Get a message response builder for use in the REST server flow.

        !!! note
            For interactions received over the gateway
            `CommandInteraction.create_initial_response` should be used to set
            the interaction response message.

        Examples
        --------
        ```py
        async def handle_command_interaction(interaction: CommandInteraction) -> InteractionMessageBuilder:
            return (
                interaction
                .build_response()
                .add_embed(Embed(description="Hi there"))
                .set_content("Konnichiwa")
            )
        ```

        Returns
        -------
        hikari.api.special_endpoints.InteractionMessageBuilder
            Interaction message response builder object.
        """
        return self.app.rest.interaction_message_builder(bases.ResponseType.MESSAGE_CREATE)

    def build_deferred_response(self) -> special_endpoints.InteractionDeferredBuilder:
        """Get a deferred message response builder for use in the REST server flow.

        !!! note
            For interactions received over the gateway
            `CommandInteraction.create_initial_response` should be used to set
            the interaction response message.

        !!! note
            Unlike `hikari.api.special_endpoints.InteractionMessageBuilder`,
            the result of this call can be returned as is without any modifications
            being made to it.

        Returns
        -------
        hikari.api.special_endpoints.InteractionMessageBuilder
            Deferred interaction message response builder object.
        """
        return self.app.rest.interaction_deferred_builder(bases.ResponseType.DEFERRED_MESSAGE_CREATE)

    async def fetch_channel(self) -> channels.TextChannel:
        """Fetch the guild channel this was triggered in.

        Returns
        -------
        hikari.channels.TextChannel
            The requested partial channel derived object of the channel this was
            triggered in.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the `READ_MESSAGES` permission in the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
        channel = await self.app.rest.fetch_channel(self.channel_id)
        assert isinstance(channel, channels.TextChannel)
        return channel

    def get_channel(self) -> typing.Union[channels.GuildTextChannel, channels.GuildNewsChannel, None]:
        """Get the guild channel this was triggered in from the cache.

        !!! note
            This will always return `builtins.None` for interactions triggered
            in a DM channel.

        Returns
        -------
        typing.Union[hikari.channels.GuildTextChannel, hikari.channels.GuildNewsChannel, builtins.None]
            The object of the guild channel that was found in the cache or
            `builtins.None`.
        """
        if isinstance(self.app, traits.CacheAware):
            channel = self.app.cache.get_guild_channel(self.channel_id)
            assert isinstance(channel, (channels.GuildTextChannel, channels.GuildNewsChannel))
            return channel

        return None

    async def fetch_command(self) -> Command:
        """Fetch the command which triggered this interaction.

        Returns
        -------
        hikari.interactions.commands.Command
            Object of this interaction's command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the target command.
        hikari.errors.NotFoundError
            If the command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
        return await self.app.rest.fetch_application_command(
            application=self.application_id, command=self.id, guild=self.guild_id or undefined.UNDEFINED
        )

    async def fetch_guild(self) -> typing.Optional[guilds.RESTGuild]:
        """Fetch the guild this interaction happened in.

        Returns
        -------
        typing.Optional[hikari.guilds.RESTGuild]
            Object of the guild this interaction happened in or `builtins.None`
            if this occurred within a DM channel.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
        if not self.guild_id:
            return None

        return await self.app.rest.fetch_guild(self.guild_id)

    def get_guild(self) -> typing.Optional[guilds.GatewayGuild]:
        """Get the object of this interaction's guild guild from the cache.

        Returns
        -------
        typing.Optional[hikari.guilds.GatewayGuild]
            The object of the guild if found, else `builtins.None`.
        """
        if self.guild_id and isinstance(self.app, traits.CacheAware):
            return self.app.cache.get_guild(self.guild_id)

        return None
