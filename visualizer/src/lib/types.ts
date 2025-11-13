/**
 * Defines TypeScript interfaces for data models used in the trading application,
 * inferred from the Python TradeEngine's data structures.
 */

export interface Candle {
  datetime: string; // ISO 8601 string (e.g., "2025-10-20T10:00:00")
  High: number;
  Low: number;
  Close: number;
  Open: number;
  Volume: number;
}

export type TradeType = 'BUY' | 'SELL';
export type TradeStatus = 'ACTIVE' | 'CLOSED';

export interface BaseTrade {
  entry_id: string;
  ticker: string;
  entry_datetime: string; // ISO 8601 string
  entry_price: number;
  type: TradeType;
  stop_loss: number;
  take_profit?: number | null; // Optional, can be null if not set
  size_units: number;
  margin_used: number;
  status: TradeStatus;
}

export interface ActiveTrade extends BaseTrade {
  unrealised_pnl?: number; // Optional, only present if requested (e.g., include_pnl=True)
}

export interface ClosedTrade extends BaseTrade {
  closed_datetime: string; // ISO 8601 string
  closed_price: number;
  profit: number;
  reason?: string; // Reason for closure (e.g., "SL hit", "TP hit", "Manual Close")
}

export interface EquityHistoryEntry {
  datetime: string; // ISO 8601 string
  equity: number;
  current_balance: number;
  unrealised_pnl: number;
  max_equity_so_far: number;
  min_equity_so_far: number;
}

export interface TradeEngineOptions {
  start_date: string;
  end_date: string;
  interval: string;
  ticker: string;
  save_location_base: string;
  ema_short: number;
  ema_long: number;
  window: number;
  threshold_bb: number;
  threshold_adx: number;
  tolerance: number;
  loops: number;
  results_file_dir: string;
}

export interface TradeSummaryResponse {
  options: TradeEngineOptions;
  active_trades: ActiveTrade[];
  closed_trades: ClosedTrade[];
  final_balance: number;
}

export interface DailyPayloadCandle {
  high: number;
  close: number;
  open: number;
  low: number;
  volume: number;
}

export interface DailyPayloadConditions {
  trend_status: string;
  ema_crossover: string;
  candles_since_consolidation: number;
  candles_since_crossover: number;
  consolidation_maxima: number;
  consolidation_minima: number;
}

export interface DailyPayloadEntry {
  payload: {
    strategy_type: string;
    datetime: string;
    interval: string;
    candle: DailyPayloadCandle;
    ticker: string;
    conditions: DailyPayloadConditions;
  };
  decision: {
    action_taken: string;
    reason: string;
    entry?: {
      // Optional, only present for BUY/SELL_ENTRY
      entry_price: number;
      type: TradeType;
      stop_loss: number;
      ticker: string;
      datetime: string;
    };
  };
}

export interface DailyPayloadsResponse {
  options: TradeEngineOptions;
  payloads: DailyPayloadEntry[];
}

export interface RunFilter {
  run_name: string;
  backtest_start_date?: string; // Optional, as it might not always be present
  dates: string[]; // YYYY-MM-DD format
}

export interface IntervalFilter {
  interval: string;
  runs: RunFilter[];
}

export interface TickerFilter {
  ticker: string;
  intervals: IntervalFilter[];
}

export type FiltersResponse = TickerFilter[];

export interface IndicatorEntry {
  datetime: string;
  value: number;
}

export type IndicatorsResponse = Record<string, IndicatorEntry[]>;
