
from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DocumentPermission(models.Model):

    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('edit', 'Edit'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='permissions'
    )

    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_documents'
    )

    permission = models.CharField(
        max_length=10,
        choices=PERMISSION_CHOICES
    )

    granted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='granted_permissions'
    )

    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'shared_with')

    def __str__(self):
        return f"{self.document.title} - {self.shared_with.username} - {self.permission}"


class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('upload', 'Document Uploaded'),
        ('share', 'Document Shared'),
        ('access', 'Document Accessed'),
        ('revoke', 'Access Revoked'),
        ('edit', 'Document Edited'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )

    details = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.actor} - {self.timestamp}"


class PasswordResetRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='password_reset_requests'
    )

    username = models.CharField(max_length=150)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_password_requests'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.status}"
