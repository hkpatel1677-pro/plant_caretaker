import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_caretaker.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
print(','.join(u.username for u in User.objects.filter(is_superuser=True)))
