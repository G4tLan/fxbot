import type { CanvasRenderingTarget2D } from 'fancy-canvas';
import type {
  Coordinate,
  IChartApi,
  IPrimitivePaneRenderer,
  IPrimitivePaneView,
  ISeriesPrimitive,
  PrimitivePaneViewZOrder,
  SeriesAttachedParameter,
  Time,
} from 'lightweight-charts';
import type { TimeRange } from '../types';
import { timeZoneCorrection } from '../utils';

export interface ConsolidationPrimitiveOptions {
  color?: string;
}

interface ConsolidationRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ProcessedRange {
  startTs: number;
  endTs: number;
  minLow: number;
  maxHigh: number;
}

class ConsolidationPaneRenderer implements IPrimitivePaneRenderer {
  constructor(private _view: ConsolidationPaneView) {}

  draw(target: CanvasRenderingTarget2D): void {
    target.useMediaCoordinateSpace((scope) => {
      const ctx = scope.context;
      const rects = this._view.rects;
      if (!rects || rects.length === 0) return;

      const options = this._view.options;

      ctx.save();
      ctx.fillStyle = options.color ?? 'rgba(100, 100, 255, 0.2)';
      for (const rect of rects) {
        ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
      }

      ctx.restore();
    });
  }
}

class ConsolidationPaneView implements IPrimitivePaneView {
  rects: ConsolidationRect[] = [];

  constructor(private _source: ConsolidationPrimitive) {}

  get options() {
    return this._source.options;
  }

  zOrder(): PrimitivePaneViewZOrder {
    return 'bottom';
  }

  update() {
    this.rects = this._calculateRects();
  }

  renderer() {
    return new ConsolidationPaneRenderer(this);
  }

  private _calculateRects(): ConsolidationRect[] {
    const chart = this._source.chart;
    const series = this._source.series;
    const processedRanges = this._source.processedRanges;
    console.log(
      'Visible Range:',
      !chart || !series || !processedRanges || processedRanges.length === 0
    );

    if (!chart || !series || !processedRanges || processedRanges.length === 0) {
      return [];
    }

    const timeScale = chart.timeScale();
    const visibleRange = timeScale.getVisibleRange();

    // If no visible range (chart not ready?), we can't draw properly
    if (!visibleRange) return [];

    const rects: ConsolidationRect[] = [];
    const visibleFrom = visibleRange.from as number;
    const visibleTo = visibleRange.to as number;
    for (const range of processedRanges) {
      // Check if range is completely outside visible area
      if (range.endTs < visibleFrom || range.startTs > visibleTo) {
        continue;
      }

      // Calculate X coordinates with clamping for off-screen points
      let x1 = timeScale.timeToCoordinate(range.startTs as Time);
      let x2 = timeScale.timeToCoordinate(range.endTs as Time);

      // Handle off-screen coordinates
      if (x1 === null) {
        x1 = (range.startTs < visibleFrom ? -10000 : 10000) as Coordinate;
      }
      if (x2 === null) {
        x2 = (range.endTs > visibleTo ? 10000 : -10000) as Coordinate;
      }

      const y1 = series.priceToCoordinate(range.maxHigh);
      const y2 = series.priceToCoordinate(range.minLow);

      if (y1 === null || y2 === null) continue;

      rects.push({
        x: Math.min(x1 as number, x2 as number),
        y: Math.min(y1, y2),
        width: Math.abs((x2 as number) - (x1 as number)),
        height: Math.abs(y2 - y1),
      });
    }

    return rects;
  }
}

export class ConsolidationPrimitive implements ISeriesPrimitive<Time> {
  chart: IChartApi | null = null;
  series: any;
  processedRanges: ProcessedRange[] = [];
  options: ConsolidationPrimitiveOptions;

  private _paneViews: ConsolidationPaneView[];
  private _requestUpdate?: () => void;

  constructor(series: any, options: ConsolidationPrimitiveOptions = {}) {
    this.series = series;
    this.options = options;
    this._paneViews = [new ConsolidationPaneView(this)];
  }

  attached({ chart, requestUpdate }: SeriesAttachedParameter<Time>) {
    this.chart = chart;
    this._requestUpdate = requestUpdate;
    this._paneViews.forEach((v) => v.update());
    this.requestUpdate();
  }

  detached() {
    this.chart = null;
  }

  requestUpdate() {
    if (this._requestUpdate) this._requestUpdate();
  }

  setData(ranges: TimeRange[], candles: any[]) {
    this.processedRanges = [];

    if (!candles || candles.length === 0) {
      this.requestUpdate();
      return;
    }

    const INTERVAL_SEC = 5 * 60;

    for (const range of ranges) {
      const startTs = Math.floor(timeZoneCorrection(range.startDate) / INTERVAL_SEC) * INTERVAL_SEC;
      const endTs = Math.floor(timeZoneCorrection(range.endDate) / INTERVAL_SEC) * INTERVAL_SEC;

      const rangeCandles = candles.filter((c) => {
        const t = c.time as number;
        return t >= startTs && t <= endTs;
      });

      if (rangeCandles.length === 0) continue;

      let minLow = Infinity;
      let maxHigh = -Infinity;

      for (const c of rangeCandles) {
        if (c.low < minLow) minLow = c.low;
        if (c.high > maxHigh) maxHigh = c.high;
      }

      if (minLow === Infinity || maxHigh === -Infinity) continue;

      this.processedRanges.push({
        startTs,
        endTs,
        minLow,
        maxHigh,
      });
    }

    this._paneViews.forEach((v) => v.update());
    this.requestUpdate();
  }

  updateAllViews() {
    this._paneViews.forEach((pv) => pv.update());
  }

  paneViews() {
    return this._paneViews;
  }
}
