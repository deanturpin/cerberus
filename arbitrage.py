#!/usr/bin/env python3

import json
import requests

# Create a CryptoCompare URL from an exchange and a pair of symbols
def construct_url(exchange, from_symbol, to_symbol):
  url = "https://min-api.cryptocompare.com/data/price?"
  url += "e=" + exchange
  url += "&fsym=" + from_symbol
  url += "&tsyms=" + to_symbol
  return url

# Get the spot price for a trade
def get_spot(exchange, from_symbol, to_symbol):
      url = construct_url(exchange, from_symbol, to_symbol)
      r = requests.get(url)
      price = r.json()
      return float(price[to_symbol])

def tabulate(table):
    print()
    for row in table:
      for cell in row:
        print(cell, end="|")
      print()
    print("\n")

try:

    # Get all pairs from all exchanges
    url = 'https://min-api.cryptocompare.com/data/all/exchanges'
    r = requests.get(url)
    all_coins = r.json()

    # Exchanges we're not interested in
    exchange_blacklist = ["MonetaGo", "Lykke", "CCEDK", "Zecoex", "ExtStock",
            "EthexIndia", "Quoine", "Yacuna", "BTCE", "Cryptsy", "Abucoins",
            "WEX", "Cexio", "CCEX", "Coinsetter", "Bitlish", "BTER", "LocalBitcoins"]

    # Get all currency pairs for all exchanges
    currency_pairs = []
    for exchange in all_coins:
      if exchange not in exchange_blacklist:
        for from_symbol in all_coins[exchange]:
          for to_symbol in all_coins[exchange][from_symbol]:
            currency_pairs.append([exchange, from_symbol, to_symbol])

    entry_currency = "GBP"
    exit_currency = "EUR"

    # Extract the viable entry and exit points for our trade
    entry_points = []
    exit_points = []
    for trade in currency_pairs:
      exchange = trade[0]
      from_symbol = trade[1]
      to_symbol = trade[2]

      # Store entry points and get spot
      if to_symbol == entry_currency:
        trade.append(get_spot(exchange, from_symbol, to_symbol))
        entry_points.append(trade)

      # Store exit points and get spot
      if to_symbol == exit_currency:
        trade.append(get_spot(exchange, from_symbol, to_symbol))
        exit_points.append(trade)

    # Arbitrage - loop over each entry point
    arbitrage = []
    for trade1 in entry_points:
      exchange1 = trade1[0]
      from1 = trade1[1]
      to1 = trade1[2]
      spot1 = trade1[3]

      # And compare with each exit point
      for trade2 in exit_points:
        exchange2 = trade2[0]
        from2 = trade2[1]
        to2 = trade2[2]
        spot2 = trade2[3]

        # Store if the trades share a common currency
        if from1 == from2:
          arbitrage.append([spot2 / spot1, to1, exchange1, from1, exchange2, to2])

    # Arbitrage summary
    print("* ", len(currency_pairs), "currency pairs listed across all exchanges")
    print("* Calculating exchange rates from", entry_currency, "to", exit_currency,
            "via 1 crypto currency")
    print("* Entry points", len(entry_points))
    print("* Exit points: ", len(exit_points))
    print("* Prices fetched using the [CryptoCompare API](https://min-api.cryptocompare.com/)\n")

    # Sort and report
    print("# Triangular arbitrage")
    print("Fiat to crypto to fiat.")

    arbitrage.sort()
    arbitrage.reverse()
    tabulate(arbitrage)

    print("# Entry points")
    print("Converting fiat to crypto currency.")
    tabulate(entry_points)

    print("# Exit points")
    print("Converting crypto back to target fiat currency.")
    tabulate(exit_points)

except Exception as e:
    print("exception ", e)
