from brownie import (
    accounts, network, config, Contract, interface)

FORKED_LOCAL_ENVIRONMENTS = ['mainnet-fork', 'mainnet-fork-dev']
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganache-local', 'mainnet-fork']

DECIMALS = 8
INITIAL_VALUE = 200000000000

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    return accounts.add(config['wallets']['from_key'])



def get_contract(contract_name):
    '''
    Function to grab contract addresses from brownie config, if defined. Otherwise, a mock version will be deployed
    Args:
        contract_name - string
    Returns:
        brownie.network.contract.ProjectContract: The most recently deployed version
    '''
    contract_type = contract_to_mock[contract_name]
    # If on development chain, get mock contract
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1] # MockV3Aggregator[-1]
    # Else on mainnet/testnet get actual contract address
    else:
        contract_address = config['networks'][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract


