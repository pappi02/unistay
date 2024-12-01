# Generated by Django 5.1.3 on 2024-11-28 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0004_remove_booking_room_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='emergency_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='booking',
            name='emergency_relationship',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='booking',
            name='full_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='booking',
            name='room_type',
            field=models.CharField(choices=[('Single', 'Single'), ('Double', 'Double'), ('Bedsitter', 'Bedsitter')], max_length=15),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='location',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='main_image',
            field=models.ImageField(upload_to='media/main'),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='name',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='total_rooms',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='price_per_semester',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
