
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='home'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload'),
    path('documents/', views.document_list, name='document_list'),
    path('share/<int:document_id>/', views.share_document, name='share_document'),
    path('access/<int:document_id>/', views.access_document, name='access_document'),
    path('revoke/<int:document_id>/<int:user_id>/', views.revoke_access, name='revoke_access'),
    path('audit-trail/', views.audit_trail, name='audit_trail'),
    path('edit/<int:document_id>/', views.edit_document, name='edit_document'),
    path('logout/', views.user_logout, name='logout'),
]
