import secrets
from django.contrib import admin
from .models import (
    Document,
    DocumentPermission,
    AuditLog,
    PasswordResetRequest
)

from django.contrib import messages
from django.utils import timezone

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'uploaded_at')
    search_fields = ('title', 'owner__username')
    list_filter = ('uploaded_at',)


@admin.register(DocumentPermission)
class DocumentPermissionAdmin(admin.ModelAdmin):
    list_display = (
        'document',
        'shared_with',
        'permission',
        'granted_by',
        'granted_at'
    )
    search_fields = ('document__title', 'shared_with__username')
    list_filter = ('permission',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('document', 'actor', 'action', 'timestamp')
    search_fields = ('document__title', 'actor__username')
    list_filter = ('action', 'timestamp')



@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'status',
        'created_at',
        'resolved_by',
        'resolved_at'
    )

    search_fields = ('username',)

    list_filter = ('status', 'created_at')

    readonly_fields = (
        'user',
        'username',
        'created_at'
    )

    actions = ['generate_temporary_password']

    @admin.action(description='Generate temporary password for selected request')
    def generate_temporary_password(self, request, queryset):

        for reset_request in queryset:

            if reset_request.status != 'pending':
                self.message_user(
                    request,
                    f"{reset_request.username}: Request is not pending.",
                    level=messages.WARNING
                )
                continue

            if reset_request.user is None:
                reset_request.status = 'rejected'
                reset_request.resolved_by = request.user
                reset_request.resolved_at = timezone.now()
                reset_request.save()

                self.message_user(
                    request,
                    f"{reset_request.username}: Account not found. Request rejected.",
                    level=messages.WARNING
                )
                continue

            # Generate a random temporary password.
            temporary_password = secrets.token_urlsafe(12)

            # Set the new password securely using Django hashing.
            reset_request.user.set_password(temporary_password)
            reset_request.user.save(update_fields=['password'])

            # Mark the request as resolved.
            reset_request.status = 'resolved'
            reset_request.resolved_by = request.user
            reset_request.resolved_at = timezone.now()
            reset_request.save()

            # Show the temporary password only to the admin.
            self.message_user(
                request,
                f"Temporary password for {reset_request.username}: "
                f"{temporary_password}. Share it securely with the user.",
                level=messages.SUCCESS
            )

