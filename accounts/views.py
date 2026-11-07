
import os
import re
import zipfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Document, DocumentPermission, AuditLog


# --------------------------------------------------
# DOCUMENT FILE VALIDATION
# --------------------------------------------------

def is_valid_document_file(uploaded_file, extension):
    """Perform basic file-format checks. This is not a malware scan."""
    try:
        uploaded_file.seek(0)

        if extension == '.pdf':
            return uploaded_file.read(5) == b'%PDF-'

        if extension == '.doc':
            doc_signature = bytes.fromhex('D0 CF 11 E0 A1 B1 1A E1')
            return uploaded_file.read(8) == doc_signature

        if extension == '.docx':
            uploaded_file.seek(0)

            if not zipfile.is_zipfile(uploaded_file):
                return False

            uploaded_file.seek(0)

            with zipfile.ZipFile(uploaded_file, 'r') as archive:
                names = archive.namelist()
                return (
                    '[Content_Types].xml' in names
                    and 'word/document.xml' in names
                )

        if extension == '.txt':
            content = uploaded_file.read()
            content.decode('utf-8-sig')
            return b'\x00' not in content

        return False

    except (
        UnicodeDecodeError,
        zipfile.BadZipFile,
        OSError,
        ValueError
    ):
        return False

    finally:
        uploaded_file.seek(0)


# --------------------------------------------------
# USER REGISTRATION - WITHOUT OTP
# --------------------------------------------------

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all fields!')
            return redirect('register')

        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            messages.error(request, 'Enter a valid email address!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if len(password) < 8:
            messages.error(
                request,
                'Password must contain at least 8 characters!'
            )
            return redirect('register')

        if not re.search(r'[A-Z]', password):
            messages.error(
                request,
                'Password needs an uppercase letter!'
            )
            return redirect('register')

        if not re.search(r'[a-z]', password):
            messages.error(
                request,
                'Password needs a lowercase letter!'
            )
            return redirect('register')

        if not re.search(r'[0-9]', password):
            messages.error(
                request,
                'Password needs a number!'
            )
            return redirect('register')

        if not re.search(r'[^A-Za-z0-9\s]', password):
            messages.error(
                request,
                'Password needs a special character!'
            )
            return redirect('register')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')

        # Create the account immediately without email OTP.
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            'Account created successfully! Please login.'
        )

        return redirect('login')

    return render(request, 'accounts/register.html')


# --------------------------------------------------
# USER LOGIN
# --------------------------------------------------

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(
                request,
                'Please enter username and password!'
            )
            return redirect('login')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            messages.success(request, 'Login successful!')
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password!')
        return redirect('login')

    return render(request, 'accounts/login.html')


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@login_required
def dashboard(request):

    documents = Document.objects.filter(owner=request.user)

    shared_permissions = DocumentPermission.objects.filter(
        shared_with=request.user
    ).select_related('document')

    return render(
        request,
        'accounts/dashboard.html',
        {
            'documents': documents,
            'shared_permissions': shared_permissions,
            'document_count': documents.count(),
            'shared_count': shared_permissions.count(),
        }
    )


# --------------------------------------------------
# DOCUMENT UPLOAD
# --------------------------------------------------

@login_required
def upload_document(request):

    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        uploaded_file = request.FILES.get('file')

        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        max_size = 30 * 1024 * 1024

        if not title:
            messages.error(request, 'Document title cannot be empty!')
            return redirect('upload')

        if not uploaded_file:
            messages.error(request, 'Please select a document to upload!')
            return redirect('upload')

        extension = os.path.splitext(uploaded_file.name)[1].lower()

        if extension not in allowed_extensions:
            messages.error(
                request,
                'Only PDF, DOC, DOCX and TXT files are allowed!'
            )
            return redirect('upload')

        if uploaded_file.size > max_size:
            messages.error(
                request,
                'File size must not exceed 30 MB!'
            )
            return redirect('upload')

        if not is_valid_document_file(uploaded_file, extension):
            messages.error(
                request,
                'Invalid file content. Please upload a valid document!'
            )
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


# --------------------------------------------------
# DOCUMENT LIST
# --------------------------------------------------

