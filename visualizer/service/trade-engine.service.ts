import { 
    Candle, 
    ActiveTrade, 
    ClosedTrade,
    EquityHistoryEntry,
    TradeSummaryResponse,
    DailyPayloadsResponse,
    FiltersResponse,
} from './types';

export class TradeEngineService {
    private baseUrl: string;

    /**
     * Initializes the TradeEngineService.
     * @param baseUrl The base URL for the TradeEngine API. Defaults to 'http://127.0.0.1:5000'.
     */
    constructor(baseUrl: string = 'http://127.0.0.1:5000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Generic helper to fetch data from the API.
     * @param endpoint The API endpoint relative to the base URL.
     * @returns A Promise resolving to the fetched data of type T.
     * @throws An error if the network request fails or the response status is not OK.
     * @param params Optional query parameters to append to the URL.
     */
    private async fetchData<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
        let url = `${this.baseUrl}${endpoint}`;
        if (params) {
            url += `?${new URLSearchParams(params).toString()}`;
        }
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
            return await response.json() as T;
        } catch (error) {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error; // Re-throw to allow caller to handle
        }
    }

    /**
     * Fetches a structured list of all available backtest runs.
     * Corresponds to Python API endpoint `GET /filters`.
     * @returns Promise<FiltersResponse> A hierarchical view of available backtests.
     */
    async getFilters(): Promise<FiltersResponse> {
        return this.fetchData<FiltersResponse>('/filters');
    }

    /**
     * Fetches the historical equity data for a specific backtest run.
     * Corresponds to Python API endpoint `GET /equity`.
     * @param ticker The currency pair or stock symbol (e.g., `EURUSD=X`).
     * @param interval The candle interval (e.g., `5m`).
     * @param runName The name of the run (e.g., `run-1`).
     * @returns Promise<EquityHistoryEntry[]> A list of historical equity entries.
     */
    async getEquity(ticker: string, interval: string, runName: string): Promise<EquityHistoryEntry[]> {
        return this.fetchData<EquityHistoryEntry[]>('/equity', { ticker, interval, run_name: runName });
    }

    /**
     * Fetches all processed candle data.
     * Corresponds to Python API endpoint `GET /candles`.
     * @param ticker The currency pair or stock symbol (e.g., `EURUSD=X`).
     * @param interval The candle interval (e.g., `5m`).
     * @param runName The name of the run (e.g., `run-1`).
     * @returns Promise<Candle[]> A list of candle data.
     */
    async getCandleData(ticker: string, interval: string, runName: string): Promise<Candle[]> {
        return this.fetchData<Candle[]>('/candles', { ticker, interval, run_name: runName });
    }

    /**
     * Fetches the summary of all active and closed trades, along with the final account balance
     * for a specific backtest run.
     * Corresponds to Python API endpoint `GET /trades`.
     * @param ticker The currency pair or stock symbol (e.g., `EURUSD=X`).
     * @param interval The candle interval (e.g., `5m`).
     * @param runName The name of the run (e.g., `run-1`).
     * @returns Promise<TradeSummaryResponse> The trade summary data.
     */
    async getTradeSummary(ticker: string, interval: string, runName: string): Promise<TradeSummaryResponse> {
        return this.fetchData<TradeSummaryResponse>('/trades', { ticker, interval, run_name: runName });
    }

    /**
     * Fetches a list of active trades.
     * Extracts active trades from the `TradeSummaryResponse` fetched from the `/trades` endpoint.
     * @param ticker The currency pair or stock symbol (e.g., `EURUSD=X`).
     * @param interval The candle interval (e.g., `5m`).
     * @param runName The name of the run (e.g., `run-1`).
     * @returns Promise<ActiveTrade[]> A list of active trades.
     */
    async getActiveTrades(ticker: string, interval: string, runName: string): Promise<ActiveTrade[]> {
        const summary = await this.getTradeSummary(ticker, interval, runName);
        return summary.active_trades;
    }

    /**
     * Fetches a list of closed trades.
     * Extracts closed trades from the `TradeSummaryResponse` fetched from the `/trades` endpoint.
     * @param ticker The currency pair or stock symbol (e.g., `EURUSD=X`).
     * @param interval The candle interval (e.g., `5m`).
     * @param runName The name of the run (e.g., `run-1`).
     * @returns Promise<ClosedTrade[]> A list of closed trades.
     */
    async getClosedTrades(ticker: string, interval: string, runName: string): Promise<ClosedTrade[]> {
        const summary = await this.getTradeSummary(ticker, interval, runName);
        return summary.closed_trades;
    }

    /**
     * Fetches the detailed payloads generated for a single day within a specific backtest run.
     * Corresponds to Python API endpoint `GET /payloads`.
     * @param ticker The currency pair or stock symbol (e.g., `EURUSD=X`).
     * @param interval The candle interval (e.g., `5m`).
     * @param runName The name of the run (e.g., `run-1`).
     * @param date The specific date for the payloads in `YYYY-MM-DD` format (e.g., `2025-10-20`).
     * @returns Promise<DailyPayloadsResponse> The daily payloads data.
     */
    async getDailyPayloads(ticker: string, interval: string, runName: string, date: string): Promise<DailyPayloadsResponse> {
        return this.fetchData<DailyPayloadsResponse>('/payloads', { ticker, interval, run_name: runName, date });
    }
}