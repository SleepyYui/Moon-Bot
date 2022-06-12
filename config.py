import os
from dotenv import load_dotenv

load_dotenv()


class Emojis:
    def __init__(self):
        self.staff = '<:DiscordStaffBadge:973226542127804486>'
        self.yes = '<:Thumbsup:913382613266350091><'
        self.no = '<:Thumpsdown:913382668752805889>'
        self.loading = '<a:Discord:913382205106044938>'


class Logs:
    def __init__(self):
        self.cmds: int = 985665700100206613
        self.cmd_errs: int = 985665700100206613
        self.event_errs: int = 985665700100206613
        self.add_remove: int = 985665700100206613


class Config:
    def __init__(self):
        self.emojis = Emojis()
        self.logs = Logs()
        self.status = 'dir in die Augen'
        self.owners = [443769343138856961]
        self.client_secret = os.environ.get('CLIENT_SECRET')
        self.bot_lists = []
        self.transcript_db_channel = 985665700100206613
