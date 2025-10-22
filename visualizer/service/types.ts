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

export type TradeType = "BUY" | "SELL";
export type TradeStatus = "ACTIVE" | "CLOSED";

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