import numpy as np
import pandas as pd
import yfinance as yf
import ta
import mplfinance as mpf
import logging

# ---------------------------
# flip / run helpers
# ---------------------------

def _extract_runs_bool(arr):
    """Return list of (bool_value, length) for boolean 1D array-like."""
    arr = np.asarray(arr, dtype=bool)
    if arr.size == 0:
        return []
    runs = []
    curr = arr[0]
    length = 1
    for x in arr[1:]:
        if x == curr:
            length += 1
        else:
            runs.append((bool(curr), length))
            curr = x
            length = 1
    runs.append((bool(curr), length))
    return runs

def merge_runs(runs_list):
    """Merge adjacent runs with same boolean. Input: list[(bool,int)]. Output: list[(bool,int)]."""
    if not runs_list:
        return []
    merged = []
    current_bool, current_len = runs_list[0]
    for b, ln in runs_list[1:]:
        if b == current_bool:
            current_len += ln
        else:
            merged.append((current_bool, current_len))
            current_bool, current_len = b, ln
    merged.append((current_bool, current_len))
    return merged

def avg_gap_fill(runs_list, window, threshold):
    """
    One pass: flip small sandwiched gaps based on run lengths.
    - runs_list: list[(bool,length)]
    - window: scale used when comparing
    - threshold: multiplicative threshold vs neighbor mean
    Returns a new list[(bool,length)] (doesn't mutate input).
    """
    if not runs_list or len(runs_list) < 3:
        return runs_list.copy()
    result = runs_list.copy()
    # We'll accumulate changes in new_runs so neighbor checks refer to original runs in this pass.
    new_runs = result.copy()
    for i in range(1, len(result) - 1):
        b, v = result[i]               # middle run
        prev_b, prev_v = result[i - 1]
        next_b, next_v = result[i + 1]
        # False between two True -> maybe flip to True
        if (not b) and prev_b and next_b:
            mean_neighbor = (prev_v + next_v) / 2.0
            if (v < max(1, window * 0.6)) and (v < mean_neighbor * threshold):
                new_runs[i] = (True, v)
        # True between two False -> maybe flip to False
        if b and (not prev_b) and (not next_b):
            mean_neighbor = (prev_v + next_v) / 2.0
            if (v < max(1, window * 0.25)) and (v < mean_neighbor * threshold):
                new_runs[i] = (False, v)
    return merge_runs(new_runs)

def flip_small_segments(vals, options=None):
    """
    vals: 1D array-like boolean-ish (True/False)
    returns: numpy boolean array after iterating avg_gap_fill `loops` times
    """
    if options is None:
        options = {}
    
    loops = int(options.get('loops', 2))
    window = int(options.get('window', 25))
    threshold = float(options.get('segment_threshold', 0.5))

    vals = np.asarray(vals, dtype=bool)
    if vals.size == 0:
        return np.array([], dtype=bool)
    runs = _extract_runs_bool(vals)
    if not runs or len(runs) < 3:
        return runs
    for _ in range(int(max(1, loops))):
        runs = avg_gap_fill(runs, window, threshold)

    return runs

def expand_segments(runs):
    # expand runs back to boolean array
    out = np.empty(sum(length for _, length in runs), dtype=bool)
    idx = 0
    for b, length in runs:
        out[idx: idx + length] = b
        idx += length
    return out

# ---------------------------
# Replace subarrays
# ---------------------------

def replace_true_subarrays(b, f, agg_func):
    """
    Replace subarrays in f where boolean mask b is True with agg_func applied to each True run.
    - b: 1D boolean array-like
    - f: 1D numeric array-like (same length as b)
    - agg_func: function that accepts a 1D numpy array and returns a scalar
    Returns: numpy array same length as f
    """
    b = np.asarray(b, dtype=bool)
    f = np.asarray(f)
    if b.shape[0] != f.shape[0]:
        raise ValueError("b and f must be same length")
    if f.size == 0:
        return f.copy()
    out = f.copy()
    # identify starts/ends of True runs
    diff = np.diff(b.astype(int))
    starts = np.where(diff == 1)[0] + 1
    ends = np.where(diff == -1)[0] + 1
    if b[0]:
        starts = np.r_[0, starts]
    if b[-1]:
        ends = np.r_[ends, f.size]
    # sanity
    if starts.size != ends.size:
        # unlikely but handle gracefully
        min_len = min(starts.size, ends.size)
        starts = starts[:min_len]
        ends = ends[:min_len]
    for s, e in zip(starts, ends):
        if s >= e:
            continue
        subset = f[s:e]
        if subset.size == 0:
            continue
        replacement = agg_func(subset)
        # ensure scalar
        if np.ndim(replacement) != 0:
            # try to reduce to scalar
            replacement = np.asarray(replacement).ravel()[0]
        out[s:e] = replacement
    return out

