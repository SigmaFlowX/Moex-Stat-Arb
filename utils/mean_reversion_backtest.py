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
