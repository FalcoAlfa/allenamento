# App di allenamento — piano di lavoro

Documento di riferimento. Chi riprende il lavoro in una sessione futura legge
**solo questo file** e sa cosa fare: le decisioni qui dentro sono chiuse, non
vanno ridiscusse. Prima di toccare qualsiasi cosa, leggi comunque
[../CLAUDE.md](../CLAUDE.md).

---

## 0. Registro — dove siamo arrivati

**Prossimo passo: fase 4.**

| Fase | Stato | Cosa è successo davvero |
|---|---|---|
| 0 · Decisioni | ✅ 16/08/2026 | Piano scritto. Nessuna riga di codice. |
| 1 · `costruisci.py` | ✅ 16/08/2026 | Fatto `costruisci.py` + `modello.html` (guscio provvisorio: elenca le sedute con le figure, la fase 2 lo riscrive). Conteggio vero: **M1 8 · M2 8 · M3 8 · A 17 · B 17 · figure 36** — il §5.4 diceva 16/16/34, sbagliato il piano non le schede, ora corretto. Tre cose che il piano non prevedeva: **(a)** ci sono schede che rimandano a un'altra (`B1 → A1`, `F2 → R2`, le 5 mattutine condivise → forza): ereditano figura e testi ma **mai quanto e recupero**, che cambiano da blocco a blocco (il jumping jack è 45 s nel riscaldamento e 30 s nel finisher). **(b)** Finisher (`F*`) e scarico (`S*`) non hanno **Come progredire** e non devono averlo: il controllo pretende i quattro paragrafi solo fuori da lì, tre negli altri casi. **(c)** Ci sono anche le tabelle-indice di ogni blocco (il §5.2 lo negava, corretto): servono a dare quanto/recupero alle schede che rimandano. Aggiunto un controllo non previsto: max 4 esercizi per blocco skill/forza. Riscritto il §9 con la procedura per aggiungere/togliere un esercizio.<br><br>**Aggiunto dopo**, perché servirà ai timer della fase 2: `quanto` e `recupero` sono testo libero (`3 × 10-20 s`, `0 (poi F2)`), quindi il build ne ricava anche i numeri — per esercizio `serie`, `secondi` (0 = a ripetizioni, niente countdown), `per_lato`, `recupero_s`; per blocco `giri` e `recupero_giro_s` (il finisher gira 2 volte). Dei range prende il massimo, che è l'obiettivo. È un'euristica sul testo: il testo originale resta e l'app lo mostra sempre. **Rimandato alla fase 2**: quali esercizi sono "chiave" per i campi di fine seduta (§6). Non è deducibile dalle schede — 3 delle 8 voci del test (dead hang massimale, trazioni, plank frontale) non hanno un esercizio corrispondente in nessuna seduta. |
| 2 · L'app | ✅ 16/08/2026 | `modello.html` riscritto: home, seduta, timer, fine seduta, storico, export. Un file, nessuna dipendenza. **Le due domande che la fase 1 e il §11 avevano lasciato aperte, chiuse così:** **(a)** esercizi chiave, 6 su 8 — dead hang (R5 e mattutino), negativa (B3), piegamenti (A4), L-sit (A1/B1), crow (A2), mani-muro (A3). Trazioni e plank frontale non stanno in nessuna seduta: restano voci del test, si compilano a mano nella tabella. **(b)** §11.3 confermato: la seduta in corso si salva a ogni passo, alla riapertura la home offre *Riprendi / Butta via*; riprendendo riparte dall'esercizio dov'era, ferma, con il suo cronometro, e il tap è di nuovo *Inizia*.<br><br>**Cose che il piano non prevedeva.** La seduta è una **lista piatta di passi** (un passo = una serie, e un lato): 3 × 20 s sono tre countdown, `45 s per lato` sono due, e il finisher gira davvero due volte — la sessione A sono 36 passi per 17 esercizi. Il recupero di fine giro batte quello dell'esercizio, l'ultimo passo non ne ha. **La riga di log è una per giorno, non per seduta**: la tabella del diario ha sia *Sessione* sia *Mattutina*, quindi mattutina e forza dello stesso giorno finiscono nella stessa riga; se le esporti in due momenti l'export dice di sostituire la riga invece di aggiungerla. Il §6 diceva "quattro sezioni richiudibili": sono quattro o tre a seconda della scheda (finisher e scarico non hanno *Come progredire*, vedi fase 1) più *Cosa cambia al mattino* dove c'è.<br><br>**Corretto in `costruisci.py`** (3 righe, l'unica modifica alla fase 1): la mattutina prescrive nella **tabella della routine**, non nella scheda — il gatto-cammello è 8 ripetizioni in M1 e 6 in M2 — quindi i numeri dei timer di ogni riga si ricavano da lì. Prima l'app avrebbe cronometrato i numeri della scheda, cioè quelli sbagliati.<br><br>**Rimandato alla fase 3**: `manifest.json`, `sw.js`, `icona.svg`. Sono l'installazione sul telefono, non l'app: la verifica della fase 2 gira su file locale.<br><br>**Verifica fatta**: `index.html?test=1` esegue gli assert su passi, rotazione M1→M2→M3 e A/B, riga di log e sigle sparite (in Chrome dice *test ok*); M1 e A finte da cima a fondo, con un esercizio saltato, fino a salvataggio ed export; le quattro schermate aperte in un browser vero. `?veloce=1` fa scorrere i timer 10×.|
| 3 · Pubblicazione | ✅ 16/08/2026 | Online su **https://falcoalfa.github.io/allenamento/**, repo `FalcoAlfa/allenamento`, Pages da `main` `/`. Fatti i tre file che la fase 2 aveva rimandato: `manifest.json`, `sw.js`, `icona.svg`. In `modello.html` quattro righe di `<head>` (manifest, icona, `apple-touch-icon`, `apple-mobile-web-app-capable`) e una riga in fondo che registra il service worker con `?.` e `.catch()`: da `file://` il service worker non esiste e la verifica in locale della fase 2 deve continuare a girare.<br><br>**Due scelte che il §4 non prevedeva.** **(a)** Il service worker è **rete-prima, cache di scorta**, non cache-prima: "tiene l'app in cache" preso alla lettera avrebbe congelato il primo build per sempre, mentre il §9 promette che il telefono prende la versione nuova alla prima apertura con rete. Nel `catch` la cache risponde con `ignoreSearch`, altrimenti offline `?veloce=1` e `?test=1` non aprirebbero niente. **(b)** L'icona è un solo SVG, disegnato dentro il cerchio di sicurezza dell'80% così vale anche come `maskable`. Niente PNG 192/512: si aggiungono solo se il telefono è un iPhone e l'icona esce male.<br><br>`gh` 2.97 installato con winget, login fatto (`FalcoAlfa`), repo git inizializzato in `app/` con il primo commit. L'identità git è **locale al repo** e usa `314305238+FalcoAlfa@users.noreply.github.com`: il repo è pubblico, l'email vera no.<br><br>**La cosa che il §2 aveva previsto ed è successa davvero**: il repo è nato privato, perché era quello che volevo, e Pages ha risposto `422 — Your current plan does not support GitHub Pages for this repository`. Piano gratuito, Pages solo su repo pubblici. Il punto che ha deciso: **il sito pubblicato è comunque leggibile da chiunque abbia l'URL** — `index.html` va servito in chiaro perché il telefono lo scarichi, quindi "repo privato" nascondeva `PIANO.md` e `costruisci.py`, non le schede. Le alternative erano Cloudflare Pages (gratis, repo privato, account nuovo e OAuth) o GitHub Pro (4 $/mese). Scelto pubblico: nel repo non c'è niente di mio, il diario resta sul telefono. Il repo è stato portato da privato a pubblico con `gh repo edit --visibility public`.<br><br>**Verifica fatta**: dal PC i quattro file rispondono 200 con il MIME giusto (`index.html` 182 KB, `manifest.json`, `sw.js`, `icona.svg`); dal telefono app installata sulla schermata Home e **provata in modalità aereo**, funziona tutta. |
| 4 · Primo giro completo | ⬜ da fare — la catena è pronta e verificata a vuoto | Controllato prima di iniziare, così la seduta vera non si scontra con un formato sbagliato: la riga che produce `rigaLog()` ha le stesse cinque colonne del *Log delle sedute* di `diario.md` (`Data · Sessione · Mattutina · Nota chiave · Sensazione`), e il testo di `nota()` ha gli stessi titoli e gli stessi sei punti di `_modello-nota.md`. `python diario/riepilogo.py` gira pulito sul diario vuoto (`autotest ok`, 0 sedute) e non legge `sedute.jsonl`: è la fase 5, giusto così.<br><br>**Un prerequisito che il §8 non nomina**: `riepilogo.py` dice *"fai la riga di partenza prima della 1a seduta"*. La riga dei **test di riferimento** in `diario.md` è vuota, e senza quella i numeri della prima seduta non hanno un termine di paragone. Va misurata a muscoli riposati, solo riscaldamento prima. Sono numeri suoi, nessuno può inventarli. |
| 5 · Riepilogo esteso | ⬜ rimandata | Solo dopo ~10 sedute registrate. |

