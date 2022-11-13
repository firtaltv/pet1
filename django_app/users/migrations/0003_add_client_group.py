# Generated by Django 4.0.3 on 2022-09-15 13:32

from django.db import migrations


def add_client_group(apps, schema_editor):
    """
    Add 'Client' group.
    'Client' has next permissions:
    - Slot - Can view permission
    - Massage - Can add/change/delete/view permission
    :param apps:
    :param schema_editor:
    :return:
    """
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")

    db_alias = schema_editor.connection.alias

    # Adding 'Client' group
    permissions_code_names = ["view_slot", "add_massage", "change_massage", "delete_massage", "view_massage"]
    permissions = permission_model.objects.using(db_alias).filter(codename__in=permissions_code_names)
    group, _ = group_model.objects.using(db_alias).get_or_create(name="Client")
    group.permissions.set(permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_therapist_group'),
    ]

    operations = [
        migrations.RunPython(add_client_group),
    ]