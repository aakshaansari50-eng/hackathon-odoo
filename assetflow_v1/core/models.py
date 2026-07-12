from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Department(models.Model):
    name=models.CharField(max_length=100); code=models.CharField(max_length=20, unique=True)
    head=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name='headed_departments')
    parent=models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL); active=models.BooleanField(default=True)
    def __str__(self): return f'{self.code} — {self.name}'
class Profile(models.Model):
    ROLES=[('ADMIN','Admin'),('MANAGER','Asset Manager'),('HEAD','Department Head'),('EMPLOYEE','Employee')]
    user=models.OneToOneField(User,on_delete=models.CASCADE); department=models.ForeignKey(Department,null=True,blank=True,on_delete=models.SET_NULL)
    role=models.CharField(max_length=10,choices=ROLES,default='EMPLOYEE'); active=models.BooleanField(default=True)
    def __str__(self): return self.user.get_full_name() or self.user.username
class Category(models.Model):
    name=models.CharField(max_length=80,unique=True); description=models.TextField(blank=True); warranty_months=models.PositiveIntegerField(default=12); active=models.BooleanField(default=True)
    def __str__(self): return self.name
class Asset(models.Model):
    STATUS=[('AVAILABLE','Available'),('ALLOCATED','Allocated'),('RESERVED','Reserved'),('MAINTENANCE','Maintenance'),('LOST','Lost'),('RETIRED','Retired'),('DISPOSED','Disposed')]
    asset_id=models.CharField(max_length=30,unique=True); name=models.CharField(max_length=150); category=models.ForeignKey(Category,on_delete=models.PROTECT)
    serial_number=models.CharField(max_length=100,blank=True); purchase_date=models.DateField(null=True,blank=True); cost=models.DecimalField(max_digits=12,decimal_places=2,default=0); location=models.CharField(max_length=120,blank=True)
    condition=models.CharField(max_length=60,default='Good'); status=models.CharField(max_length=15,choices=STATUS,default='AVAILABLE'); assigned_to=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name='assets')
    def __str__(self): return f'{self.asset_id} — {self.name}'
class Allocation(models.Model):
    asset=models.ForeignKey(Asset,on_delete=models.PROTECT); employee=models.ForeignKey(User,on_delete=models.PROTECT); allocated_on=models.DateField(default=timezone.localdate); due_back=models.DateField(null=True,blank=True); returned_on=models.DateField(null=True,blank=True); approved_by=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name='approved_allocations')
    def __str__(self): return f'{self.asset} → {self.employee}'
class Resource(models.Model):
    name=models.CharField(max_length=100); location=models.CharField(max_length=120,blank=True); capacity=models.PositiveIntegerField(default=1); active=models.BooleanField(default=True)
    def __str__(self): return self.name
class Booking(models.Model):
    STATUS=[('PENDING','Pending'),('APPROVED','Approved'),('CANCELLED','Cancelled')]
    resource=models.ForeignKey(Resource,on_delete=models.CASCADE); user=models.ForeignKey(User,on_delete=models.CASCADE); start=models.DateTimeField(); end=models.DateTimeField(); purpose=models.CharField(max_length=255); status=models.CharField(max_length=10,choices=STATUS,default='PENDING')
    def __str__(self): return f'{self.resource} ({self.start:%d %b %H:%M})'
class MaintenanceRequest(models.Model):
    STATUS=[('PENDING','Pending'),('APPROVED','Approved'),('IN_PROGRESS','In Progress'),('RESOLVED','Resolved'),('REJECTED','Rejected')]
    asset=models.ForeignKey(Asset,on_delete=models.PROTECT); raised_by=models.ForeignKey(User,on_delete=models.PROTECT); issue=models.TextField(); status=models.CharField(max_length=15,choices=STATUS,default='PENDING'); created_at=models.DateTimeField(auto_now_add=True); resolved_at=models.DateTimeField(null=True,blank=True)
class TransferRequest(models.Model):
    STATUS=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')]
    asset=models.ForeignKey(Asset,on_delete=models.PROTECT); requested_by=models.ForeignKey(User,on_delete=models.PROTECT); target_user=models.ForeignKey(User,on_delete=models.PROTECT,related_name='incoming_transfers'); reason=models.TextField(); status=models.CharField(max_length=10,choices=STATUS,default='PENDING')
class Audit(models.Model):
    asset=models.ForeignKey(Asset,on_delete=models.PROTECT); audited_by=models.ForeignKey(User,on_delete=models.PROTECT); outcome=models.CharField(max_length=20,choices=[('FOUND','Found'),('MISSING','Missing'),('DAMAGED','Damaged')]); notes=models.TextField(blank=True); audited_at=models.DateTimeField(auto_now_add=True)
class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE); title=models.CharField(max_length=140); body=models.CharField(max_length=255); read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self): return f'{self.user.username}: {self.title}'
    LINK_KEYWORDS=[('transfer','transfers'),('booking','bookings'),('maintenance','maintenance'),('asset','assets'),('request','approvals')]
    @property
    def target_url(self):
        from django.urls import reverse
        text=f'{self.title} {self.body}'.lower()
        for keyword,view_name in self.LINK_KEYWORDS:
            if keyword in text:
                return reverse(view_name)
        return reverse('dashboard')