**Regola: chiude una fase chi la fa.** Prima di dire "fatto", aggiorna la riga
qui sopra e scrivi nell'ultima colonna cosa è cambiato rispetto al piano —
scelte diverse, trappole trovate, pezzi rimandati. Se una fase finisce a metà,
scrivilo (`🟡 a metà: manca X`). Senza questo registro, la sessione dopo
riparte alla cieca e rifà il lavoro.

**Regola: questo file non si tocca senza il mio permesso.** L'unica eccezione
è la tabella qui sopra, che va aggiornata a fine fase. Tutto il resto —
decisioni, fasi, regole di lettura — si cambia solo se te lo chiedo io: se
lavorando scopri che una parte del piano è sbagliata, **dillo e basta**,
scrivilo nel registro e vai avanti. Un piano che si riscrive da solo mentre lo
esegui non è più un piano.

---

## 1. Cosa deve fare

Un'app che apro dal telefono e che mi guida durante l'allenamento: mi dice
cosa tocca oggi, mi fa scegliere tra routine mattutina e forza, mi porta
esercizio per esercizio con figura, ripetizioni e istruzioni, cronometra, e a
fine seduta raccoglie i miei numeri e i miei feedback e li trasforma nei file
del diario.

Il punto non è avere un'app: è che il diario si compili da solo, così le
schede si aggiornano su dati veri invece che su ricordi.

