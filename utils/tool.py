import asyncio

import discord


class ErrorTool:
    perm_list = {
        "add_reaction": "반응 달기",
        "administrator": "관리자",
        "attach_files": "파일 첨부하기",
        "ban_members": "멤버 차단하기",
        "change_nickname": "닉네임 변경하기",
        "connect": "음성 채널 연결하기",
        "create_instant_invite": "초대 코드 만들기",
        "create_private_threads": "비공개 스레드 만들기",
        "create_public_threads": "공개 스레드 만들기",
        "deafen_members": "멤버의 헤드셋 음소거하기",
        "embed_links": "링크 첨부하기",
        "external_emojis": "외부 이모지 사용하기",
        "external_stickers": "외부 스티커 사용하기",
        "kick_members": "멤버 추방하기",
        "manage_channels": "채널 관리하기",
        "manage_emojis": "이모지 관리하기",
        "manage_emojis_and_stickers": "이모지 및 스티커 관리하기",
        "manage_events": "서버 이벤트 관리하기",
        "manage_guild": "서버 관리하기",
        "manage_messages": "메시지 관리하기",
        "manage_nicknames": "닉네임 관리하기",
        "manage_permissions": "채널 권한 관리하기",
        "manage_roles": "역할 관리하기",
        "manage_threads": "스레드 관리하기",
        "manage_webhooks": "웹후크 관리하기",
        "mention_everyone": "@everyone 맨션하기",
        "moderate_members": "멤버 중재하기",
        "move_members": "음성 채널의 멤버 이동하기",
        "mute_members": "멤버의 마이크 음소거하기",
        "priority_speaker": "우선 발언권",
        "read_message_history": "메시지 기록 보기",
        "read_messages": "채널 보기",
        "request_to_speak": "(스테이지) 발언권 요청하기",
        "send_messages": "메시지 보내기",
        "send_messages_in_threads": "스레드에 메시지 보내기",
        "send_tts_messages": "TTS 메시지 보내기",
        "speak": "말하기",
        "start_embedded_activites": "음성 채널 활동 사용하기",
        "stream": "화면 공유하기",
        "use_application_commands": "슬래시 명령어 사용하기",
        "use_external_emojis": "외부 이모지 사용하기",
        "use_external_stickers": "외부 스티커 사용하기",
        "use_slash_commands": "슬래시 명령어 사용하기",
        "use_voice_activation": "음성 감지 사용하기",
        "view_audit_log": "감사 로그 보기",
        "view_channel": "채널 보기",
        "view_guild_insights": "서버 인사이트 보기",
    }

    def check_perm(perm: list):
        return [ErrorTool.perm_list[i] for i in perm]


class CheckTool:
    async def button_check(ctx, msg):
        async def check_for_msg(inter):
            if (inter.user.id == ctx.author.id and inter.message.id == msg.id) is False:
                await inter.followup.send(
                    f"{inter.user.mention}, 이 버튼은 명령어를 사용하신 유저만 누를 수 있어요.",
                    ephemeral=True,
                )
                return

        def check(inter):
            if inter.type == discord.InteractionType.component:
                if (
                    inter.user.id == ctx.author.id and inter.message.id == msg.id
                ) is False:
                    asyncio.create_task(check_for_msg(inter))
                    return False
                else:
                    return True
            else:
                return False

        try:
            interaction_check = await ctx.bot.wait_for(
                "interaction", check=check, timeout=60.0
            )
            return interaction_check
        except asyncio.TimeoutError:
            return None
