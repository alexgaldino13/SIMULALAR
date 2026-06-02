import os
import django
from datetime import timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCalc.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from simulacao.subscription_models import SubscriptionPlan, Subscription

User = get_user_model()

print("=== USUÁRIOS ===")
for u in User.objects.all():
    tc = getattr(u, 'tipo_conta', 'N/A')
    exp = getattr(u, 'premium_expira_em', 'N/A')
    print(f"  ID:{u.id} | {u.username} | tipo_conta: {tc} | expira: {exp}")

print("\n=== PLANOS DE ASSINATURA ===")
for p in SubscriptionPlan.objects.all():
    print(f"  [{p.id}] {p.nome} | R${p.preco} | dias: {p.dias_duracao}")

print("\n=== ASSINATURAS ATIVAS ===")
for s in Subscription.objects.all():
    print(f"  {s.usuario.username} -> {s.plano.nome} | Status: {s.status} | Expira: {s.data_expiracao}")
