import os
import re
import secrets
import time

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings

from .models import Document, DocumentPermission, AuditLog

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all fields!')
            return redirect('register')

        if len(password) < 8:
            messages.error(request, 'Password must contain at least 8 characters!')
            return redirect('register')

        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password needs an uppercase letter!')
            return redirect('register')

        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password needs a lowercase letter!')
            return redirect('register')

        if not re.search(r'[0-9]', password):
            messages.error(request, 'Password needs a number!')
            return redirect('register')

        if not re.search(r'[^A-Za-z0-9\s]', password):
            messages.error(request, 'Password needs a special character!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')

        # Generate a 6-digit OTP
        otp = str(secrets.randbelow(900000) + 100000)

        # Store pending registration details in the session
        request.session['pending_registration'] = {
            'username': username,
            'email': email,
            'password_hash': make_password(password),
            'otp_hash': make_password(otp),
            'expires_at': time.time() + 300,
            'attempts': 0,
        }

        # Send OTP to email
        try:
            send_mail(
                subject='TrustVault - Email Verification OTP',
                message=(
                    f'Hello {username},\n\n'
                    f'Your TrustVault verification OTP is: {otp}\n\n'
                    'This OTP expires in 5 minutes.\n'
                    'Do not share this OTP with anyone.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            request.session.pop('pending_registration', None)
            messages.error(
                request,
                'Unable to send OTP. Please check your email configuration.'
            )
            return redirect('register')

        messages.success(request, 'OTP sent to your email address!')
        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


def verify_otp(request):
    pending = request.session.get('pending_registration')

    if not pending:
        messages.error(request, 'Please register first.')
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        if time.time() > pending['expires_at']:
            request.session.pop('pending_registration', None)
            messages.error(request, 'OTP expired. Please register again.')
            return redirect('register')

        if pending['attempts'] >= 5:
            request.session.pop('pending_registration', None)
            messages.error(request, 'Too many incorrect attempts. Please register again.')
            return redirect('register')

        if not check_password(entered_otp, pending['otp_hash']):
            pending['attempts'] += 1
            request.session['pending_registration'] = pending
            messages.error(request, 'Incorrect OTP. Please try again.')
            return redirect('verify_otp')

        # Check again to prevent duplicate registration
        if User.objects.filter(
            username__iexact=pending['username']
        ).exists():
            request.session.pop('pending_registration', None)
            messages.error(request, 'Username already exists. Please register again.')
            return redirect('register')

        if User.objects.filter(
            email__iexact=pending['email']
        ).exists():
            request.session.pop('pending_registration', None)
            messages.error(request, 'Email already registered. Please login.')
            return redirect('login')

        # Create account only after successful OTP verification
        user = User(
            username=pending['username'],
            email=pending['email'],
        )
        user.password = pending['password_hash']
        user.save()

        request.session.pop('pending_registration', None)

        messages.success(
            request,
            'Email verified! Your account has been created. Please login.'
        )
        return redirect('login')

    return render(request, 'accounts/verify_otp.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')

    return render(request, 'accounts/login.html')


@login_required
def dashboard(request):
    my_documents = Document.objects.filter(owner=request.user).count()
    shared_documents = DocumentPermission.objects.filter(
        shared_with=request.user
    ).count()

    return render(request, 'accounts/dashboard.html', {
        'my_documents': my_documents,
        'shared_documents': shared_documents
    })


@login_required
def upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        uploaded_file = request.FILES.get('file')

        if not title or not uploaded_file:
            messages.error(request, 'Please provide a title and select a file!')
            return redirect('upload')

        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        max_size = 5 * 1024 * 1024

        extension = os.path.splitext(uploaded_file.name)[1].lower()

        if extension not in allowed_extensions:
            messages.error(request, 'Only PDF, DOC, DOCX and TXT files are allowed!')
            return redirect('upload')

        if uploaded_file.size > max_size:
            messages.error(request, 'File size must not exceed 5 MB!')
            return redirect('upload')

        document = Document.objects.create(
            owner=request.user,
            title=title,
            file=uploaded_file
        )

        AuditLog.objects.create(
            document=document,
            actor=request.user,
            action='upload',
            details='Document uploaded'
        )

        messages.success(request, 'Document uploaded successfully!')
        return redirect('document_list')

    return render(request, 'accounts/upload.html')


@login_required
def document_list(request):
    search_query = request.GET.get('q', '').strip()

    my_documents = Document.objects.filter(owner=request.user)

    shared_documents = Document.objects.filter(
        permissions__shared_with=request.user
    )

    if search_query:
        my_documents = my_documents.filter(title__icontains=search_query)
        shared_documents = shared_documents.filter(title__icontains=search_query)

    my_documents = my_documents.order_by('-uploaded_at')
    shared_documents = shared_documents.distinct().order_by('-uploaded_at')

    return render(request, 'accounts/document_list.html', {
        'documents': my_documents,
        'shared_documents': shared_documents,
        'search_query': search_query
    })


@login_required
def share_document(request, document_id):
    document = get_object_or_404(
        Document,
        id=document_id,
        owner=request.user
    )

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        permission_type = request.POST.get('permission')

        if permission_type not in ['read', 'edit']:
            messages.error(request, 'Invalid permission selected!')
            return redirect('share_document', document_id=document.id)

        try:
            shared_user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist!')
            return redirect('share_document', document_id=document.id)

        if shared_user == request.user:
            messages.error(request, 'You cannot share a document with yourself!')
            return redirect('share_document', document_id=document.id)

        DocumentPermission.objects.update_or_create(
            document=document,
            shared_with=shared_user,
            defaults={
                'permission': permission_type,
                'granted_by': request.user
            }
        )

        AuditLog.objects.create(
            document=document,
            actor=request.user,
            action='share',
            details=f'Shared with {shared_user.username} ({permission_type})'
        )

        messages.success(request, 'Document shared successfully!')
        return redirect('document_list')

    return render(request, 'accounts/share.html', {
        'document': document
    })



@login_required
def access_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    is_owner = document.owner == request.user

    has_permission = DocumentPermission.objects.filter(
        document=document,
        shared_with=request.user
    ).exists()

    if not is_owner and not has_permission:
        raise Http404

    if not document.file:
        raise Http404("Document file not found.")

    try:
        file_handle = document.file.open('rb')
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("Document file not found.")

    AuditLog.objects.create(
        document=document,
        actor=request.user,
        action='access',
        details='Document downloaded'
    )

    filename = os.path.basename(document.file.name)

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=filename
    )

@login_required
@require_POST
def revoke_access(request, document_id, user_id):
    document = get_object_or_404(
        Document,
        id=document_id,
        owner=request.user
    )

    permission = get_object_or_404(
        DocumentPermission,
        document=document,
        shared_with_id=user_id
    )

    username = permission.shared_with.username
    permission.delete()

    AuditLog.objects.create(
        document=document,
        actor=request.user,
        action='revoke',
        details=f'Access revoked for {username}'
    )

    messages.success(request, 'Document access revoked successfully!')
    return redirect('document_list')


@login_required
def audit_trail(request):
    logs = AuditLog.objects.filter(
        document__owner=request.user
    ).select_related(
        'document',
        'actor'
    ).order_by('-timestamp')

    return render(request, 'accounts/audit_trail.html', {
        'logs': logs
    })


@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    is_owner = document.owner == request.user

    permission = DocumentPermission.objects.filter(
        document=document,
        shared_with=request.user
    ).first()

    if not is_owner and (
        permission is None or permission.permission != 'edit'
    ):
        raise Http404

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        uploaded_file = request.FILES.get('file')

        if not title:
            messages.error(request, 'Document title cannot be empty!')
            return redirect('edit_document', document_id=document.id)

        if uploaded_file:
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            max_size = 5 * 1024 * 1024

            extension = os.path.splitext(uploaded_file.name)[1].lower()

            if extension not in allowed_extensions:
                messages.error(
                    request,
                    'Only PDF, DOC, DOCX and TXT files are allowed!'
                )
                return redirect('edit_document', document_id=document.id)

            if uploaded_file.size > max_size:
                messages.error(request, 'File size must not exceed 5 MB!')
                return redirect('edit_document', document_id=document.id)

            document.file = uploaded_file

        document.title = title
        document.save()

        AuditLog.objects.create(
            document=document,
            actor=request.user,
            action='edit',
            details='Document updated'
        )

        messages.success(request, 'Document updated successfully!')
        return redirect('document_list')

    return render(request, 'accounts/edit_document.html', {
        'document': document
    })


@login_required
@require_POST
def user_logout(request):
    logout(request)
    return redirect('login')