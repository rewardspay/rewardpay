from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
# import json
from json2html import *

from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .forms import (
    CreateAssetForm,
    CreateWalletForm,
    SearchTransactionsForm,
    TransferFundsForm,
    CreateUserForm,
    CustomerForm,
)
from .helpers import (
    INITIAL_FUNDS,
    add_asset,
    add_standalone_account,
    add_transaction,
    add_wallet,
    cli_passphrase_for_account,
    get_wallet,
    initial_funds_sender,
    search_transactions,
    network_status,
)
from .models import Account, Asset, Wallet, WalletAccount, Netwk_status, Customer

from .decorators import unauthenticated_user, allowed_users, admin_only

def assets(request):
    """Display all the created assets."""
    assets = Asset.objects.order_by("-created")
    context = {"assets": assets}
    return render(request, "mainapp/assets.html", context)


def create_asset(request):
    """Create Algorand asset from the form data."""
    if request.method == "POST":

        if "retrieve_passphrase" in request.POST:
            creator = Account.instance_from_address(request.POST.get("creator"))
            request.POST = request.POST.copy()
            request.POST.update({"passphrase": creator.passphrase})
            form = CreateAssetForm(request.POST)
        else:

            form = CreateAssetForm(request.POST)

            if form.is_valid():

                asset_id, error_description = add_asset(form.cleaned_data)
                if error_description == "":

                    asset = form.save(commit=False)
                    asset.asset_id = asset_id
                    asset.save()

                    message = "Asset {} has been successfully created!".format(
                        form.cleaned_data["name"]
                    )
                    messages.add_message(request, messages.SUCCESS, message)
                    return redirect("assets")

                form.add_error(None, error_description)

    else:
        form = CreateAssetForm()

    context = {"form": form}

    return render(request, "mainapp/create_asset.html", context)


def create_standalone(request):
    """Create standalone account."""
    private_key, address = add_standalone_account()
    account = Account.objects.create(address=address, private_key=private_key)
    context = {"account": (address, account.passphrase)}
    return render(request, "mainapp/create_standalone.html", context)


def create_wallet(request):
    """Create wallet from the form data."""
    if request.method == "POST":

        form = CreateWalletForm(request.POST)

        if form.is_valid():

            wallet_id = add_wallet(
                form.cleaned_data["name"], form.cleaned_data["password"]
            )
            if wallet_id != "":
                Wallet.objects.create(
                    wallet_id=wallet_id,
                    name=form.cleaned_data["name"],
                    password=form.cleaned_data["password"],
                )
                message = "Wallet with name '{}' and ID '{}' has been created.".format(
                    form.cleaned_data["name"], wallet_id
                )
                messages.add_message(request, messages.SUCCESS, message)
                return redirect("wallet", wallet_id)

            form.add_error(None, "Wallet is not created!")

    else:
        form = CreateWalletForm()

    context = {"form": form}

    return render(request, "mainapp/create_wallet.html", context)


def create_wallet_account(request, wallet_id):
    """Create account in the wallet with provided ID."""
    model = Wallet.instance_from_id(wallet_id)
    wallet = get_wallet(model.name, model.password)
    address = wallet.generate_key()
    WalletAccount.objects.create(wallet=model, address=address)
    message = "Address '{}' has been created in the wallet.".format(address)
    messages.add_message(request, messages.SUCCESS, message)
    return redirect("wallet", wallet_id)

def stage1(request):
    netwk_status = Netwk_status()
    #netwk_status.stats = json.dumps(network_status(), sort_keys=True, indent=4,)
    netwk_status.stats = json2html.convert(json=network_status())
    context = {
        'Latest network status': netwk_status.stats
    }
    return render(request, "mainapp/stage1.html", {'Network': context})

def index(request):
    return render(request, "mainapp/index.html", {})

@unauthenticated_user
def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, "mainapp/Login.html", context)

@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            h_addr = add_standalone_account()

            group = Group.objects.get(name='customer')
            user.groups.add(group)

            Customer.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                algo_private_key=h_addr[0],
                algo_addr=h_addr[1],
            )

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, "mainapp/Register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
# content to show on user page
    #customer = request.user.customer.get_profile()
    #context = {'customer':customer}

    return render(request, 'mainapp/user.html', {})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES,instance=customer)
        if form.is_valid():
            form.save()

    context = {'form':form}
    return render(request, 'mainapp/account-settings.html', context)

@login_required(login_url='login')
def stage1(request):
    return render(request, "mainapp/stage1.html", {})

@login_required(login_url='login')
def std_account(request):
    """Display all the created standalone accounts."""

    accounts = Account.objects.exclude(walletaccount__isnull=False).order_by("-created")
    context = {"accounts": accounts}
    return render(request, "mainapp/std_account.html", context)


def initial_funds(request, receiver):
    """Add initial funds to provided standalone receiver account.

    Initial funds are transferred from one of the testing accounts
    created in the sandbox.
    """
    sender = initial_funds_sender()
    if sender is None:
        message = "Initial funds weren't transferred!"
        messages.add_message(request, messages.ERROR, message)
    else:
        add_transaction(
            sender,
            receiver,
            cli_passphrase_for_account(sender),
            INITIAL_FUNDS,
            "Initial funds",
        )
    return redirect("standalone-account", receiver)


def search(request):
    """Search transactions based on criteria created from the form data."""
    transactions = []
    if request.method == "POST":

        form = SearchTransactionsForm(request.POST)

        if form.is_valid():

            transactions = search_transactions(form.cleaned_data)

    else:
        form = SearchTransactionsForm()

    context = {"form": form, "transactions": transactions}

    return render(request, "mainapp/search.html", context)


def standalone_account(request, address):
    """Display information of the standalone account with provided address."""
    context = {"account": Account.instance_from_address(address)}
    return render(request, "mainapp/standalone_account.html", context)


def transfer_funds(request, sender):
    """Transfer funds from the provided sender account to the receiver from the form."""
    if request.method == "POST":

        if "retrieve_passphrase" in request.POST:
            sender_instance = Account.instance_from_address(sender)
            request.POST = request.POST.copy()
            request.POST.update({"passphrase": sender_instance.passphrase})
            form = TransferFundsForm(request.POST)
        else:

            form = TransferFundsForm(request.POST)

            if form.is_valid():

                error_field, error_description = add_transaction(
                    sender,
                    form.cleaned_data["receiver"],
                    form.cleaned_data["passphrase"],
                    form.cleaned_data["amount"],
                    form.cleaned_data["note"],
                )
                if error_field == "":
                    message = "Amount of {} microAlgos has been successfully transferred to account {}".format(
                        form.cleaned_data["amount"], form.cleaned_data["receiver"]
                    )
                    messages.add_message(request, messages.SUCCESS, message)
                    return redirect("standalone-account", sender)

                form.add_error(error_field, error_description)

    else:

        form = TransferFundsForm()

    context = {"form": form, "sender": sender}

    return render(request, "mainapp/transfer_funds.html", context)


def wallet(request, wallet_id):
    """Display information of the wallet with provided ID."""
    context = {"wallet": Wallet.instance_from_id(wallet_id)}
    return render(request, "mainapp/wallet.html", context)


def wallet_account(request, wallet_id, address):
    """Display information of the wallet account with provided address."""
    context = {
        "wallet": Wallet.instance_from_id(wallet_id),
        "account": Account.instance_from_address(address),
    }
    return render(request, "mainapp/wallet_account.html", context)


def wallets(request):
    """Display all the created wallets."""
    wallets = Wallet.objects.order_by("name")
    context = {"wallets": wallets}
    return render(request, "mainapp/wallets.html", context)
