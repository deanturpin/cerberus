#!/usr/bin/env python3

import json
import requests
from collections import deque

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
  # Only print the top rows
  index = 0
  print()
  for row in table:
    for cell in row:
      print(cell, end="|")
    print()
    index += 1
    if index >= 15:
        break
  print("\n")

try:

  # Get entry and exit currencies
  f = open("currencies.txt")
  currencies = deque(f.read().split())

  # Get all pairs from all exchanges
  url = 'https://min-api.cryptocompare.com/data/all/exchanges'
  r = requests.get(url)
  all_coins = r.json()

  # Exchanges we're not interested in
  f = open("blacklist.txt")
  blacklist = deque(f.read().split())

  f = open("whitelist.txt")
  whitelist = deque(f.read().split())

  # Get all currency pairs for all exchanges
  currency_pairs = []
  for exchange in all_coins:
    if exchange in whitelist:
      for from_symbol in all_coins[exchange]:
        for to_symbol in all_coins[exchange][from_symbol]:
          currency_pairs.append([exchange, from_symbol, to_symbol])

  print("*", len(currency_pairs), "currency pairs listed across all exchanges")
  print("*", len(whitelist), "whitelisted exchanges")
  print("* Prices fetched using the",
    "[CryptoCompare API](https://min-api.cryptocompare.com/)\n")

  # Calculate arbitrage opportunities each target currency
  for c in currencies:

    entry_currency = c
    exit_currency = c

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

    # Arbitrage summary - sort and report
    print("#", c, flush=True)
    print("* Entry points", len(entry_points))
    print("* Permutations", len(arbitrage))
    arbitrage.sort()
    arbitrage.reverse()
    tabulate(arbitrage)

except Exception as e:
    print("exception ", e)
