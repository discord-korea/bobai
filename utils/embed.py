import discord


class Embed:
    def default(title: str = None, description: str = None, **kwargs):
        embed = discord.Embed(**kwargs, color=0x5865F2)
        if not title is None:
            embed.title = title
        if not description is None:
            embed.description = description
        return embed

    def warn(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs,
            colour=discord.Colour.gold(),
            title="⚠ 경고",
            description=description,
        )
        return embed

    def perm_warn(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs,
            colour=discord.Colour.gold(),
            title="⚠ 권한 부족",
            description=description,
        )
        return embed

    def cancel(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs, color=0x5865F2, title="❌ 취소됨", description=description
        )
        return embed

    def error(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs, color=0xFF0000, title="⚠ 오류 발생", description=description
        )
        return embed

    def user_footer(embed, user):
        return embed.set_footer(
            text=user,
            icon_url=user.display_avatar,
        )
