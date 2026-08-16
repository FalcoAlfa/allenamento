// Service worker minimo: l'app deve partire in modalita' aereo.
// Rete prima, cache come rete di scorta -> con rete vedo sempre il build nuovo
// (il §9 del PIANO: "il telefono prende la versione nuova alla prima apertura").
const CACHE = "allenamento";
const FILE = ["./", "./index.html", "./manifest.json", "./icona.jpg"];

self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILE)));
});

self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request)
      .then(r => {
        const copia = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copia));
        return r;
      })
      // ignoreSearch: offline con ?veloce=1 o ?test=1 deve comunque aprirsi
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
