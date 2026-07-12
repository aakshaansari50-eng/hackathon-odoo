from django.contrib import admin
from .models import *

admin.site.site_header = 'AssetFlow Administration'
admin.site.site_title = 'AssetFlow Admin'
admin.site.index_title = 'Manage your assets and operations'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','role','department','active'); list_filter=('role','active','department'); search_fields=('user__username','user__first_name','user__last_name')
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display=('asset_id','name','category','status','assigned_to','location'); list_filter=('status','category'); search_fields=('asset_id','name','serial_number')
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display=('resource','user','start','end','status'); list_filter=('status','resource')
@admin.register(MaintenanceRequest)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display=('asset','raised_by','status','created_at'); list_filter=('status',)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display=('title','user','read','created_at'); list_filter=('read',); search_fields=('title','body','user__username')
admin.site.register([Department,Category,Allocation,Resource,TransferRequest,Audit])
