import MetaTrader5 as mt5
import pandas as pd
import time
import ta  # TA-Lib o‘rniga ta kutubxonasidan foydalanamiz

# 🟢 MetaTrader 5 ga ulanamiz
if not mt5.initialize():
    print("MetaTrader 5 ga ulanishda xatolik! ❌")
    exit()

# 🔵 Foydalanuvchidan ma'lumot olish
symbol = input("Valyuta juftligini kiriting (masalan: EURUSD): ").upper()
timeframe_map = {
    "1m": mt5.TIMEFRAME_M1,
    "5m": mt5.TIMEFRAME_M5,
    "15m": mt5.TIMEFRAME_M15,
    "30m": mt5.TIMEFRAME_M30,
    "1h": mt5.TIMEFRAME_H1,
    "4h": mt5.TIMEFRAME_H4,
    "1d": mt5.TIMEFRAME_D1,
    "w1": mt5.TIMEFRAME_W1,
    "mn": mt5.TIMEFRAME_MN1
}

timeframe_input = input("Timeframe ni kiriting (1m, 5m, 15m, 30m, 1h, 4h, 1d, w1, mn): ").lower()
if timeframe_input not in timeframe_map:
    print("❌ Noto‘g‘ri timeframe kiritildi!")
    mt5.shutdown()
    exit()

timeframe = timeframe_map[timeframe_input]


# 🔴 Ma'lumotlarni olish va strategiyani qo‘llash
def get_data(symbol, timeframe, bars=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print("❌ Ma'lumotlarni olishda xatolik!")
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df


# 🔵 Strategiya: EMA + RSI
def apply_strategy(df):
    df['EMA_50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['RSI_14'] = ta.momentum.rsi(df['close'], window=14)

    latest_close = df['close'].iloc[-1]
    latest_ema = df['EMA_50'].iloc[-1]
    latest_rsi = df['RSI_14'].iloc[-1]

    if latest_close > latest_ema and latest_rsi < 30:
        return "BUY", latest_close * 1.02, latest_close * 0.98  # TP: +2%, SL: -2%
    elif latest_close < latest_ema and latest_rsi > 70:
        return "SELL", latest_close * 0.98, latest_close * 1.02  # TP: -2%, SL: +2%
    return None, None, None


# 🔵 Asosiy tsikl
while True:
    df = get_data(symbol, timeframe)
    if df is not None:
        signal, tp, sl = apply_strategy(df)

        if signal:
            print(f"\n🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 {symbol} bo‘yicha {timeframe_input} signal: {signal}")
            print(f"🎯 Take Profit: {tp:.5f}, 🛑 Stop Loss: {sl:.5f}")
        else:
            print(f"⏳ {symbol} da hali signal yo‘q...")

    time.sleep(60)  # Har 1 daqiqada yangilanadi

# 🛑 MetaTrader 5 ni yopamiz
mt5.shutdown()