---

## 2. Decisioni prese — non si riaprono

| Domanda | Scelta | Perché |
|---|---|---|
| Dove gira | **App web installabile (PWA) su GitHub Pages** | Funziona anche senza rete e senza PC acceso. Si installa sulla schermata home come un'app vera. |
| Da dove prende gli esercizi | **Dai `.md` esistenti**, tramite uno script che li converte | Unica fonte di verità: le schede restano il posto dove si lavora, l'app è solo una vista. |
| Dove stanno i miei dati | **Sul telefono** (`localStorage`), mai su GitHub | Il diario è roba mia, il repo è pubblico. |
| Quanto registro durante la seduta | **Solo gli esercizi chiave** | Un diario che pesa è un diario che smetti di compilare. |
| Avanzamento tra esercizi | **Sempre manuale**, con segnale a fine tempo | Se sto sistemando il tappetino non voglio che l'app sia già due esercizi avanti. |
| Segnali | **Vibrazione + schermo sempre acceso**. Niente suoni | Funziona con la musica alta e con le mani occupate. |
| Cosa finisce nel diario | **Riga di log + nota libera se serve + storico completo su richiesta** | Vedi §6: le prime due cose rispettano il sistema che già uso, la terza serve a me (Claude) per aggiornare le schede. |

**Nota sul repo pubblico**: GitHub Pages gratuito serve solo repository
pubbliche. Nel repo finiscono **solo** le routine e il codice dell'app — cose
che non sono segrete. Diario, numeri, note e feedback non ci arrivano mai:
restano sul telefono finché non li incollo io. Se un giorno il repo pubblico
dà fastidio, l'alternativa è Cloudflare Pages con repo privato (stesso
risultato, mezz'ora di configurazione in più).

