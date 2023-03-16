from django.contrib.auth.management.commands.createsuperuser import Command as SuperUserCommand
from django.core.management.base import CommandParser


class Command(SuperUserCommand):
    help = "Create a superuser. Use like: `./manage.py createsuperuser First Last`"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("first_name", help="Specifies the superuser's first name.")
        parser.add_argument("last_name", help="Specifies the superuser's last name.")
        return super().add_arguments(parser)
