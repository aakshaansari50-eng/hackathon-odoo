from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [migrations.AlterModelOptions(name='notification', options={'ordering': ['-created_at']})]
