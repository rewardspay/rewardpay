from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("std-account/", views.std_account, name="std-account"),
    path("create-standalone/", views.create_standalone, name="create-standalone"),
    path(
        "standalone-account/<str:address>/",
        views.standalone_account,
        name="standalone-account",
    ),
    path("initial-funds/<str:receiver>/", views.initial_funds, name="initial-funds"),
    path("transfer-funds/<str:sender>/", views.transfer_funds, name="transfer-funds"),
    path("wallets/", views.wallets, name="wallets"),
    path("create-wallet/", views.create_wallet, name="create-wallet"),
    path("wallet/<str:wallet_id>/", views.wallet, name="wallet"),
    path(
        "create-wallet-account/<str:wallet_id>/",
        views.create_wallet_account,
        name="create-wallet-account",
    ),
    path(
        "wallet-account/<str:wallet_id>/<str:address>/",
        views.wallet_account,
        name="wallet-account",
    ),
    path("assets/", views.assets, name="assets"),
    path("create-asset/", views.create_asset, name="create-asset"),
    path("search/", views.search, name="search"),
    path("Login/", views.loginUser, name="login"),
    path("Logout/", views.logoutUser, name="logout"),
    path("Register/", views.register, name="register"),
    path("user/", views.userPage, name="user-page"),
    path("stage1/", views.stage1, name="stage1"),
    path("account/", views.accountSettings, name="account"),
    path("idCheck/", views.idCheck, name="idCheck"),
    path("smartCrt/", views.smartContract, name="smartCrt"),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="mainapp/password_reset.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="mainapp/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="mainapp/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="mainapp/password_reset_done.html"),
         name="password_reset_complete"),
]
