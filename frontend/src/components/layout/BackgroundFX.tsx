/** רקע קבוע: dot-grid עדין + זוהר ירוק רדיאלי + ויניֶּטה תחתונה. לא אינטראקטיבי. */
export function BackgroundFX() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div
        className="absolute inset-0 bg-dot-grid opacity-60 [background-size:22px_22px] [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]"
      />
      <div className="absolute -top-48 right-1/4 h-[600px] w-[600px] rounded-full bg-accent/20 blur-[140px]" />
      <div className="absolute left-[-10rem] top-1/3 h-[440px] w-[440px] rounded-full bg-syntax-cyan/10 blur-[140px]" />
      <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-bg to-transparent" />
    </div>
  );
}
