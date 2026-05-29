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

