import pandas as pd
import numpy as np


def rolling_ols(A, B, window):
    mean_A = A.rolling(window).mean()
    mean_B = B.rolling(window).mean()
    cov_AB = (A * B).rolling(window).mean() - mean_A * mean_B
    var_B  = (B * B).rolling(window).mean() - mean_B ** 2
    beta  = cov_AB / var_B
    alpha = mean_A - beta * mean_B
    return alpha, beta

def run_backtest(df, fee, z_window, z_exit, z_entry):
    bt = df.copy()

    alpha, beta = rolling_ols(bt['close_x'], bt['close_y'], window=z_window)
    bt['beta'] = beta
    bt['spread'] = bt['close_x'] - beta * bt['close_y'] - alpha

    mean, std = bt['spread'].rolling(z_window).mean(), bt['spread'].rolling(z_window).std()
    bt['z_score'] = (bt['spread'] - mean) / std

    bt['signal'] = np.nan
    bt.loc[bt['z_score'] > z_entry, 'signal'] = -1
    bt.loc[bt['z_score'] < -z_entry, 'signal'] = 1
    bt.loc[bt['z_score'].abs() < z_exit, 'signal'] = 0
    bt['signal'] = bt['signal'].ffill().fillna(0)

    bt['position'] = bt['signal'].shift(1).fillna(0)

    pos = bt['position']
    changed = pos != pos.shift(1)
    bt['entry_beta'] = (bt['beta'].shift(1).where(changed).ffill()).where(pos != 0, 0.0)

    bt['return_x'] = bt['close_x'].pct_change()
    bt['return_y'] = bt['close_y'].pct_change()

    w_y = (bt['entry_beta'] * bt['close_y'].shift(1) / bt['close_x'].shift(1)).fillna(0.0)
    capital = 1.0 + w_y.abs()

    gross = bt['position'] * (bt['return_x'] - w_y * bt['return_y'])
    bt['strategy_return'] = (gross / capital).fillna(0.0)

    turnover = (bt['position'] - bt['position'].shift(1)).abs().fillna(0.0)
    bt['fee'] = turnover * fee * 2 * (1.0 + w_y.abs()) / capital
    bt['net_return'] = bt['strategy_return'] - bt['fee']
    bt['equity'] = (1.0 + bt['net_return']).cumprod()

    return bt