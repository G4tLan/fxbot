interface Placement {
  x: number;
  y: number;
  width: number;
  height: number;
  inProfit: boolean;
  closeTime?: number | null;
  yClose?: number;
  yStopLoss?: number;
  yTakeProfit?: number;
}
