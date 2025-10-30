import { toZonedTime } from 'date-fns-tz';

export function timeZoneCorrection(
  stringDate: string,
  timezone: string = Intl.DateTimeFormat().resolvedOptions().timeZone
): number {
  return toZonedTime(new Date(stringDate), timezone).getTime() / 1000;
}

export function timeZoneCorrectionString(stringDate: string, timezone: string = 'UTC'): string {
  const zoned = toZonedTime(new Date(stringDate), timezone);

  const pad = (n: number) => String(n).padStart(2, '0');

  const year = zoned.getFullYear();
  const month = pad(zoned.getMonth() + 1);
  const day = pad(zoned.getDate());
  const hour = pad(zoned.getHours());
  const minute = pad(zoned.getMinutes());
  const second = pad(zoned.getSeconds());

  const tzName =
    new Intl.DateTimeFormat('en-US', { timeZone: timezone, timeZoneName: 'short' })
      .formatToParts(zoned)
      .find((part) => part.type === 'timeZoneName')?.value ?? timezone;

  return `${year}-${month}-${day} ${hour}:${minute}:${second} ${tzName}`;
}