# ---------------------------
# yfinance helper (fetch_data)
# ---------------------------

def fetch_data(ticker, interval, specific_date, days=1, tz='Africa/Johannesburg', tz_localize=False):
    """
    Download ticker via yfinance for [specific_date, specific_date + days)
    Returns a cleaned DataFrame (OHLCV) with numeric columns and index in tz or naive depending on tz_localize.
    """
    start = pd.to_datetime(specific_date)
    end = start + pd.Timedelta(days=days)
    data = yf.download(ticker, interval=interval, start=start, end=end, progress=False,auto_adjust=False)

    if data.empty:
        return data

    data.columns = data.columns.droplevel('Ticker')

    # coerce columns to numeric where possible
    for col in list(data.columns):
        try:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        except Exception:
            # keep non-numeric columns (rare) but ignore
            pass

    # drop all rows where Close is NaN or all OHLC are NaN
    data = data.dropna(how='all', subset=['Open', 'High', 'Low', 'Close'] if set(['Open','High','Low','Close']).issubset(data.columns) else data.columns)

    # print(data.iloc[0])
    # timezone handling: yfinance returns tz-aware datetimes for intraday; keep consistency
    if tz_localize:
        try:
            # if tz-aware already, convert
            data.index = pd.to_datetime(data.index)
            if data.index.tz is None:
                data.index = data.index.tz_localize('UTC').tz_convert(tz)
            else:
                data.index = data.index.tz_convert(tz)
            # optionally make naive (comment out if you prefer tz-aware)
            data.index = data.index.tz_localize(None)
        except Exception:
            # if conversion fails, leave as-is
            pass
    # print(data.iloc[0])
    return data

# ---------------------------
# compute_data (minor sanity)
# ---------------------------

def compute_data(data, options=None):
    if options is None:
        options = {}
    ema_short_window = int(options.get('ema_short', 9))
    ema_long_window = int(options.get('ema_long', 21))
    window = int(options.get('window', 25))
    threshold_bb = float(options.get('threshold_bb', 0.5))
    threshold_adx = float(options.get('threshold_adx', 25))
    tolerance = float(options.get('tolerance', 0.6))

    # ensure Close exists
    if 'Close' not in data.columns:
        raise ValueError("'Close' column required in data")

    computed_data = pd.DataFrame(index=data.index)
    computed_data['SMA'] = data['Close'].rolling(window=window, min_periods=1).mean()
    computed_data['StdDev'] = data['Close'].rolling(window=window, min_periods=1).std().fillna(0)
    computed_data['BB_Upper'] = computed_data['SMA'] + (2 * computed_data['StdDev'])
    computed_data['BB_Lower'] = computed_data['SMA'] - (2 * computed_data['StdDev'])
    computed_data['BB_Width'] = computed_data['BB_Upper'] - computed_data['BB_Lower']

    # ADX from ta library: use typical recommended args (will return NaN for first rows)
    computed_data['ADX'] = ta.trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=window)

    computed_data['EMA_short'] = ta.trend.EMAIndicator(close=data['Close'], window=ema_short_window).ema_indicator()
    computed_data['EMA_long'] = ta.trend.EMAIndicator(close=data['Close'], window=ema_long_window).ema_indicator()

    prev_short = computed_data['EMA_short'].shift(1)
    prev_long = computed_data['EMA_long'].shift(1)
    computed_data['EMA_cross'] = 0
    bullish_cross = (computed_data['EMA_short'] > computed_data['EMA_long']) & (prev_short <= prev_long)
    bearish_cross = (computed_data['EMA_short'] < computed_data['EMA_long']) & (prev_short >= prev_long)
    computed_data.loc[bullish_cross, 'EMA_cross'] = 1
    computed_data.loc[bearish_cross, 'EMA_cross'] = -1

    computed_data['BB_Width_Avg'] = computed_data['BB_Width'].rolling(window=window, min_periods=1).mean()
    computed_data['Consolidation_orig'] = (computed_data['BB_Width'] < computed_data['BB_Width_Avg'] * threshold_bb) & (computed_data['ADX'] < threshold_adx)

    seq1 = computed_data['BB_Width']
    seq2 = computed_data['BB_Width_Avg'] * threshold_bb
    computed_data['Consolidation'] = ((np.abs(seq1 - seq2) / np.maximum(np.abs(seq1), np.abs(seq2))).fillna(0) <= tolerance) & (computed_data['ADX'] < threshold_adx)

    scatter_series_bull = pd.Series(np.nan, index=computed_data.index)
    scatter_series_bull[computed_data['EMA_cross'] == 1] = data['Close'][computed_data['EMA_cross'] == 1]
    scatter_series_bear = pd.Series(np.nan, index=computed_data.index)
    scatter_series_bear[computed_data['EMA_cross'] == -1] = data['Close'][computed_data['EMA_cross'] == -1]
    computed_data['Crossover_bull'] = scatter_series_bull
    computed_data['Crossover_bear'] = scatter_series_bear
    
    return computed_data

