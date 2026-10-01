export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer__inner">
        <p>© {new Date().getFullYear()} Harrison Farber · BIM Designer &amp; Coordinator</p>
        <p>
          Some images are representative ·{" "}
          <a href="/assets/images/stock/CREDITS.md" target="_blank" rel="noopener">Photo credits</a>
        </p>
      </div>
    </footer>
  );
}
