# simulacao/management/commands/clearsessions.py
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone


class Command(BaseCommand):
    help = 'Limpa sessões expiradas do banco de dados'

    def handle(self, *args, **options):
        # Conta sessões antes
        total_before = Session.objects.count()
        expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
        
        # Remove sessões expiradas
        Session.objects.filter(expire_date__lt=timezone.now()).delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Limpeza concluída!\n'
                f'Sessões expiradas removidas: {expired_count}\n'
                f'Sessões ativas restantes: {total_before - expired_count}'
            )
        )
