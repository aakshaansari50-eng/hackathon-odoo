from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import csv
from django.utils import timezone
from .forms import AssetForm, BookingForm, MaintenanceForm, SignupForm, TransferForm
from .models import *

def profile_for(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    if user.is_superuser and profile.role != 'ADMIN':
        profile.role = 'ADMIN'; profile.save(update_fields=['role'])
    return profile

def can_manage(user):
    return user.is_authenticated and (user.is_superuser or profile_for(user).role in ['ADMIN', 'MANAGER'])

def manager_required(view):
    return user_passes_test(can_manage)(view)

def notify_managers(title, body):
    users = User.objects.filter(profile__role__in=['ADMIN','MANAGER'], profile__active=True).distinct()
    for user in users:
        Notification.objects.create(user=user, title=title, body=body)

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user: login(request, user); return redirect('dashboard')
        messages.error(request, 'Incorrect username or password.')
    return render(request, 'core/login.html')
def signup(request):
    form=SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid(): form.save(); messages.success(request, 'Account created. Please sign in.'); return redirect('login')
    return render(request, 'core/signup.html', {'form':form})
def logout_view(request): logout(request); return redirect('login')
def greeting_for(now):
    hour=now.hour
    if hour < 12: return 'Good morning'
    if hour < 17: return 'Good afternoon'
    return 'Good evening'

@login_required
def dashboard(request):
    profile=profile_for(request.user)
    today=timezone.localdate(); assets=Asset.objects.all()
    stats={'total':assets.count(),'available':assets.filter(status='AVAILABLE').count(),'allocated':assets.filter(status='ALLOCATED').count(),'reserved':assets.filter(status='RESERVED').count(),'maintenance':MaintenanceRequest.objects.filter(created_at__date=today).count(),'bookings':Booking.objects.filter(status='APPROVED',end__gte=timezone.now()).count(),'transfers':TransferRequest.objects.filter(status='PENDING').count(),'returns':Allocation.objects.filter(due_back__gte=today,returned_on__isnull=True).count(),'overdue':Allocation.objects.filter(due_back__lt=today,returned_on__isnull=True).count(),'lost':assets.filter(status='LOST').count()}
    return render(request,'core/dashboard.html',{'stats':stats,'profile':profile,'greeting':greeting_for(timezone.localtime()),'activities':MaintenanceRequest.objects.select_related('asset','raised_by').order_by('-created_at')[:5],'notifications':Notification.objects.filter(user=request.user)[:5],'unread_notifications':Notification.objects.filter(user=request.user,read=False).count(),'category_data':list(assets.values('category__name').annotate(total=Count('id')).order_by('-total'))})
@login_required
def assets(request):
    items=Asset.objects.select_related('category','assigned_to').order_by('-id')
    query=request.GET.get('q','').strip()
    status=request.GET.get('status','').strip()
    if query: items=items.filter(Q(name__icontains=query)|Q(asset_id__icontains=query)|Q(serial_number__icontains=query))
    if status: items=items.filter(status=status)
    return render(request,'core/assets.html',{'assets':items,'statuses':Asset.STATUS,'selected_status':status,'query':query,'can_manage':can_manage(request.user)})

@login_required
@manager_required
def asset_status_update(request, pk):
    asset=get_object_or_404(Asset, pk=pk)
    if request.method=='POST':
        new_status=request.POST.get('status','').strip()
        valid_statuses=dict(Asset.STATUS)
        if new_status in valid_statuses and new_status != asset.status:
            old_display=asset.get_status_display()
            asset.status=new_status
            asset.save(update_fields=['status'])
            Notification.objects.create(user=request.user, title='Asset status updated', body=f'{asset.asset_id} · {asset.name} changed from {old_display} to {asset.get_status_display()}.')
            if request.headers.get('x-requested-with')=='XMLHttpRequest':
                return JsonResponse({'ok':True,'status':asset.status,'status_display':asset.get_status_display()})
            messages.success(request, f'{asset.name} status updated to {asset.get_status_display()}.')
        elif new_status not in valid_statuses:
            if request.headers.get('x-requested-with')=='XMLHttpRequest':
                return JsonResponse({'ok':False,'error':'Invalid status'}, status=400)
            messages.error(request, 'Invalid status selected.')
    next_url=request.POST.get('next') or request.META.get('HTTP_REFERER') or 'assets'
    return redirect(next_url)

@login_required
def export_assets(request):
    response=HttpResponse(content_type='text/csv'); response['Content-Disposition']='attachment; filename="assetflow-assets.csv"'
    writer=csv.writer(response); writer.writerow(['Asset ID','Name','Category','Serial Number','Location','Status','Assigned To'])
    for asset in Asset.objects.select_related('category','assigned_to').order_by('asset_id'):
        writer.writerow([asset.asset_id,asset.name,asset.category.name,asset.serial_number,asset.location,asset.get_status_display(),asset.assigned_to.username if asset.assigned_to else ''])
    return response
@login_required
@manager_required
def asset_create(request):
    form=AssetForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        asset=form.save()
        notify_managers('New asset registered', f'{asset.asset_id} · {asset.name} was added by {request.user.get_full_name() or request.user.username}.')
        messages.success(request,'Asset registered successfully. A notification has been sent to the management team.')
        return redirect('assets')
    return render(request,'core/form.html',{'form':form,'title':'Register a new asset','icon':'bi-box-seam'})
@login_required
def bookings(request):
    form=BookingForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        b=form.save(commit=False); overlap=Booking.objects.filter(resource=b.resource,status__in=['PENDING','APPROVED'],start__lt=b.end,end__gt=b.start).exists()
        if overlap: messages.error(request,'That resource already has a booking in the chosen time slot.')
        else:
            b.user=request.user; b.save()
            Notification.objects.create(user=request.user,title='Booking received',body=f'{b.resource} booking is pending approval.')
            notify_managers('Booking approval needed', f'{request.user.get_full_name() or request.user.username} requested {b.resource}.')
            messages.success(request,'Booking request submitted.'); return redirect('bookings')
    query=request.GET.get('q','').strip()
    listing=Booking.objects.select_related('resource','user').order_by('-start')
    if query: listing=listing.filter(Q(resource__name__icontains=query)|Q(purpose__icontains=query)|Q(user__username__icontains=query)|Q(user__first_name__icontains=query)|Q(user__last_name__icontains=query))
    return render(request,'core/bookings.html',{'form':form,'bookings':listing,'query':query})
@login_required
def maintenance(request):
    form=MaintenanceForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        item=form.save(commit=False); item.raised_by=request.user; item.save(); item.asset.status='MAINTENANCE'; item.asset.save()
        notify_managers('Maintenance request raised', f'{request.user.get_full_name() or request.user.username} reported {item.asset.name}.')
        messages.success(request,'Maintenance request sent to Asset Management.'); return redirect('maintenance')
    query=request.GET.get('q','').strip()
    listing=MaintenanceRequest.objects.select_related('asset','raised_by').order_by('-created_at')
    if query: listing=listing.filter(Q(asset__name__icontains=query)|Q(issue__icontains=query)|Q(raised_by__username__icontains=query)|Q(raised_by__first_name__icontains=query)|Q(raised_by__last_name__icontains=query))
    return render(request,'core/maintenance.html',{'form':form,'requests':listing,'query':query})
@login_required
def directory(request):
    query=request.GET.get('q','').strip()
    listing=Profile.objects.select_related('user','department').all()
    if query: listing=listing.filter(Q(user__username__icontains=query)|Q(user__first_name__icontains=query)|Q(user__last_name__icontains=query)|Q(user__email__icontains=query)|Q(department__name__icontains=query))
    return render(request,'core/directory.html',{'profiles':listing,'query':query})
@login_required
def departments(request):
    query=request.GET.get('q','').strip()
    listing=Department.objects.select_related('head','parent')
    if query: listing=listing.filter(Q(name__icontains=query)|Q(code__icontains=query))
    return render(request,'core/departments.html',{'departments':listing,'query':query})
@login_required
def reports(request): return render(request,'core/reports.html',{'by_dept':Profile.objects.values('department__name').annotate(total_assets=Count('user__assets')).order_by('-total_assets'),'by_status':Asset.objects.values('status').annotate(total=Count('id')).order_by('-total')})

@login_required
def export_report(request):
    response=HttpResponse(content_type='text/csv'); response['Content-Disposition']='attachment; filename="assetflow-report.csv"'
    writer=csv.writer(response); writer.writerow(['Status','Asset count'])
    for row in Asset.objects.values('status').annotate(total=Count('id')).order_by('status'): writer.writerow([row['status'],row['total']])
    return response

@login_required
def notifications(request):
    if request.method=='POST' and request.POST.get('action')=='mark_all_read':
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    query=request.GET.get('q','').strip()
    items=Notification.objects.filter(user=request.user)
    if query: items=items.filter(Q(title__icontains=query)|Q(body__icontains=query))
    return render(request, 'core/notifications.html', {'notifications':items,'query':query})

@login_required
def notification_open(request, pk):
    notification=Notification.objects.filter(pk=pk, user=request.user).first()
    if not notification:
        messages.error(request, 'Notification not found.')
        return redirect('notifications')
    if not notification.read:
        notification.read=True; notification.save(update_fields=['read'])
    return redirect(notification.target_url)

@login_required
def transfers(request):
    form=TransferForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        transfer=form.save(commit=False); transfer.requested_by=request.user; transfer.save()
        Notification.objects.create(user=transfer.target_user,title='Asset transfer requested',body=f'{request.user.get_full_name() or request.user.username} requested transfer of {transfer.asset.name}.')
        notify_managers('Transfer approval needed', f'{transfer.asset.name} transfer needs review.')
        messages.success(request, 'Transfer request submitted.'); return redirect('transfers')
    query=request.GET.get('q','').strip()
    listing=TransferRequest.objects.select_related('asset','requested_by','target_user').order_by('-id')
    if query: listing=listing.filter(Q(asset__name__icontains=query)|Q(reason__icontains=query)|Q(requested_by__username__icontains=query)|Q(target_user__username__icontains=query))
    return render(request, 'core/transfers.html', {'form':form,'transfers':listing,'query':query})

@manager_required
def approvals(request):
    if request.method == 'POST':
        kind=request.POST.get('kind'); item_id=request.POST.get('id'); action=request.POST.get('action')
        model={'booking':Booking,'maintenance':MaintenanceRequest,'transfer':TransferRequest}.get(kind)
        item=model.objects.filter(pk=item_id).first() if model else None
        if not item or action not in ['approve','reject','resolve']:
            messages.error(request,'Invalid approval action.'); return redirect('approvals')
        if kind=='booking':
            item.status='APPROVED' if action=='approve' else 'CANCELLED'; recipient=item.user
        elif kind=='maintenance':
            item.status='RESOLVED' if action=='resolve' else ('APPROVED' if action=='approve' else 'REJECTED'); recipient=item.raised_by
            if action=='resolve': item.resolved_at=timezone.now(); item.asset.status='AVAILABLE'; item.asset.save(update_fields=['status'])
        else:
            item.status='APPROVED' if action=='approve' else 'REJECTED'; recipient=item.requested_by
            if action=='approve': item.asset.assigned_to=item.target_user; item.asset.status='ALLOCATED'; item.asset.save(update_fields=['assigned_to','status'])
        item.save(); Notification.objects.create(user=recipient,title='Request updated',body=f'Your {kind} request is now {item.get_status_display().lower()}.')
        messages.success(request,'Request updated successfully.'); return redirect('approvals')
    return render(request,'core/approvals.html',{'bookings':Booking.objects.filter(status='PENDING').select_related('resource','user'),'maintenance_requests':MaintenanceRequest.objects.exclude(status__in=['RESOLVED','REJECTED']).select_related('asset','raised_by'),'transfers':TransferRequest.objects.filter(status='PENDING').select_related('asset','requested_by','target_user')})
