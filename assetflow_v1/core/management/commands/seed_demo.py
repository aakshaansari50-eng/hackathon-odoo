from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Asset, Booking, Category, Department, MaintenanceRequest, Profile, Resource

class Command(BaseCommand):
    help = 'Creates a safe demonstration workspace for AssetFlow.'

    def handle(self, *args, **kwargs):
        admin, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@assetflow.local','first_name':'Aarav','last_name':'Sharma','is_staff':True,'is_superuser':True})
        if created: admin.set_password('Admin@123'); admin.save()
        it, _ = Department.objects.get_or_create(code='IT', defaults={'name':'Information Technology','head':admin})
        ops, _ = Department.objects.get_or_create(code='OPS', defaults={'name':'Operations','head':admin})
        profile, _ = Profile.objects.get_or_create(user=admin); profile.role='ADMIN'; profile.department=it; profile.save()
        manager, created = User.objects.get_or_create(username='manager', defaults={'email':'manager@assetflow.local','first_name':'Rohan','last_name':'Mehta'})
        if created: manager.set_password('Manager@123'); manager.save()
        mp, _ = Profile.objects.get_or_create(user=manager); mp.department=it; mp.role='MANAGER'; mp.save()
        employee, created = User.objects.get_or_create(username='priya', defaults={'email':'priya@assetflow.local','first_name':'Priya','last_name':'Nair'})
        if created: employee.set_password('Employee@123'); employee.save()
        p, _ = Profile.objects.get_or_create(user=employee); p.department=ops; p.role='EMPLOYEE'; p.save()
        laptop, _ = Category.objects.get_or_create(name='Laptop', defaults={'description':'Portable company computers','warranty_months':36})
        monitor, _ = Category.objects.get_or_create(name='Monitor', defaults={'description':'External display equipment','warranty_months':24})
        Asset.objects.get_or_create(asset_id='AF-LAP-001',defaults={'name':'MacBook Pro 14','category':laptop,'serial_number':'MBP-2026-001','location':'Bengaluru HQ','status':'ALLOCATED','assigned_to':employee,'cost':185000})
        Asset.objects.get_or_create(asset_id='AF-MON-014',defaults={'name':'Dell UltraSharp 27','category':monitor,'serial_number':'DEL-014','location':'Bengaluru HQ','status':'AVAILABLE','cost':42000})
        Asset.objects.get_or_create(asset_id='AF-LAP-009',defaults={'name':'ThinkPad X1 Carbon','category':laptop,'location':'Mumbai Office','status':'MAINTENANCE','cost':130000})
        room, _ = Resource.objects.get_or_create(name='Ocean Meeting Room',defaults={'location':'Bengaluru HQ · Floor 3','capacity':12})
        now=timezone.now(); Booking.objects.get_or_create(resource=room,user=employee,start=now+timedelta(days=1),end=now+timedelta(days=1,hours=1),defaults={'purpose':'Sprint planning','status':'APPROVED'})
        damaged=Asset.objects.get(asset_id='AF-LAP-009'); MaintenanceRequest.objects.get_or_create(asset=damaged,raised_by=employee,defaults={'issue':'Battery requires inspection','status':'IN_PROGRESS'})
        self.stdout.write(self.style.SUCCESS('Demo data ready. Logins: admin/Admin@123, manager/Manager@123, priya/Employee@123'))
