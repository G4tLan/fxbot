from peewee import *
from engine.models.base import BaseModel
import json

class Candle(BaseModel):
    timestamp = BigIntegerField()
    open = DecimalField(max_digits=20, decimal_places=8)
    high = DecimalField(max_digits=20, decimal_places=8)
    low = DecimalField(max_digits=20, decimal_places=8)
    close = DecimalField(max_digits=20, decimal_places=8)
    volume = DecimalField(max_digits=20, decimal_places=8)
    exchange = CharField()
    symbol = CharField()

    class Meta:
        indexes = (
            (('exchange', 'symbol', 'timestamp'), True),
        )

class ClosedTrade(BaseModel):
    entry_price = DecimalField(max_digits=20, decimal_places=8)
    exit_price = DecimalField(max_digits=20, decimal_places=8)
    qty = DecimalField(max_digits=20, decimal_places=8)
    pnl = DecimalField(max_digits=20, decimal_places=8)
    opened_at = BigIntegerField()
    closed_at = BigIntegerField()
    strategy_name = CharField()
    leverage = IntegerField(default=1)
    type = CharField() # long/short

class Order(BaseModel):
    id = CharField(primary_key=True)
    price = DecimalField(max_digits=20, decimal_places=8, null=True)
    qty = DecimalField(max_digits=20, decimal_places=8)
    type = CharField() # MARKET/LIMIT/STOP
    status = CharField() # ACTIVE/EXECUTED/CANCELED
    side = CharField() # buy/sell
    submitted_at = BigIntegerField()
    executed_at = BigIntegerField(null=True)
    exchange = CharField()
    symbol = CharField()
    reduce_only = BooleanField(default=False)

class Trade(BaseModel):
    timestamp = BigIntegerField()
    price = DecimalField(max_digits=20, decimal_places=8)
    buy_qty = DecimalField(max_digits=20, decimal_places=8)
    sell_qty = DecimalField(max_digits=20, decimal_places=8)
    buy_count = IntegerField()
    sell_count = IntegerField()
    exchange = CharField()
    symbol = CharField()

class Log(BaseModel):
    session_id = CharField(null=True)
    timestamp = BigIntegerField()
    message = TextField()
    type = CharField() # INFO/ERROR

class Option(BaseModel):
    type = CharField(unique=True)
    json = TextField()

class ExchangeApiKeys(BaseModel):
    exchange_name = CharField()
    name = CharField()
    api_key = CharField()
    api_secret = CharField()
    additional_fields = TextField(null=True) # JSON

class Ticker(BaseModel):
    timestamp = BigIntegerField()
    last_price = DecimalField(max_digits=20, decimal_places=8)
    high_price = DecimalField(max_digits=20, decimal_places=8)
    low_price = DecimalField(max_digits=20, decimal_places=8)
    volume = DecimalField(max_digits=20, decimal_places=8)
    exchange = CharField()
    symbol = CharField()

class Orderbook(BaseModel):
    timestamp = BigIntegerField()
    data = BlobField() # Or TextField if JSON
    exchange = CharField()
    symbol = CharField()

class DailyBalance(BaseModel):
    timestamp = BigIntegerField()
    identifier = CharField() # e.g. session_id or 'live'
    exchange = CharField()
    asset = CharField()
    balance = DecimalField(max_digits=20, decimal_places=8)

class User(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()
    email = CharField(null=True)
    created_at = BigIntegerField()


class MonteCarloSession(BaseModel):
    id = CharField(primary_key=True)
    status = CharField()
    metrics = TextField()
    data = TextField()

class OptimizationSession(BaseModel):
    id = CharField(primary_key=True)
    status = CharField()
    strategy_name = CharField()
    best_dna = TextField()
    results = TextField()

class NotificationApiKeys(BaseModel):
    driver = CharField()
    fields = TextField() # JSON

class Task(BaseModel):
    id = CharField(primary_key=True)
    type = CharField() # import/backtest
    status = CharField() # queued/processing/completed/failed
    result = TextField(null=True) # JSON
    error = TextField(null=True)
    created_at = BigIntegerField()
    updated_at = BigIntegerField()

class BacktestSession(BaseModel):
    id = CharField(primary_key=True)
    status = CharField()
    metrics = TextField(null=True)
    equity_curve = TextField(null=True)
    trades = TextField(null=True) # Executions
    closed_trades = TextField(null=True) # Completed trades
    hyperparameters = TextField(null=True)
    chart_data = TextField(null=True)
    state = TextField(null=True)
    title = CharField(max_length=255, null=True)
    description = TextField(null=True)
    strategy_codes = TextField(null=True)
    exception = TextField(null=True)
    traceback = TextField(null=True)
    execution_duration = FloatField(null=True)
    created_at = BigIntegerField()
    updated_at = BigIntegerField()

    @property
    def metrics_json(self):
        return json.loads(self.metrics) if self.metrics else None

    @property
    def equity_curve_json(self):
        return json.loads(self.equity_curve) if self.equity_curve else None

    @property
    def trades_json(self):
        return json.loads(self.trades) if self.trades else None

    @property
    def closed_trades_json(self):
        return json.loads(self.closed_trades) if self.closed_trades else None

    @property
    def hyperparameters_json(self):
        return json.loads(self.hyperparameters) if self.hyperparameters else None

    @property
    def chart_data_json(self):
        return json.loads(self.chart_data) if self.chart_data else None

    @property
    def state_json(self):
        return json.loads(self.state) if self.state else None

    @property
    def strategy_codes_json(self):
        return json.loads(self.strategy_codes) if self.strategy_codes else None