---

## 3. Come funziona, dall'inizio alla fine

```
  routine-mattutina.md          [io scrivo/aggiorno le schede]
  allenamento-forza.md
  img/*.svg
         │
         │  python costruisci.py        ← unico passaggio di build
         ▼
  app/index.html                 [un solo file, tutto dentro: dati, SVG, CSS, JS]
         │
         │  git push                    ← lo faccio io quando aggiorno le schede
         ▼
  https://<utente>.github.io/allenamento/
         │
         │  il telefono la scarica una volta e la tiene in cache
         ▼
  App sul telefono → seduta → dati salvati in locale
         │
         │  bottone "Esporta" → copia negli appunti → incollo a Claude
         ▼
  diario/diario.md  (riga di log)
  diario/AAAA-MM-GG.md  (nota, solo se serve)
  diario/sedute.jsonl  (storico completo, quando lo chiedo)
```

Il telefono non parla mai direttamente con il PC. L'unico ponte è il
copia-incolla dell'export, ed è voluto: niente server da tenere acceso,
niente rete di casa, niente sincronizzazione da debuggare.

---

## 4. Struttura dei file

```
1-Sport/app/
  PIANO.md          questo documento
  costruisci.py     legge i .md, genera index.html. L'unico script.
  modello.html      il guscio dell'app: HTML + CSS + JS, con un segnaposto per i dati
  index.html        GENERATO. Non modificarlo a mano: al prossimo build sparisce.
  manifest.json     serve perché il telefono la installi come app
  sw.js             service worker minimo: tiene l'app in cache per l'uso offline
  icona.svg         icona sulla schermata home
```

`1-Sport/app/` **è anche il repository git** pubblicato su GitHub Pages. Il
resto di `99-Personale/` non ci entra.

---

## 5. `costruisci.py` — le regole di lettura

È il pezzo delicato: dipende dal formato fisso imposto dalla sezione 7 di
CLAUDE.md. Regola generale: **se qualcosa non torna, si ferma con un errore
chiaro**. Mai saltare un esercizio in silenzio.

### 5.1 Routine mattutina

- Le tre sequenze sono le tabelle sotto i titoli `# M1 · …`, `# M2 · …`,
  `# M3 · …`. Colonne: `# | Esercizio | Quanto | Il cue che conta | Tempo`.
- Il nome dell'esercizio è un link `[Nome](#ancora)`: l'ancora punta alla
  scheda `### Nome` nella sezione "Schede degli esercizi".
- Dalla scheda si prendono: figura `![…](img/slug.svg)`, tabella
  quanto/recupero/attrezzi, e i quattro paragrafi **Come si fa**,
  **Attenzione a**, **Per sfruttarlo al meglio**, **Come progredire**, più il
  link 🎥.

### 5.2 Allenamento di forza

**La sequenza è l'ordine delle schede nel file**, non l'ordine delle
tabelle. Le schede sono titoli `## R1. Nome` / `### A4. Nome`.

Ogni blocco ha comunque la sua tabella-indice (`| # | Esercizio | Serie ×
quanto | Recupero |`) e il build la legge, ma solo per prendere quanto e
recupero: servono alle schede che rimandano a un'altra e non hanno tabella
propria (`B1 → A1`, `F2 → R2`). Quando la scheda ha la sua tabella, vince
quella.

Composizione delle due sedute:

| Seduta | Blocchi, in quest'ordine |
|---|---|
| **A** | `BLOCCO 0` (R1→R5) → `SESSIONE A / BLOCCO 1` (A1→A3) → `BLOCCO 2` (A4→A7) → `BLOCCO 3 Finisher A` (F1, F2) → `BLOCCO 4` |
| **B** | `BLOCCO 0` (R1→R5) → `SESSIONE B / BLOCCO 1` (B1→B3) → `BLOCCO 2` (B4→B7) → `BLOCCO 3 Finisher B` (F1, F2) → `BLOCCO 4` |

