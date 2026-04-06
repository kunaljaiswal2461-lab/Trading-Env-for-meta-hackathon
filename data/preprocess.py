import pandas as pd, numpy as np
from ta.momentum import RSIIndicator

def load_and_preprocess(csv_path, train_ratio=0.80):
    df = pd.read_csv(csv_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['sma5']       = df['close'].rolling(5).mean()
    df['sma20']      = df['close'].rolling(20).mean()
    df['sma5_dist']  = (df['close'] - df['sma5']) / df['sma5']
    df['sma20_dist'] = (df['close'] - df['sma20']) / df['sma20']
    df['rsi']        = RSIIndicator(df['close'], 14).rsi() / 100.0
    df['norm_volume'] = (df['volume'] / 
                         df['volume'].rolling(20).mean()).clip(0, 5)
    df['volatility'] = df['log_return'].rolling(10).std()
    
    FEAT = ['log_return', 'sma5_dist', 'sma20_dist',
            'rsi', 'norm_volume', 'volatility']
    df = df.dropna(subset=FEAT).reset_index(drop=True)
    out = df[['date', 'close'] + FEAT].copy()
    
    # CRITICAL: time-based split - NEVER random
    idx = int(len(out) * train_ratio)
    return out.iloc[:idx].reset_index(drop=True), \
           out.iloc[idx:].reset_index(drop=True)

if __name__ == '__main__':
    train, test = load_and_preprocess('data/spy_prices.csv')
    print(f'Train: {len(train)} rows | Test: {len(test)} rows')
    print(train.describe())
    
    # Internal Verifications requested by END CONDITION
    assert len(train.columns) == 8, f"Output columns: {len(train.columns)}"
    assert train.isna().sum().sum() == 0, "NaNs found in training output!"
    assert test.isna().sum().sum() == 0, "NaNs found in test output!"
    assert train['date'].max() < test['date'].min(), "Time leak detected!"
    print("OK: True")