# ---------------------------
# plot improvements
# ---------------------------

def plot(data, computed_data, options=None):
    if options is None:
        options = {}
    threshold_adx = float(options.get('threshold_adx', 25))
    bb_width_dev_tolerance = float(options.get('tolerance', 0.6))
    threshold_bb = float(options.get('threshold_bb', 0.65))
    window = int(options.get('window', 25))
    ticker = options.get('ticker', getattr(data, 'name', 'ticker'))
    interval = options.get('interval', '5m')
    figsize = options.get('figsize', (15, 8))
    style = options.get('style', 'yahoo')
    row_index = options.get('row_index', 0)

    # compute consolidated boolean mask (align with data.index)
    segments = flip_small_segments(computed_data['Consolidation'].values, options=options)
    consolidation_mask = expand_segments(segments)
    consolidation_mask = np.asarray(consolidation_mask, dtype=bool)
    # convert to Series with same index for mplfinance fill_between alignment
    consolidation_series = consolidation_mask

    # y1 = min per consolidated region, y2 = max per consolidated region (aligned Series)
    y1 = replace_true_subarrays(consolidation_series, data['Low'].values, agg_func=np.min)
    y2 = replace_true_subarrays(consolidation_series, data['High'].values, agg_func=np.max)

    fill_between_args = dict(
        y1=y1,
        y2=y2,
        where=consolidation_series,
        color='purple',
        alpha=0.2
    )

    seq1 = computed_data['BB_Width']
    seq2 = computed_data['BB_Width_Avg'] * threshold_bb
    # treeee as Series aligned too
    treeee = (np.abs(seq1 - seq2) / np.maximum(np.abs(seq1), np.abs(seq2))).fillna(0)


    addplots = [
        mpf.make_addplot(computed_data['BB_Upper']),
        mpf.make_addplot(computed_data['BB_Lower']),
        mpf.make_addplot(computed_data['BB_Width'], panel=1),
        mpf.make_addplot(computed_data['BB_Width_Avg'] * threshold_bb, panel=1),
        mpf.make_addplot(computed_data['ADX'], panel=2),
        mpf.make_addplot(pd.Series([threshold_adx] * len(computed_data['ADX']), index=computed_data.index), panel=2, linestyle='--'),
        mpf.make_addplot(treeee, panel=3),
        mpf.make_addplot(pd.Series([bb_width_dev_tolerance] * len(treeee), index=treeee.index), panel=3, linestyle='--'),
        mpf.make_addplot(computed_data['EMA_short']),
        mpf.make_addplot(computed_data['EMA_long']),
        mpf.make_addplot(computed_data['Crossover_bull'], type='scatter', markersize=80, marker='^'),
        mpf.make_addplot(computed_data['Crossover_bear'], type='scatter', markersize=80, marker='v'),
    ]

    mpf.plot(
        data,
        type='candle',
        title=f'{ticker} {interval} Consolidation Zones with EMA Crossovers (window={window})',
        style=style,
        figsize=figsize,
        addplot=addplots,
        panel_ratios=(6, 1, 1, 1),
        vlines=dict(
            vlines=[data.index[row_index]],
            colors='pink',
            linewidths=1,
            linestyle='--'
        ),
        fill_between=fill_between_args,
        volume=False,
        xrotation=45,
    )

