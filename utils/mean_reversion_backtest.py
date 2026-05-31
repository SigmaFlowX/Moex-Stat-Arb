import pandas as pd
import numpy as np
import optuna
from dateutil.relativedelta import relativedelta


def generate_walk_forward_windows(df, train_months=6, test_months=3):
    windows = []
    start_date = df['timestamp'].min()
    end_date = df['timestamp'].max()

    current_start = start_date

    while True:
        train_start = current_start
        train_end = train_start + relativedelta(months=train_months)
        test_start = train_end
        test_end = test_start + relativedelta(months=test_months)

        if test_end > end_date:
            break

        windows.append((train_start, train_end, test_start, test_end))
        current_start = train_start + relativedelta(months=test_months)

    return windows

def rolling_ols(A, B, window):
    mean_A = A.rolling(window).mean()
    mean_B = B.rolling(window).mean()
    cov_AB = (A * B).rolling(window).mean() - mean_A * mean_B
    var_B  = (B * B).rolling(window).mean() - mean_B ** 2
    beta  = cov_AB / var_B
    alpha = mean_A - beta * mean_B
    return alpha, beta

def run_backtest(df, z_window, z_exit, z_entry, fee=0.02/100):
    bt = df.copy()
    bt = bt[['timestamp', 'close_x','close_y']].dropna()

    alpha, beta = rolling_ols(bt['close_x'], bt['close_y'], window=z_window)
    bt['beta'] = beta.shift(1)
    bt['alpha'] = alpha.shift(1)

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

    bt['return_x'] = bt['close_x'].pct_change(fill_method=None)
    bt['return_y'] = bt['close_y'].pct_change(fill_method=None)

    w_y = (bt['entry_beta'] * bt['close_y'].shift(1) / bt['close_x'].shift(1)).fillna(0.0)
    capital = 1.0 + w_y.abs()

    gross = bt['position'] * (bt['return_x'] - w_y * bt['return_y'])
    bt['strategy_return'] = (gross / capital).fillna(0.0)

    turnover = (bt['position'] - bt['position'].shift(1)).abs().fillna(0.0)
    bt['fee'] = turnover * fee * 2 * (1.0 + w_y.abs()) / capital
    bt['net_return'] = bt['strategy_return'] - bt['fee']
    bt['equity'] = (1.0 + bt['net_return']).cumprod()

    return bt


def objective(trial, df, fee):
    df = df.copy()

    z_entry = trial.suggest_float('z_entry', 0.0, 5)
    z_exit = trial.suggest_float('z_exit', 0.0, z_entry)
    z_window = trial.suggest_int('z_window', 0, 100)

    bt = run_backtest(df, z_window, z_exit, z_entry, fee)
    total_return = bt.iloc[-1]['equity'] - 1

    return total_return


def optimize(df, fee, trials=200):
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, df, fee), n_trials=trials, n_jobs=-1)

    return study.best_params

def walk_forward_optimization(df, fee, train_month, test_month):
    df = df.copy()

    windows = generate_walk_forward_windows(df, train_month, test_month)

