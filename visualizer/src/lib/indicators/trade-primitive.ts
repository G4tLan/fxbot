import type { CanvasRenderingTarget2D } from 'fancy-canvas';
import type {
  IChartApi,
  IPrimitivePaneRenderer,
  IPrimitivePaneView,
  ISeriesPrimitive,
  PrimitivePaneViewZOrder,
  SeriesAttachedParameter,
  Time,
} from 'lightweight-charts';

export interface TradePrimitiveOptions {
  profitColor?: string;
  lossColor?: string;
  alpha?: number;
  tradeLineColor?: string;
  tradeLineWidth?: number;
}

export interface TradePoints {
  entryTime: Time;
  entryPrice: number;
  closePrice?: number | null;
  latestTime?: Time | null;
  latestPrice?: number | null;
  stopLoss?: number | null;
  takeProfit?: number | null;
}

class TradePaneRenderer implements IPrimitivePaneRenderer {
  constructor(
    private source: TradePrimitive,
    private view: TradePaneView
  ) {}

  draw(target: CanvasRenderingTarget2D): void {
    target.useMediaCoordinateSpace((scope) => {
      const ctx = scope.context;
      const pos = this.view._placement;
      if (!pos) return;
      const options = this.source._options;

      ctx.save();
      ctx.globalAlpha = 1;
      if (pos.yStopLoss !== undefined) {
        ctx.fillStyle = options?.lossColor ?? 'rgba(255, 0, 0, 0.5)';
        const height = pos.yStopLoss - pos.y;
        ctx.fillRect(pos.x, pos.y, pos.width, height);
      }

      ctx.fillStyle = options?.profitColor ?? 'rgba(0, 255, 0, 0.5)';
      const height = pos.yTakeProfit ? pos.yTakeProfit - pos.y : pos.height;
      ctx.fillRect(pos.x, pos.y, pos.width, height);

      // Draw trade line
      ctx.strokeStyle = options?.tradeLineColor ?? 'black';
      ctx.lineCap = 'round';
      ctx.lineWidth = options?.tradeLineWidth ?? 2;
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      console.log('Drawing trade line to:', pos);
      ctx.lineTo(pos.x + pos.width, pos.yClose ?? pos.y + pos.height);
      ctx.stroke();
      ctx.restore();
    });
  }
}

class TradePaneView implements IPrimitivePaneView {
  _placement: Placement | null = null;

  constructor(private source: TradePrimitive) {}

  zOrder(): PrimitivePaneViewZOrder {
    return 'top';
  }

  update() {
    this._placement = this._calculatePlacement();
  }

  renderer() {
    return new TradePaneRenderer(this.source, this);
  }

  _calculatePlacement(): Placement | null {
    if (!this.source._chart || !this.source._points || !this.source._series) return null;

    const points = this.source._points;
    const timeScale = this.source._chart.timeScale();
    const data = this.source._series.data();
    const lastTime = points.latestTime ?? (data.length > 0 ? data[data.length - 1].time : null);
    const lastClose = points.latestPrice ?? (data.length > 0 ? data[data.length - 1].close : null);
    const series = this.source._series;
    if (!lastTime || !lastClose) return null;

    const x1 = timeScale.timeToCoordinate(points.entryTime);
    const x2 = timeScale.timeToCoordinate(lastTime);
    const y1 = series.priceToCoordinate(points.entryPrice);
    const y2 = series.priceToCoordinate(lastClose);
    const yStopLoss = points.stopLoss ? series.priceToCoordinate(points.stopLoss) : null;
    const yTakeProfit = points.takeProfit ? series.priceToCoordinate(points.takeProfit) : null;
    const yClose = points.closePrice ? series.priceToCoordinate(points.closePrice) : y2;

    if (x1 === null || x2 === null || y1 === null || y2 === null) return null;

    const x = x1;
    const y = y1;
    const width = Math.abs(x2 - x1);
    const height = y2 - y1;

    return { x, y, width, height, yStopLoss, yTakeProfit, yClose };
  }
}

export class TradePrimitive implements ISeriesPrimitive<Time> {
  _chart: IChartApi | null = null;
  _series: any;
  _requestUpdate?: () => void;
  _paneViews: TradePaneView[];
  _points: TradePoints | null;
  _options: TradePrimitiveOptions | undefined;

  constructor(series: any, options?: TradePrimitiveOptions) {
    this._series = series;
    this._points = null;
    this._options = options;
    this._paneViews = [new TradePaneView(this)];
  }

  attached({ chart, requestUpdate }: SeriesAttachedParameter<Time>) {
    this._chart = chart;
    this._requestUpdate = requestUpdate;
    this._paneViews.forEach((view) => view.update());
    this.requestUpdate();
  }

  detached(): void {
    this._chart = null;
  }

  requestUpdate() {
    if (this._requestUpdate) {
      this._requestUpdate();
    }
  }

  setPoints(points: TradePoints | null) {
    this._points = points;
    this._paneViews.forEach((view) => view.update());
    this.requestUpdate();
  }

  updateAllViews() {
    this._paneViews.forEach((pv) => pv.update());
  }

  paneViews() {
    return this._paneViews;
  }
}
