from django.urls import path
from .views import RegisterView, DeleteAccountView

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]
