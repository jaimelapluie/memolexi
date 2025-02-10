from django.urls import path
from .views import RegisterView, DeleteAccountView, ChangePasswordView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/delete-account/", DeleteAccountView.as_view(), name="delete_account"),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    path('api/reset-password/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
