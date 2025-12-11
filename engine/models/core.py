from peewee import *
from engine.models.base import BaseModel

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

class Trade(BaseModel):
    timestamp = BigIntegerField()
    price = DecimalField(max_digits=20, decimal_places=8)
    buy_qty = DecimalField(max_digits=20, decimal_places=8)
    sell_qty = DecimalField(max_digits=20, decimal_places=8)
    buy_count = IntegerField()
    sell_count = IntegerField()
    exchange = CharField()
    symbol = CharField()

class BacktestSession(BaseModel):
    id = CharField(primary_key=True)
    status = CharField()
    metrics = TextField() # JSON
    equity_curve = TextField() # JSON
    trades = TextField() # JSON
    hyperparameters = TextField() # JSON
    strategy_codes = TextField() # JSON
    created_at = BigIntegerField()

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

