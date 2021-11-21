from pyteal import *

var_admin = Bytes("admin")

def license_program():
    """
    A smart contract to store driver licenses
    """
    # sets the creator as the admin
    # only called when Txn.application_id() == Int(0)
    init_contract = Seq([
        App.globalPut(var_admin, Txn.sender()),
        Return(Int(1))
    ])

    # see if sender is the admin
    is_admin = Txn.sender() == App.globalGet(var_admin)

    # add drivers license to global storage
    id_data_global = Txn.application_args[1]
    license_data_global = Txn.application_args[2]
    add_license_global = Seq([
        Assert(is_admin),
        App.globalPut(id_data_global, license_data_global),
        Return(Int(1))
    ])

    # flow logic of the smart contract
    program = Cond(
        [Txn.application_id() == Int(0), init_contract],
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))],
        [Txn.application_args[0] == Bytes("add_license_global"), add_license_global]
    )

    return program

if __name__ == "__main__":
    print(compileTeal(license_program(), Mode.Application, version=5))
