from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0003_rename_softwareupdate_softwareupdatemessage_and_more'),
    ]

    operations = [
        # 1. Ajustar la Primary Key para que incluya timestamp (requisito estricto de TimescaleDB)
        migrations.RunSQL(
            sql="""
            ALTER TABLE control_telemetrymessage DROP CONSTRAINT IF EXISTS control_telemetrymessage_pkey CASCADE;
            ALTER TABLE control_telemetrymessage ADD PRIMARY KEY (id, timestamp);
            SELECT create_hypertable('control_telemetrymessage', 'timestamp', if_not_exists => TRUE);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]