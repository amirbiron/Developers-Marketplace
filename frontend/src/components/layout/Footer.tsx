export function Footer() {
  return (
    <footer className="mt-24 border-t border-line/60 py-8">
      <div className="container-app flex flex-col items-center gap-2 text-center text-faint sm:flex-row sm:justify-between">
        <p className="font-mono text-xs">
          <span className="text-accent-bright">$</span> devmatch · התאמת מפתחים ישראלים
        </p>
        <p className="text-xs">הפנייה ישירה בוואטסאפ · בלי תיווך · בלי עמלות</p>
      </div>
    </footer>
  );
}
