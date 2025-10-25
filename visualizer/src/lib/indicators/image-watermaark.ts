import { CanvasRenderingTarget2D } from 'fancy-canvas';
import type {
	IChartApi,
	IPrimitivePaneRenderer,
	IPrimitivePaneView,
	PrimitivePaneViewZOrder,
	Time,
    SeriesAttachedParameter,
    ISeriesPrimitive,
} from 'lightweight-charts';
export interface RectanglePrimitiveOptions {
	color?: string;
	alpha?: number;
	borderWidth?: number;
}

interface ChartPoint {
	time: Time;
	price: number;
}

interface Placement {
	x: number;
	y: number;
	width: number;
	height: number;
}

class RectanglePaneRenderer implements IPrimitivePaneRenderer {
	constructor(private source: RectanglePrimitive, private view: RectanglePaneView) {}

	draw(target: CanvasRenderingTarget2D) {
		target.useMediaCoordinateSpace(scope => {
			const ctx = scope.context;
			const pos = this.view._placement;
			if (!pos) return;

			ctx.save();
			ctx.globalAlpha = this.source._options.alpha ?? 1;
			ctx.fillStyle = this.source._options.color ?? 'rgba(0, 150, 255, 0.3)';
			ctx.fillRect(pos.x, pos.y, pos.width, pos.height);

			if (this.source._options.borderWidth) {
				ctx.strokeStyle = this.source._options.color ?? 'rgba(0, 150, 255, 1)';
				ctx.lineWidth = this.source._options.borderWidth;
				ctx.strokeRect(pos.x, pos.y, pos.width, pos.height);
			}
			ctx.restore();
		});
	}
}

class RectanglePaneView implements IPrimitivePaneView {
	_placement: Placement | null = null;

	constructor(private source: RectanglePrimitive) {}

	zOrder(): PrimitivePaneViewZOrder {
		return 'top';
	}

	update() {
		this._placement = this._calculatePlacement();
	}

	renderer() {
		return new RectanglePaneRenderer(this.source, this);
	}

	private _calculatePlacement(): Placement | null {
		if (!this.source._chart) return null;

		const { time1, price1, time2, price2 } = this.source._points;
		const timeScale = this.source._chart.timeScale();
		const priceScale = this.source._series.priceScale();

		const x1 = timeScale.timeToCoordinate(time1);
		const x2 = timeScale.timeToCoordinate(time2);
		const y1 = this.source._series.priceToCoordinate(price1);
		const y2 = this.source._series.priceToCoordinate(price2);

		if (x1 === null || x2 === null || y1 === null || y2 === null) return null;

		const x = Math.min(x1, x2);
		const y = Math.min(y1, y2);
		const width = Math.abs(x2 - x1);
		const height = Math.abs(y2 - y1);

		return { x, y, width, height };
	}
}

export class RectanglePrimitive implements ISeriesPrimitive<Time> {
	_chart: IChartApi | null = null;
	_series: any;
	_requestUpdate?: () => void;
	_paneViews: RectanglePaneView[];
	_points: { time1: Time; price1: number; time2: Time; price2: number };
	_options: RectanglePrimitiveOptions;

	constructor(series: any, points: { time1: Time; price1: number; time2: Time; price2: number }, options: RectanglePrimitiveOptions) {
		this._series = series;
		this._points = points;
		this._options = options;
		this._paneViews = [new RectanglePaneView(this)];
	}

	attached({ chart, requestUpdate }: SeriesAttachedParameter<Time>) {
		this._chart = chart;
		this._requestUpdate = requestUpdate;
		this._paneViews.forEach(pv => pv.update());
		this.requestUpdate();
	}

	detached() {}

	requestUpdate() {
		if (this._requestUpdate) this._requestUpdate();
	}

	updateAllViews() {
		this._paneViews.forEach(pv => pv.update());
	}

	paneViews() {
		return this._paneViews;
	}
}