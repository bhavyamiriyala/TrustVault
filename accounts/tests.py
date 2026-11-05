
import re
import tempfile
import time

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import make_password

from .models import Document, DocumentPermission, AuditLog


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(
    MEDIA_ROOT=TEST_MEDIA_ROOT,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class TrustVaultTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='TestPass@123'
        )

        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='TestPass@123'
        )

        self.editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='TestPass@123'
        )

        self.document = Document.objects.create(
            owner=self.owner,
            title='Test Document',
            file=SimpleUploadedFile(
                'test.txt',
                b'This is a test document.',
                content_type='text/plain'
            )
        )

    def login_as(self, user):
        self.client.force_login(user)

    def test_registration_sends_otp_and_creates_account(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'StrongPass@123',
                'confirm_password': 'StrongPass@123',
            }
        )

        self.assertRedirects(response, reverse('verify_otp'))
        self.assertEqual(len(mail.outbox), 1)

        otp_match = re.search(
            r'OTP is: (\d{6})',
            mail.outbox[0].body
        )
        self.assertIsNotNone(otp_match)

        otp = otp_match.group(1)

        response = self.client.post(
            reverse('verify_otp'),
            {'otp': otp}
        )

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )

    def test_registration_rejects_incorrect_otp(self):
        session = self.client.session

        session['pending_registration'] = {
            'username': 'wrongotpuser',
            'email': 'wrongotp@example.com',
            'password_hash': make_password('StrongPass@123'),
            'otp_hash': make_password('123456'),
            'expires_at': time.time() + 300,
            'attempts': 0,
        }

        session.save()

        response = self.client.post(
            reverse('verify_otp'),
            {'otp': '654321'}
        )

        self.assertRedirects(response, reverse('verify_otp'))

        self.assertFalse(
            User.objects.filter(username='wrongotpuser').exists()
        )

        self.assertEqual(
            self.client.session['pending_registration']['attempts'],
            1
        )

    def test_registration_rejects_expired_otp(self):
        session = self.client.session

        session['pending_registration'] = {
            'username': 'expiredotpuser',
            'email': 'expiredotp@example.com',
            'password_hash': make_password('StrongPass@123'),
            'otp_hash': make_password('123456'),
            'expires_at': time.time() - 10,
            'attempts': 0,
        }

        session.save()

        response = self.client.post(
            reverse('verify_otp'),
            {'otp': '123456'}
        )

        self.assertRedirects(response, reverse('register'))

        self.assertNotIn(
            'pending_registration',
            self.client.session
        )

        self.assertFalse(
            User.objects.filter(username='expiredotpuser').exists()
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'owner',
                'password': 'TestPass@123',
            }
        )

        self.assertRedirects(response, reverse('dashboard'))

    def test_user_cannot_login_with_incorrect_password(self):
        self.client.post(
            reverse('login'),
            {
                'username': 'owner',
                'password': 'WrongPassword@123',
            }
        )

        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}"
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}"
        )

    def test_document_owner_can_view_document_list(self):
        self.login_as(self.owner)

        response = self.client.get(reverse('document_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')

    def test_document_search(self):
        self.login_as(self.owner)

        Document.objects.create(
            owner=self.owner,
            title='Another File',
            file=SimpleUploadedFile(
                'another.txt',
                b'Another document',
                content_type='text/plain'
            )
        )

        response = self.client.get(
            reverse('document_list'),
            {'q': 'Test'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')
        self.assertNotContains(response, 'Another File')

    def test_user_can_upload_valid_document(self):
        self.login_as(self.owner)

        uploaded_file = SimpleUploadedFile(
            'newfile.txt',
            b'New document content',
            content_type='text/plain'
        )

        response = self.client.post(
            reverse('upload'),
            {
                'title': 'New Document',
                'file': uploaded_file,
            }
        )

        self.assertRedirects(response, reverse('document_list'))

        self.assertTrue(
            Document.objects.filter(
                owner=self.owner,
                title='New Document'
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action='upload',
                actor=self.owner
            ).exists()
        )

    def test_upload_rejects_oversized_file(self):
        self.login_as(self.owner)

        large_file = SimpleUploadedFile(
            'large.txt',
            b'A' * (5 * 1024 * 1024 + 1),
            content_type='text/plain'
        )

        response = self.client.post(
            reverse('upload'),
            {
                'title': 'Large Document',
                'file': large_file,
            }
        )

        self.assertRedirects(response, reverse('upload'))

        self.assertFalse(
            Document.objects.filter(
                title='Large Document'
            ).exists()
        )

    def test_upload_rejects_invalid_extension(self):
        self.login_as(self.owner)

        uploaded_file = SimpleUploadedFile(
            'malware.exe',
            b'Invalid file',
            content_type='application/octet-stream'
        )

        response = self.client.post(
            reverse('upload'),
            {
                'title': 'Invalid Document',
                'file': uploaded_file,
            }
        )

        self.assertRedirects(response, reverse('upload'))

        self.assertFalse(
            Document.objects.filter(
                title='Invalid Document'
            ).exists()
        )

    def test_owner_can_share_document_with_read_permission(self):
        self.login_as(self.owner)

        response = self.client.post(
            reverse(
                'share_document',
                args=[self.document.id]
            ),
            {
                'username': 'reader',
                'permission': 'read',
            }
        )

        self.assertRedirects(response, reverse('document_list'))

        self.assertTrue(
            DocumentPermission.objects.filter(
                document=self.document,
                shared_with=self.reader,
                permission='read'
            ).exists()
        )

    def test_shared_user_can_download_document(self):
        DocumentPermission.objects.create(
            document=self.document,
            shared_with=self.reader,
            permission='read',
            granted_by=self.owner
        )

        self.login_as(self.reader)

        response = self.client.get(
            reverse(
                'access_document',
                args=[self.document.id]
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response['Content-Disposition'].startswith('attachment')
        )
        response.close()

    def test_unshared_user_cannot_access_document(self):
        self.login_as(self.editor)

        response = self.client.get(
            reverse(
                'access_document',
                args=[self.document.id]
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_read_permission_user_cannot_edit_document(self):
        DocumentPermission.objects.create(
            document=self.document,
            shared_with=self.reader,
            permission='read',
            granted_by=self.owner
        )

        self.login_as(self.reader)

        response = self.client.get(
            reverse(
                'edit_document',
                args=[self.document.id]
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_permission_user_can_edit_document(self):
        DocumentPermission.objects.create(
            document=self.document,
            shared_with=self.editor,
            permission='edit',
            granted_by=self.owner
        )

        self.login_as(self.editor)

        response = self.client.post(
            reverse(
                'edit_document',
                args=[self.document.id]
            ),
            {'title': 'Updated Document'}
        )

        self.assertRedirects(response, reverse('document_list'))

        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Document')

    def test_owner_can_revoke_document_access(self):
        DocumentPermission.objects.create(
            document=self.document,
            shared_with=self.reader,
            permission='read',
            granted_by=self.owner
        )

        self.login_as(self.owner)

        response = self.client.post(
            reverse(
                'revoke_access',
                args=[self.document.id, self.reader.id]
            )
        )

        self.assertRedirects(response, reverse('document_list'))

        self.assertFalse(
            DocumentPermission.objects.filter(
                document=self.document,
                shared_with=self.reader
            ).exists()
        )

    def test_non_owner_cannot_revoke_access(self):
        DocumentPermission.objects.create(
            document=self.document,
            shared_with=self.reader,
            permission='read',
            granted_by=self.owner
        )

        self.login_as(self.reader)

        response = self.client.post(
            reverse(
                'revoke_access',
                args=[self.document.id, self.reader.id]
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_audit_trail_is_available_to_owner(self):
        AuditLog.objects.create(
            document=self.document,
            actor=self.owner,
            action='upload',
            details='Test upload'
        )

        self.login_as(self.owner)

        response = self.client.get(reverse('audit_trail'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test upload')

    def test_other_user_cannot_view_owner_audit_logs(self):
        AuditLog.objects.create(
            document=self.document,
            actor=self.owner,
            action='upload',
            details='Private owner activity'
        )

        self.login_as(self.reader)

        response = self.client.get(reverse('audit_trail'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Private owner activity')
