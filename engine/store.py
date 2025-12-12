class Store:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current_candle = None
        self.price = 0
        self.orders = []
        self.trades = [] # Executions
        self.closed_trades = [] # Completed trades (entry + exit)
        self.balance = {}
        self.positions = {}
        self.app_mode = None # 'backtest', 'live', 'import'

