import base64

from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import PaymentTxn
from algosdk.future import transaction
import os
from pathlib import Path


# Sandbox
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)

# Setup Admin account to run the smart contract
admin_addr = "YOX4A65TCVLYQM5R5MQNAL3XYSIF67J7WEH4RBUXWTMY62HJMXVT4VT2HQ"
admin_private_key = "FIIyiQSlIsE3D/ScHilDUAkD6vcmJ5gUZcGKM6ahPeXDr8B7sxVXiDOx6yDQL3fEkF99P7EPyIaXtNmPaOll6w=="

account_info = algod_client.account_info(admin_addr)
#print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

# Check the number of smart contract apps created under the account
app_count = len(account_info.get('created-apps'))

# Check the balance of the account
account_bal = account_info.get('amount')

# Declare application state storage (immutable)
local_ints = 0
local_bytes = 1
global_ints = 1
global_bytes = 10
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)

# Set Path to the Teal files
BASE_DIR = Path(__file__).resolve().parent.parent
sm_contract_file = os.path.join(BASE_DIR,'mainapp/assets/license_smart_contract.teal')
clr_program_file = os.path.join(BASE_DIR,'mainapp/assets/clear_program.teal')

# Create new application
def create_app(client, private_key, 
               approval_program, clear_program, 
               global_schema, local_schema): 
    print("Creating new app")

    # Define sender as creator
    sender = account.address_from_private_key(private_key)

    # Declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # Get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    # Create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender, params, on_complete, 
        approval_program, clear_program, 
        global_schema, local_schema)

    # Sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # Send transaction
    client.send_transactions([signed_txn])

    # Await confirmation
    wait_for_confirmation(client, tx_id)

    # Display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id: ", app_id)

    return app_id

# Call application
def call_app(client, private_key, index, app_args, accounts): 
    # Declare sender
    sender = account.address_from_private_key(private_key)

    # Get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    # Create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args, accounts)

    # Sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # Send transaction
    client.send_transactions([signed_txn])

    # Await confirmation
    wait_for_confirmation(client, tx_id)

    # Display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Called app-id: ", transaction_response['txn']['txn']['apid'])

# Utility function for waiting on a transaction confirmation
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

# Add license to global state with respective id
def add_license(app_id, license_id, license_info):
    app_args = [b'add_license_global', bytes(license_id, 'utf-8'),bytes(license_info, 'utf-8')]
    call_app(algod_client, admin_private_key, app_id, app_args, [admin_addr])
    print("license for id #{} added to global state".format(license_id) + "\n")

# Retrieve license information with license id from global state
def retrieve_license(app_id, license_id):
    results = algod_client.account_info(admin_addr)
    apps_created = results['created-apps']
    result_found = False
    for app in apps_created:
        if app['id'] == app_id:
            for kv in app['params']['global-state']:
                key = base64.b64decode(kv['key'])
                value = kv['value']
                if key.decode("utf-8") == license_id:
                    result_found = True
                    value['bytes'] = base64.b64decode(value['bytes'])
                    #print("Drivers license information for id #{}:".format(key.decode("utf-8")))
                    retrieved_id = "Drivers license information for id #{}:".format(key.decode("utf-8"))
                    #print(value['bytes'].decode("utf-8") + "\n")
                    retrieved_detail = value['bytes'].decode("utf-8")
                    return retrieved_id, retrieved_detail
            if(result_found == False):
                print("License id not found!" + "\n")
                return None

# Helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode('utf-8'))
    return base64.b64decode(compile_response['result'])

def smart_crt(license_id, license_detail):
    if account_bal > 0 and app_count < 10:
        print("Account balance: ", account_bal)
        print("Number of created global apps: ", app_count)

        # Read the smart contract source files
        smart_contract_file = open(sm_contract_file, "rb")
        smart_contract_source = smart_contract_file.read()
        smart_contract_program = compile_program(algod_client, smart_contract_source)

        clear_program_file = open(clr_program_file, "rb")
        clear_program_source = clear_program_file.read()
        clear_program = compile_program(algod_client, clear_program_source)

        ############################################################################
        # Deploying smart contract application
        ############################################################################

        print("--------------------------------------")
        print("Deploying smart contract application:")
        print("--------------------------------------" +  "\n")

        app_id = create_app(algod_client,
                            admin_private_key,
                            smart_contract_program,
                            clear_program,
                            global_schema,
                            local_schema)

        ############################################################################
        # Adding licenses to global storage
        ############################################################################

        print("-------------------")
        #print("Example use cases:")
        print("-------------------" +  "\n")

        # Add license info with license id
        print("--- Adding licenses to global state --- " + "\n")
        add_license(app_id, license_id,license_detail)

    #    add_license(app_id, "19112021-2",
    #        "Name: Jane Doe, DoB: 10/03/1975, Expiry Date: 01/12/2023, Address: 999 Spencer St")

        # Retrieve licenses from license id
        print("--- Retrieving licenses from global state ---" + "\n")
        #sm_crt = retrieve_license(app_id, license_id)

    #    retrieve_license(app_id, "19112021-2")
        return app_id

    else:
        if account_bal <= 0:
            print("Insufficient balance! Fund the account first!")
            return None
        if app_count >= 10:
            print("Maximum number of global apps reached!")
            return None
