from scripts.helpful_scripts import get_account
from brownie import config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.000001, 'ether')


def main():
    account = get_account()

    # Get ERC20 address
    erc20_address = config['networks'][network.show_active()]['weth-token']
    if network.show_active() in ['mainnet-fork']:
        get_weth()
    
    # Get lending pool interface
    lending_pool = get_lending_pool()

    # Approve token
    approve_erc20(amount, lending_pool.address, erc20_address, account)

    # Deposit token
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {'from': account})
    tx.wait(1)
    print('--- Deposited ---')

    # Get amount able to borrow
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    # Borrow DAI
    ## Get price feed
    dai_eth_price_feed = config['networks'][network.show_active()]['dai_eth_price_feed']
    dai_eth_price = get_asset_price(dai_eth_price_feed)

    # Get how much we can borrow
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)

    # Borrow
    print(f'Borrowing {amount_dai_to_borrow}')
    dai_address = config['networks'][network.show_active()]['dai_token']
    borrow_tx = lending_pool.borrow(dai_address, Web3.toWei(amount_dai_to_borrow, 'ether'), 1, 0, account.address, {'from': account})
    borrow_tx.wait(1)
    print(f'--- Borrowed {amount_dai_to_borrow} DAI ---')

    # Repay
    repay_all(amount, lending_pool, account)


def repay_all(amount, lending_pool, account):
    dai_token_address = config['networks'][network.show_active()]['dai_token']
    approve_erc20(Web3.toWei(amount, 'ether'), lending_pool, dai_token_address, account, )

    repay_tx = lending_pool.deposit(dai_token_address, amount, account.address, 0, {'from': account})
    repay_tx.wait(1)
    print(f'--- Repaid {amount} ---')
    return repay_tx


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, 'ether')
    print(f'---- DAI/ETH Price = {converted_price}')
    return(float(converted_price))



def get_borrowable_data(lending_pool, account):
    (total_collateral_eth, 
    total_debt_eth, 
    available_borrow_eth, 
    current_liquidation_threshold, 
    ltv, 
    health_factor) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, 'ether')
    total_collateral_eth = Web3.fromWei(total_collateral_eth, 'ether')
    total_debt_eth = Web3.fromWei(total_debt_eth, 'ether')
    print(f'You have {total_debt_eth} ETH deposited.')
    print(f'You have {total_debt_eth} of ETH borrowed.')
    print(f'You can borrow {available_borrow_eth} worth of ETH.')
    return (float(available_borrow_eth), float(total_debt_eth))

    

def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_address_provider']
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()  
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print('--- Approving ERC20 token... ---')
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {'from': account})
    tx.wait(1)
    print('--- Approved ERC20 token ---')
    return tx



