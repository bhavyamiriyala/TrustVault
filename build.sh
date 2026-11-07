
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); username = 'bhavya'; user = User.objects.filter(username=username).first(); exec(\"if user is None: raise SystemExit('Admin user not found')\"); user.is_staff = True; user.is_superuser = True; user.save(update_fields=['is_staff', 'is_superuser']); print('Admin permissions enabled for', username)"