Due trappole da non sbagliare:

1. **Le sigle si ripetono**: esiste un `F1. Mountain climber` in A e un
   `F1. Burpee` in B. La chiave di un esercizio è (sezione + sigla), mai la
   sigla da sola.
2. **Il blocco 4 è condiviso e filtrato**: le schede marcate `*(solo A)*`
   entrano solo in A, quelle `*(solo B)*` solo in B, le altre in entrambe.
   L'ordine è quello del file (quindi in B: S4 → S2 → S3).

### 5.3 Figure

Gli SVG vengono **incorporati dentro `index.html`**, non linkati. Sono file
piccoli e così l'app resta un file solo che funziona offline senza dipendenze.

### 5.4 Controlli obbligatori del build

Il build fallisce, con messaggio esplicito, se:

- un esercizio in tabella non ha la scheda corrispondente;
- una scheda non ha la figura, o l'SVG citato non esiste in `img/`;
- manca uno dei quattro paragrafi obbligatori;
- una routine mattutina supera gli 8 esercizi o i 10 minuti dichiarati
  (i vincoli della sezione 7 di CLAUDE.md: se salta questo controllo, ho
  sbagliato io a scrivere la scheda).

A build riuscito stampa il conteggio: `M1 8 · M2 8 · M3 8 · A 17 · B 17 ·
figure 36`. È il modo più veloce di accorgersi che si è rotto qualcosa.

---

## 6. L'app — schermate e comportamento

### Home

- Data di oggi e **cosa tocca**: la routine mattutina viene dal ciclo
  M1→M2→M3, la sessione di forza dall'alternanza A/B. Entrambe calcolate
  dallo storico salvato sul telefono; se lo storico è vuoto si parte da M1 e A.
- Due bottoni grandi: **Mattutina (M2)** e **Forza (A)**. Sotto, in piccolo,
  "scegli un'altra" per forzare la scelta (utile se ho fatto una seduta senza
  app o mi sono perso nella rotazione).
- Terzo bottone, piccolo: **Esporta** (§7).

### Durante la seduta

- In alto: **cronometro totale**, che parte al tap su *Inizia* e si può
  mettere in pausa. È il tempo che finisce nel diario.
- Al centro la scheda dell'esercizio corrente: `3 / 8`, nome, **figura**,
  quanto (serie × ripetizioni o tempo), il cue in evidenza.
- Sotto, quattro sezioni richiudibili, chiuse di default: *Come si fa*,
  *Attenzione a*, *Per sfruttarlo al meglio*, *Come progredire*. Chiuse perché
  dopo due settimane non servono più; presenti perché le prime volte sì.
- Esercizi a tempo: countdown grande. A zero **vibra** e si ferma lì,
  aspettando il tap. Esercizi a ripetizioni: solo il bottone *Fatto*.
- Se la scheda prevede un recupero, dopo la serie parte il countdown di
  recupero, con vibrazione alla fine.
- In fondo: *Fatto* · *Salta* · *Indietro*. "Salta" è importante: un esercizio
  saltato è un dato, e voglio saperlo.
- Lo schermo resta acceso per tutta la seduta (Wake Lock).

### Fine seduta

1. **Riepilogo**: tempo totale, quanti esercizi fatti, quali saltati.
2. **Numeri chiave** — campi numerici solo per gli esercizi chiave presenti in
   quella seduta: dead hang (s), trazioni, negativa (s), piegamenti, plank (s),
   L-sit raccolto (s), crow (s), mani-muro (cm). Sono le stesse voci della
   tabella dei test del diario, così i numeri sono confrontabili.
3. **Sensazione**: 🟢 · 🟡 · 🔴.
4. **Feedback libero**: campo di testo.
5. **Ho sentito un fastidio**: interruttore che apre i campi del
   [modello nota](../diario/_modello-nota.md) — dove, con quale esercizio, in
   che punto del movimento, durante o il giorno dopo, muscolare o articolare.
   Il dolore non passa mai da un campo note generico: quando c'è, si compila
   quello strutturato.
