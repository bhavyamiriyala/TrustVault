
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Document, DocumentPermission, AuditLog


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
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

    # REGISTRATION TESTS

    def test_registration_creates_account_without_otp(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'StrongPass@123',
                'confirm_password': 'StrongPass@123',
            }
        )

        self.assertRedirects(response, reverse('login'))

        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('StrongPass@123'))

    def test_registration_rejects_duplicate_username(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'owner',
                'email': 'newowner@example.com',
                'password': 'StrongPass@123',
                'confirm_password': 'StrongPass@123',
            }
        )

        self.assertRedirects(response, reverse('register'))
        self.assertEqual(User.objects.filter(username='owner').count(), 1)

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'mismatchuser',
                'email': 'mismatch@example.com',
                'password': 'StrongPass@123',
                'confirm_password': 'DifferentPass@123',
            }
        )

        self.assertRedirects(response, reverse('register'))
        self.assertFalse(
            User.objects.filter(username='mismatchuser').exists()
        )

    # LOGIN TESTS

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

    # DOCUMENT LIST TESTS

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

    # DOCUMENT UPLOAD TESTS

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
            Document.objects.filter(title='Large Document').exists()
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
            Document.objects.filter(title='Invalid Document').exists()
        )

    def test_upload_rejects_fake_pdf_file(self):
        self.login_as(self.owner)

        fake_pdf = SimpleUploadedFile(
            'fake.pdf',
            b'This is not a real PDF file',
            content_type='application/pdf'
        )

        response = self.client.post(
            reverse('upload'),
            {
                'title': 'Fake PDF',
                'file': fake_pdf,
            }
        )

        self.assertRedirects(response, reverse('upload'))

        self.assertFalse(
            Document.objects.filter(title='Fake PDF').exists()
        )

    # DOCUMENT SHARING TESTS

    def test_owner_can_share_document_with_read_permission(self):
        self.login_as(self.owner)

        response = self.client.post(
            reverse('share_document', args=[self.document.id]),
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
            reverse('access_document', args=[self.document.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response['Content-Disposition'].startswith('attachment')
        )
        response.close()

    def test_unshared_user_cannot_access_document(self):
        self.login_as(self.editor)

        response = self.client.get(
            reverse('access_document', args=[self.document.id])
        )

        self.assertEqual(response.status_code, 404)

    # DOCUMENT EDIT PERMISSION TESTS

    def test_read_permission_user_cannot_edit_document(self):
        DocumentPermission.objects.create(
            document=self.document,
            shared_with=self.reader,
            permission='read',
            granted_by=self.owner
        )

        self.login_as(self.reader)

        response = self.client.get(
            reverse('edit_document', args=[self.document.id])
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
            reverse('edit_document', args=[self.document.id]),
            {'title': 'Updated Document'}
        )

        self.assertRedirects(response, reverse('document_list'))

        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Document')

    # REVOKE ACCESS TESTS

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

    # AUDIT TRAIL TESTS

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

    # CSRF TEST

    def test_revoke_access_rejects_post_without_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)

        response = csrf_client.post(
            reverse(
                'revoke_access',
                args=[self.document.id, self.reader.id]
            )
        )

        self.assertEqual(response.status_code, 403)
