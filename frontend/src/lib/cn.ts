/** מחבר class names, מתעלם מ-falsy. עוזר קליל בלי תלות חיצונית. */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}