6. **Salva** → finisce nello storico locale.

---

## 7. Cosa produce l'export

Bottone *Esporta* → genera il testo, lo copia negli appunti (e offre la
condivisione nativa del telefono). Io lo incollo in chat, Claude scrive i file.
Tre pezzi, prodotti solo quando servono:

**a) La riga di log** — sempre. Va nella tabella *Log delle sedute* di
[diario.md](../diario/diario.md), formato identico a quello già in uso:

```
| 18/08 | B | M2 | negativa 6 s × 3, dead hang 34 s | 🟡 |
```

La "nota chiave" viene composta dai numeri chiave inseriti, non da un
riassunto generico.

**b) La nota libera** — solo se ho scritto un feedback o segnalato un
fastidio. File `diario/AAAA-MM-GG.md` nel formato di `_modello-nota.md`.

**c) Lo storico completo** — su richiesta, dal bottone *Esporta tutto*. Una
riga JSON per seduta, in `diario/sedute.jsonl`:

```json
{"data":"2026-08-18","tipo":"forza","sessione":"B","durata_s":2410,"saltati":["B7"],"chiave":{"dead_hang_s":34,"negativa_s":6},"sensazione":"🟡","note":""}
```

**Perché anche il JSONL** (era la domanda che avevi lasciato a me): la riga di
log e la nota bastano a te, non bastano a me. Cose come *"salti sempre
l'ultimo esercizio del blocco forza"*, *"la seduta A dura in media 12 minuti
più di quanto dovrebbe"* o *"il crow è fermo da cinque sedute"* non entrano in
una riga di tabella, ma sono esattamente i segnali su cui si decide cosa
togliere e cosa far progredire. Il JSONL costa zero fatica in più (lo genera
l'app) e non sporca il diario che leggi tu.

---

## 8. Fasi di realizzazione

Ogni fase finisce con una verifica concreta. Non si passa alla successiva
senza averla superata.

### Fase 1 — `costruisci.py`

Parser + controlli + generazione di `index.html`.

- **Verifica**: `python costruisci.py` gira sui `.md` veri, stampa il
  conteggio, e un `demo()` con `assert` nel file stesso controlla che la M1
  abbia 8 esercizi, che A1 sia l'L-sit e che ogni esercizio abbia figura e i
  quattro paragrafi. Rompendo di proposito un titolo in un `.md`, il build
  deve fallire con un messaggio che dice quale.

### Fase 2 — `modello.html`, l'app

UI completa: home, seduta, timer, fine seduta, storico, export.

- **Verifica**: apro `index.html` sul PC e faccio una M1 finta da cima a fondo
  (con `?veloce=1` i timer scorrono 10× per non aspettare 9 minuti). Alla fine
  l'export produce una riga di log corretta.

### Fase 3 — pubblicazione e installazione sul telefono

Cosa serve da parte tua, una volta sola:

1. Dirmi il tuo nome utente GitHub.
2. Autorizzare il PC a fare push: `gh auth login` (o token). Ti guido io.

Poi faccio: repo `allenamento`, push, GitHub Pages attivo sul branch `main`.

Cosa fai tu sul telefono, una volta sola: apri
`https://<utente>.github.io/allenamento/`, menu del browser → *Aggiungi alla
schermata Home*.

- **Verifica**: telefono in **modalità aereo**, apro l'app dall'icona: deve
  partire e funzionare tutta, figure comprese.

### Fase 4 — il giro completo

Prima seduta vera fatta con l'app, export incollato, file del diario aggiornati.

- **Verifica**: `python diario/riepilogo.py` mostra la seduta.

### Fase 5 — solo se serve davvero

`riepilogo.py` legge anche `sedute.jsonl` e stampa medie e esercizi saltati.
Da fare **dopo** che ci sono almeno una decina di sedute dentro, non prima:
finché il file è vuoto è codice che non serve a nessuno.

---

## 9. Manutenzione — quando aggiungo, tolgo o cambio un esercizio

Le schede sono l'unica fonte: **si modifica il `.md`, mai `index.html`**.
Quando ti dico *"togli l'affondo bulgaro"* o *"aggiungi le trazioni
australiane"*, il giro è sempre questo, in quest'ordine:

1. **La scheda** — la scrivi o la togli in `allenamento-forza.md` /
   `routine-mattutina.md`, nel formato della sezione 7 di CLAUDE.md: numero
   d'ordine, nome, figura, tabella, i quattro paragrafi, link video.
2. **La tabella-indice** — la riga va aggiunta o tolta anche lì: quella del
   blocco per la forza, quella della routine per la mattutina (quanto, cue,
   tempo).
3. **La figura** — se è nuova, si aggiunge a `img/genera_figure.py` e si
   rigenera. Mai disegnata a mano.
4. **I vincoli** — massimo 4 esercizi per blocco skill e forza, massimo 8
   esercizi e 10 minuti per routine mattutina. Il build si ferma se li sfori:
   è un controllo, non un dispetto.
5. **Il build** — `python img/genera_figure.py` (solo se ci sono figure
   nuove), poi `python app/costruisci.py`. Se manca un pezzo il build dice
   quale.
6. **Il push** — `cd app && git commit -am "aggiorna schede" && git push`.
   Il telefono prende la versione nuova alla prima apertura con rete, e l'app
   mostra in fondo alla home la data del build, così so se sto guardando roba
   vecchia.

Tre cose da ricordare, sono quelle che si rompono:

- **La chiave di un esercizio è sezione + sigla** (`A:A5`). Se rinumeri, le
  sedute già salvate sul telefono continuano a citare le sigle vecchie: l'app
  deve mostrarle come *"esercizio non più in programma"* invece di rompersi.
  Vincolo per la fase 2.
- **Le schede condivise**: le 5 mattutine che rimandano ad
  `allenamento-forza.md`, `B1 → A1` e `F2 → R2`. Se togli la scheda completa
  rompi anche chi la richiama. Il build lo dice, ma è più veloce cercare il
  nome prima.
- **Il conteggio del §5.4** va aggiornato quando cambia. È l'unica riga di
  questo piano che segue le schede: correggila senza chiedere.

Regola di CLAUDE.md sezione 8, che vale sempre: il programma cresce in
difficoltà, non in lunghezza. Se ti chiedo di aggiungere un esercizio senza
dirti cosa tolgo, chiedimelo tu — il tempo è fisso.

---

## 10. Cosa l'app NON fa — di proposito

Elenco difensivo: sono cose già valutate e scartate, non dimenticanze.

| Cosa | Perché no |
|---|---|
| Account, login, cloud | Un utente solo, un telefono solo. |
| Scrittura diretta nei file del diario dal telefono | Richiederebbe un server acceso sul PC e la stessa rete. Il copia-incolla costa 5 secondi. |
| Grafici e statistiche dentro l'app | Le tendenze le leggo io dal diario, e sono la parte che ti serve discussa, non disegnata. |
| Video degli esercizi | Ci sono già i link di ricerca YouTube nelle schede. Ospitare video romperebbe l'offline. |
| Notifiche e promemoria | La routine è appena sveglio e la sera: non ho un problema di memoria, ho un problema di dati. |
| Modificare le schede dall'app | Le schede si aggiornano ragionando insieme sui numeri, non tappando su un telefono. |

---

## 11. Domande ancora aperte

Da chiudere quando arriva il momento, non bloccano l'inizio:

1. **Nome utente GitHub** — serve in fase 3.
2. **Serve la seduta di test?** I test di riferimento (ogni 4 settimane) sono
   una seduta a sé. Per ora l'app non li gestisce: si compilano a mano nella
   tabella del diario. Se dopo un paio di giri risulta scomodo, si aggiunge
   una terza modalità "Test" in home.
3. **Cosa fa l'app se apro una seduta e non la finisco?** Proposta: la tiene in
   sospeso e alla riapertura chiede "riprendi o butti via?". Da confermare
   alla fase 2.
