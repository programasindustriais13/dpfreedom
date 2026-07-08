from django.db import migrations

def rename_rh_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Ensure ContentType and Permission exist
    ct, ct_created = ContentType.objects.get_or_create(app_label='dashboard', model='dashboard_permission')
    perm, perm_created = Permission.objects.get_or_create(
        codename='view_rh_dashboard',
        content_type=ct,
        defaults={'name': 'Can view rh dashboard'}
    )
    
    has_rh = Group.objects.filter(name='RH').exists()
    has_dp = Group.objects.filter(name='Departamento Pessoal').exists()
    
    if has_rh and not has_dp:
        group = Group.objects.get(name='RH')
        group.name = 'Departamento Pessoal'
        group.save()
        group.permissions.add(perm)
    elif not has_rh and not has_dp:
        group = Group.objects.create(name='Departamento Pessoal')
        group.permissions.add(perm)
    else:
        # Both exist or only DP exists
        group = Group.objects.get(name='Departamento Pessoal')
        group.permissions.add(perm)
        if has_rh:
            rh_group = Group.objects.get(name='RH')
            for user in rh_group.user_set.all():
                user.groups.add(group)
            rh_group.delete()

def reverse_rename(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        group = Group.objects.get(name='Departamento Pessoal')
        group.name = 'RH'
        group.save()
    except Group.DoesNotExist:
        pass

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(rename_rh_group, reverse_rename),
    ]
