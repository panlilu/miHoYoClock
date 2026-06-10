#!/usr/bin/env python3
"""Bitcoin price display test tool — simulates the ESP32 firmware display logic.

Usage:
  python3 scripts/test_bitcoin.py              # Fetch live price
  python3 scripts/test_bitcoin.py --price 67234 # Test specific price
  python3 scripts/test_bitcoin.py --source binance
  python3 scripts/test_bitcoin.py --all         # Test all edge cases
"""
import sys
import os
import json
import urllib.request
import urllib.error
import ssl
import argparse

# ─── API fetch (same APIs as the firmware) ────────────────────────────

def fetch_gate():
    """Gate.io free API — works in China."""
    url = "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data[0]["last"])


def fetch_coinex():
    """CoinEx free API — works in China."""
    url = "https://api.coinex.com/v1/market/ticker?market=BTCUSDT"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data["data"]["ticker"]["last"])


def fetch_hotcoin():
    """Hotcoin free API — works in China."""
    url = "https://api.hotcoinfin.com/v1/market/ticker?symbol=btc_usdt"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data["ticker"][0]["ticker"][0]["last"])


def fetch_coingecko():
    """CoinGecko free API — no key needed."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data["bitcoin"]["usd"])


def fetch_coindesk():
    """CoinDesk free API — no key needed."""
    url = "https://api.coindesk.com/v1/bpi/currentprice.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data["bpi"]["USD"]["rate_float"])


def fetch_binance():
    """Binance free API — no key needed."""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data["price"])


def fetch_okx():
    """OKX free API — works in China."""
    url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data["data"][0]["last"])


def fetch_gate():
    """Gate.io free API — works in China."""
    url = "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
    return float(data[0]["last"])


FETCHERS = {
    "gate": ("Gate.io", fetch_gate),
    "coinex": ("CoinEx", fetch_coinex),
    "hotcoin": ("Hotcoin", fetch_hotcoin),
    "okx": ("OKX", fetch_okx),
    "coingecko": ("CoinGecko", fetch_coingecko),
    "coindesk": ("CoinDesk", fetch_coindesk),
    "binance": ("Binance", fetch_binance),
}

# ─── Display simulation (exact logic from IPSClock.cpp) ───────────────

# Tube ordering (matches firmware NUM_DIGITS array):
# HOURS_TENS=5, HOURS_ONES=4, MINUTES_TENS=3, MINUTES_ONES=2,
# SECONDS_TENS=1, SECONDS_ONES=0
TUBE_NAMES = ["Sec1", "Sec10", "Min1", "Min10", "Hr1", "Hr10"]
BTC_ICON = "₿"


def simulate_display(price):
    """Return list of 6 strings showing what each tube would display."""
    price_int = int(price)
    digits = [None] * 6

    if price_int >= 100000:
        # 6-digit price — no bitcoin icon
        p = price_int
        for i in range(5, -1, -1):
            digits[i] = str(p % 10)
            p //= 10
    elif price_int >= 10000:
        # 5-digit price — bitcoin icon first, then 5 digits
        digits[0] = BTC_ICON
        p = price_int
        for i in range(5, 0, -1):
            digits[i] = str(p % 10)
            p //= 10
    else:
        # 4 or fewer digits — bitcoin icon, space, then digits (right-aligned)
        digits[0] = BTC_ICON
        digits[1] = "·"  # space
        digit_idx = 5
        p = price_int
        for i in range(4):
            digits[digit_idx] = str(p % 10)
            digit_idx -= 1
            p //= 10
            if p == 0 and i < 3:
                break
        while digit_idx >= 1:
            digits[digit_idx] = "·"
            digit_idx -= 1

    return digits if digits[0] is not None else ["·"] * 6


def render_tubes(digits):
    """Render 6-tube display as ASCII art."""
    tube_w = 11
    tube_h = 7

    lines = []
    # Top border
    lines.append("  " + " ".join("┌" + "─" * (tube_w - 2) + "┐" for _ in range(6)))

    # Content lines
    for row in range(tube_h - 2):
        line = "  "
        for d in digits:
            if row == 2:
                padded = str(d).center(tube_w - 2)
            else:
                padded = " " * (tube_w - 2)
            line += "│" + padded + "│ "
        lines.append(line)

    # Bottom border
    lines.append("  " + " ".join("└" + "─" * (tube_w - 2) + "┘" for _ in range(6)))

    # Labels
    labels = ["  "]
    for name in TUBE_NAMES:
        labels.append(name.center(tube_w))
    lines.append("".join(labels))

    return "\n".join(lines)


def print_tube_ascii(digits):
    """Simple text rendering of tubes."""
    print()
    print("  ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗")
    print("  ║       ║ ║       ║ ║       ║ ║       ║ ║       ║ ║       ║")
    row = "  "
    for d in digits:
        s = str(d).center(7)
        row += f"║{s}║ "
    print(row)
    print("  ║       ║ ║       ║ ║       ║ ║       ║ ║       ║ ║       ║")
    print("  ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝")
    labels = "  "
    for name in TUBE_NAMES:
        labels += name.center(9)
    print(labels)
    print()


def test_all_cases():
    """Test all edge cases for display logic."""
    test_prices = [
        (0, "Zero / no data yet"),
        (1, "Single digit"),
        (100, "3 digits"),
        (9234, "4 digits — icon + space + 4 digits"),
        (50234, "5 digits — icon + 5 digits"),
        (67234, "5 digits — typical BTC range"),
        (99999, "5 digits — max before 6-digit"),
        (123456, "6 digits — no icon, all digits"),
    ]
    for price, description in test_prices:
        digits = simulate_display(price)
        print(f"\n── ${price:,} ({description}) ──")
        print(f"   Tubes: {' | '.join(str(d) for d in digits)}")
        print_tube_ascii(digits)


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bitcoin price display test tool")
    parser.add_argument("--price", type=float, help="Test with a specific price")
    parser.add_argument("--source", choices=list(FETCHERS), default="coingecko",
                        help="API source (default: coingecko)")
    parser.add_argument("--all", action="store_true", help="Test all edge cases")
    args = parser.parse_args()

    print("=" * 60)
    print("  miHoYo Clock — Bitcoin Display Simulator")
    print("=" * 60)

    if args.all:
        test_all_cases()
        return

    price = args.price
    if price is None:
        name, fetcher = FETCHERS[args.source]
        print(f"\n  Fetching live BTC price from {name}...")
        try:
            price = fetcher()
            print(f"  BTC/USD = ${price:,.2f}")
        except Exception as e:
            print(f"  Error fetching from {name}: {e}")
            print("  Try --source coindesk or --source binance")
            sys.exit(1)

    digits = simulate_display(price)
    print(f"\n  Price: ${price:,.2f}  →  ${int(price):,} on tubes")
    print(f"  Tubes: {' | '.join(str(d) for d in digits)}")

    # Show which image each tube loads
    for i, (d, name) in enumerate(zip(digits, TUBE_NAMES)):
        if d == BTC_ICON:
            img = "btc.bmp from /ips/btc/"
        elif d == "·":
            img = "space.bmp from /ips/cache/"
        else:
            img = f"{d}.bmp from /ips/cache/"
        print(f"    {name:>6s}: {d:>3s}  ← {img}")

    print_tube_ascii(digits)


if __name__ == "__main__":
    main()
