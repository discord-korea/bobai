test_mode = False  # 테스트 여부를 입력합니다.


class bot:
    """
    정식 봇과 관련된 설정입니다.
    """

    token = ""  # 실제 봇 토큰을 입력해주세요.
    prefix = ""  # 접두사를 입력해주세요.


class tbot:
    """
    테스트 봇과 관련된 설정입니다.
    """

    token = ""  # 테스트 봇 토큰을 입력해주세요.
    prefix = ""  # 접두사를 입력해주세요.


class setting:
    """
    봇 운영과 관련된 전반적인 설정값입니다.
    """

    dev_ids = []  # 개발자의 디스코드 아이디를 입력해주세요.

    db_host_uri = ""  # 사용할 MongoDB 데이터베이스 호스트를 입력해주세요.
    db_collect_name = ""  # 사용할 MongoDB 데이터베이스 콜렉션 이름을 입력해주세요.

    koreanbots_token = ""  # 한국 디스코드 리스트 (koreanbots.dev)에서 발급받은 토큰을 입력해주세요. (없으면, 비워주세요.)
    archiver_token = ""  # Archiver (archiver.me)에서 발급받은 토큰을 입력해주세요. (없으면, 비워주세요.)
    universe_token = ""  # Universlist (universlist.kr)에서 발급받은 토큰을 입력해주세요. (없으면, 비워주세요.)