@login_required
def document_list(request):

    search_query = request.GET.get('q', '').strip()

    documents = Document.objects.filter(
        owner=request.user
    ).order_by('-uploaded_at')

    shared_documents = Document.objects.filter(
        permissions__shared_with=request.user
    ).distinct().order_by('-uploaded_at')

    if search_query:
        documents = documents.filter(title__icontains=search_query)
        shared_documents = shared_documents.filter(
            title__icontains=search_query
        )

    return render(
        request,
        'accounts/document_list.html',
        {
            'documents': documents,
            'shared_documents': shared_documents,
            'search_query': search_query,
            'q': search_query,
        }
    )


# --------------------------------------------------
# SHARE DOCUMENT
# --------------------------------------------------

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
            messages.error(request, 'Invalid permission selected.')
            return redirect('share_document', document_id=document.id)

        try:
            shared_user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('share_document', document_id=document.id)

        if shared_user == request.user:
            messages.error(
                request,
                'You cannot share a document with yourself.'
            )
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
            details=(
                f"Shared with {shared_user.username} "
                f"({permission_type} permission)"
            )
        )

        AuditLog.objects.create(
            document=None,
            actor=shared_user,
            action='share',
            details=(
                f"Received '{document.title}' from "
                f"{request.user.username} with {permission_type} permission"
            )
        )

        messages.success(request, 'Document shared successfully!')
        return redirect('document_list')

    return render(
        request,
        'accounts/share.html',
        {'document': document}
    )


# --------------------------------------------------
# ACCESS / DOWNLOAD DOCUMENT
# --------------------------------------------------

@login_required
def access_document(request, document_id):

    document = get_object_or_404(Document, id=document_id)

    is_owner = document.owner == request.user

    permission = DocumentPermission.objects.filter(
        document=document,
        shared_with=request.user
    ).first()

    if not is_owner and permission is None:
        raise Http404

    AuditLog.objects.create(
        document=document,
        actor=request.user,
        action='access',
        details='Document accessed'
    )

    try:
        document.file.open('rb')

        return FileResponse(
            document.file,
            as_attachment=True,
            filename=os.path.basename(document.file.name)
        )

    except (OSError, ValueError):
        raise Http404('Document file not found.')


# --------------------------------------------------
# REVOKE DOCUMENT ACCESS
# --------------------------------------------------

@login_required
@require_POST
def revoke_access(request, document_id, user_id):

    permission = get_object_or_404(
        DocumentPermission,
        document_id=document_id,
        shared_with_id=user_id,
        document__owner=request.user
    )

    document = permission.document
    username = permission.shared_with.username

    permission.delete()

    AuditLog.objects.create(
        document=document,
        actor=request.user,
        action='revoke',
        details=f'Access revoked for {username}'
    )

    messages.success(
        request,
        'Document access revoked successfully!'
    )

    return redirect('document_list')


# --------------------------------------------------
# AUDIT TRAIL
# --------------------------------------------------

@login_required
def audit_trail(request):

    logs = AuditLog.objects.filter(
        Q(document__owner=request.user) |
        Q(actor=request.user)
    ).select_related(
        'document',
        'actor'
    ).distinct().order_by('-timestamp')

    return render(
        request,
        'accounts/audit_trail.html',
        {'logs': logs}
    )


# --------------------------------------------------
# EDIT DOCUMENT
# --------------------------------------------------

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
            return redirect(
                'edit_document',
                document_id=document.id
            )

        if uploaded_file:

            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            max_size = 30 * 1024 * 1024

            extension = os.path.splitext(uploaded_file.name)[1].lower()

            if extension not in allowed_extensions:
                messages.error(
                    request,
                    'Only PDF, DOC, DOCX and TXT files are allowed!'
                )
                return redirect(
                    'edit_document',
                    document_id=document.id
                )

            if uploaded_file.size > max_size:
                messages.error(
                    request,
                    'File size must not exceed 30 MB!'
                )
                return redirect(
                    'edit_document',
                    document_id=document.id
                )

            if not is_valid_document_file(uploaded_file, extension):
                messages.error(
                    request,
                    'Invalid file content. Please upload a valid document!'
                )
                return redirect(
                    'edit_document',
                    document_id=document.id
                )

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

    return render(
        request,
        'accounts/edit_document.html',
        {'document': document}
    )


# --------------------------------------------------
# USER LOGOUT
# --------------------------------------------------

@login_required
@require_POST
def user_logout(request):

    logout(request)
    return redirect('login')