def candles_since_last_consolidation(segments):
    """
    Returns the number of candles since the last consolidation segment (True).
    If currently in consolidation, returns 0.
    If no consolidation exists yet, returns total number of candles.
    """
    # Find last consolidation
    last_true_index = None
    for i in reversed(range(len(segments))):
        if segments[i][0]:  # True segment found
            last_true_index = i
            break

    if last_true_index is None:
        # No consolidation at all → all candles count
        return sum(length for _, length in segments)
    elif last_true_index == len(segments) - 1:
        # Last segment is consolidation → 0 candles since last consolidation
        return 0
    else:
        # Sum lengths of segments *after* last True
        return sum(length for _, length in segments[last_true_index + 1:])

def last_true_indices(segments):
    """
    Returns (start_index, end_index) of the last True segment
    in the expanded array.
    """
    cumulative_index = 0
    last_true_start = None
    last_true_end = None

    for is_true, length in segments:
        if is_true:
            last_true_start = cumulative_index
            last_true_end = cumulative_index + length
        cumulative_index += length

    if last_true_start is None:
        return (None, None)  # no True segment
    else:
        return (last_true_start, last_true_end - 1)



def generate_payload(data, computed_data, options=None):
    ctx_data = data
    ctx_comp_data = computed_data
    row_data = data.iloc[-1]
    row_computed = computed_data.iloc[-1]

    logging.info(f"Generating payload for candle at {row_data.name}. ctx_data length: {len(ctx_data)}. row_data: {row_data.to_dict()}")

    trend_status = "consolidating"
    crosses = ctx_comp_data[ctx_comp_data['EMA_cross'] != 0]
    if not crosses.empty and not row_computed['Consolidation']:
        latest_cross_value = crosses.iloc[-1]['EMA_cross']
        trend_status = "bullish" if latest_cross_value == 1 else "bearish"
    elif crosses.empty and not row_computed['Consolidation']:
        trend_status = "unknown"
        
    ema_crossover = (
        "bullish" if row_computed['EMA_cross'] == 1
        else "bearish" if row_computed['EMA_cross'] == -1
        else "none"
    )

    segments = flip_small_segments(ctx_comp_data['Consolidation'].values, options=options)
    start_idx, end_idx = last_true_indices(segments)


    if start_idx is None or start_idx == end_idx:
        maxima = ctx_data["High"].max() if not ctx_data.empty else row_data["High"]
        minima = ctx_data["Low"].min() if not ctx_data.empty else row_data["Low"]
    else:
        maxima = ctx_data["High"].iloc[start_idx:end_idx].max()
        minima = ctx_data["Low"].iloc[start_idx:end_idx].min()

    if crosses.empty:
        candles_since_crossover = len(ctx_comp_data)
    else:
        last_cross_index = ctx_comp_data.index.get_loc(crosses.index[-1])
        candles_since_crossover = len(ctx_comp_data) - 1 - last_cross_index

    row_datetime = row_data.name
    if hasattr(row_datetime, "tzinfo") and row_datetime.tzinfo is not None:
        row_datetime_str = row_datetime.isoformat()
    else:
        row_datetime_str = pd.Timestamp(row_datetime, tz="UTC").isoformat()

    payload = {
        "strategy_type": "consolidation_breakout",
        "datetime": row_datetime_str,
        "interval": options.get("interval", "5m"),
        "candle": {
            "high": round(float(row_data["High"]), 5),
            "close": round(float(row_data["Close"]), 5),
            "open": round(float(row_data["Open"]), 5),
            "low": round(float(row_data["Low"]), 5),
            "volume": round(float(row_data["Volume"]), 5)
        },
        "ticker": options.get("ticker", "UNKNOWN"),
        "conditions": {
            "trend_status": trend_status,
            "ema_crossover": ema_crossover,
            "candles_since_consolidation": 0 if row_computed['Consolidation'] else candles_since_last_consolidation(segments),
            "candles_since_crossover": candles_since_crossover,
            "consolidation_maxima": round(maxima, 5),
            "consolidation_minima": round(minima, 5),
        }
    }

    return payload
