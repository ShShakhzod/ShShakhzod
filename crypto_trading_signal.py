import ccxt
import time
import pandas as pd


def get_historical_data(symbol, timeframe, limit=100):
    exchange = ccxt.binance()
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['close'] = df['close'].astype(float)  # Float ga o‘tkazamiz
    return df


def calculate_rsi(data, period=14):
    delta = data['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    data['rsi'] = rsi
    return data


def calculate_ema(data, period=50):
    data['ema'] = data['close'].ewm(span=period, adjust=False).mean()
    return data


def decide_trade(data):
    latest = data.iloc[-1]  # Eng oxirgi ma'lumotni olish

    if latest['rsi'] < 30 and latest['close'] > latest['ema']:  # RSI oversold va narx EMA dan yuqori
        take_profit = round(latest['close'] * 1.05, 2)  # 5% o'sishda chiqish
        stop_loss = round(latest['close'] * 0.97, 2)  # 3% pasayishda chiqish
        return "Buy", take_profit, stop_loss

    elif latest['rsi'] > 70 and latest['close'] < latest['ema']:  # RSI overbought va narx EMA dan past
        take_profit = round(latest['close'] * 0.95, 2)  # 5% pasayishda chiqish
        stop_loss = round(latest['close'] * 1.03, 2)  # 3% o'sishda chiqish
        return "Sell", take_profit, stop_loss

    return None, None, None


def main():
    symbol = input("Kriptovalyuta juftligini kiriting (masalan, BTC/USDT): ").strip()
    timeframe = input("Timeframe kiriting (1m, 5m, 15m, 30m, 1h, 4h, 1d): ").strip()

    print(f"Symbol: {symbol}, Timeframe: {timeframe} bo‘yicha ma'lumot olinmoqda...\n")

    while True:
        try:
            df = get_historical_data(symbol, timeframe)
            df = calculate_rsi(df)
            df = calculate_ema(df)

            action, take_profit, stop_loss = decide_trade(df)
            if action:
                latest_price = df.iloc[-1]['close']
                print(f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🔹 Narx: {latest_price:.2f} USDT")
                print(f"✅ Signal: {action}")
                print(f"🎯 Take Profit: {take_profit:.2f} USDT")
                print(f"🛑 Stop Loss: {stop_loss:.2f} USDT\n")

            time.sleep(60)  # 1 daqiqa kutish
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")


main()
