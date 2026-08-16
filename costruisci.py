"""Legge le schede .md e genera app/index.html. Unico passaggio di build.

    python app/costruisci.py

Le schede restano l'unica fonte di verita': l'app e' solo una vista. Se
qualcosa non torna il build si ferma con un errore che dice **quale**
esercizio, mai saltarne uno in silenzio.
"""

import datetime
import json
import pathlib
import re
import sys

QUI = pathlib.Path(__file__).resolve().parent
BASE = QUI.parent
IMG = BASE / "img"

MAX_ESERCIZI_ROUTINE = 8
MAX_MINUTI_ROUTINE = 10
MAX_ESERCIZI_BLOCCO = 4          # CLAUDE.md sezione 7

# la console di Windows non e' UTF-8: senza questo il conteggio esce illeggibile
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class Errore(Exception):
    """Build fermato. Il messaggio nomina sempre l'esercizio colpevole."""


# ---------------------------------------------------------------- markdown

TITOLI = re.compile(r"^(#{1,4})\s+(.+?)\s*$", re.M)
MARCATORE = re.compile(r"^\*\*([^*\n]+?)\.\*\*[ ]*", re.M)
FIGURA = re.compile(r"!\[[^\]]*\]\(img/([\w.-]+\.svg)\)")
VIDEO = re.compile(r"\[Cerca il video\]\((.+?)\)")

PARAGRAFI = {
    "Come si fa": "come",
    "Attenzione a": "attenzione",
    "Per sfruttarlo al meglio": "sfruttare",
    "Come progredire": "progredire",
    "Cosa cambia al mattino": "mattino",
}


def ancora(titolo):
    """Slug alla maniera di GitHub: e' quello a cui puntano i link delle tabelle."""
    s = re.sub(r"[^\w\s-]", "", titolo.strip().lower())
    return re.sub(r"\s+", "-", s)


def celle(corpo):
    """Righe della prima tabella markdown incontrata, gia' spezzate in celle."""
    righe = []
    for r in corpo.splitlines():
        if r.lstrip().startswith("|"):
            righe.append([c.strip() for c in r.strip().strip("|").split("|")])
        elif righe:
            break
    return righe


def tabella(corpo):
    """Prima tabella a riga singola: dict intestazione -> valore."""
    righe = celle(corpo)
    return dict(zip(righe[0], righe[2])) if len(righe) >= 3 else {}


def colonna(tab, nome):
    return next((v for k, v in tab.items() if nome in k.lower()), "")


def paragrafi(corpo):
    """I blocchi che iniziano con **Etichetta.** a inizio riga."""
    pezzi = MARCATORE.split(corpo)
    out = {}
    for etichetta, testo in zip(pezzi[1::2], pezzi[2::2]):
        testo = testo.split("\U0001f3a5")[0].split("→ [")[0].strip()
        if testo:
            out[etichetta] = testo
    return out


def nota(corpo):
    """Il primo paragrafo di prosa di un blocco (2 giri, recuperi, ordine...)."""
    for pezzo in corpo.strip().split("\n\n"):
        pezzo = pezzo.strip()
        if pezzo and not pezzo.startswith("|") and set(pezzo) != {"-"}:
            return " ".join(pezzo.split())
    return ""


# ------------------------------------------------------------------ numeri

PARENTESI = re.compile(r"\([^)]*\)")
A_RIPETIZIONI = re.compile(r"ripetizion|respir|passi")
SERIE = re.compile(r"^\s*(\d+)\s*(?:giri\s*)?×")
SECONDI = re.compile(r"(?:(\d+)\s*-\s*)?(\d+)\s*s\b")
LATO = re.compile(r"per (lato|gamba|braccio)")
GIRI = re.compile(r"(\d+)\s*giri")
RECUPERO_GIRO = re.compile(r"(\d+)\s*s di recupero")


def numeri(quanto, recupero):
    """Da 'quanto' e 'recupero' scritti a mano ai numeri che servono ai timer.

    secondi = 0 vuol dire esercizio a ripetizioni, niente countdown. Il testo
    originale resta e l'app lo mostra sempre.

    ponytail: e' un'euristica sul testo libero, e l'avanzamento e' comunque
    manuale (sezione 2 del piano). Se una scheda nuova non viene letta bene il
    countdown parte sbagliato, ma quello che leggi sotto resta giusto.
    """
    pulito = PARENTESI.sub("", quanto)     # '3 × 3 (5 s di discesa)' e' a ripetizioni
    serie = SERIE.search(pulito)
    secondi = None if A_RIPETIZIONI.search(pulito) else SECONDI.search(pulito)
    riposo = re.search(r"(\d+)\s*s", recupero)
    return {
        "serie": int(serie.group(1)) if serie else 1,
        # del range prende il massimo: e' l'obiettivo, si tocca Fatto prima se cede
        "secondi": int(secondi.group(2)) if secondi else 0,
        "per_lato": bool(LATO.search(pulito)),
        # 'a fine giro' non e' roba dell'esercizio: lo gestisce il blocco
        "recupero_s": 0 if "giro" in recupero or not riposo else int(riposo.group(1)),
    }


def scheda(nome, corpo):
    tab = tabella(corpo)
    fig, vid = FIGURA.search(corpo), VIDEO.search(corpo)
    d = {
        "nome": nome,
        "figura": fig.group(1) if fig else "",
        "quanto": next(iter(tab.values()), ""),
        "recupero": colonna(tab, "recupero"),
        "attrezzi": colonna(tab, "attrezzi"),
        "video": vid.group(1) if vid else "",
    }
    for etichetta, testo in paragrafi(corpo).items():
        if etichetta in PARAGRAFI:
            d[PARAGRAFI[etichetta]] = testo
    return d


SALTA = {"nome", "sigla", "sezione", "blocco", "solo", "quanto", "recupero"}


def eredita(figlia, madre):
    """Le schede che rimandano a un'altra prendono solo quello che non hanno.

    Quanto e recupero non si ereditano mai: sono la prescrizione della seduta,
    e cambiano (il jumping jack e' 45 s nel riscaldamento, 30 s nel finisher).
    """
    for k, v in madre.items():
        if k not in SALTA and not figlia.get(k):
            figlia[k] = v
    figlia["da_sigla"] = madre.get("sigla", "")


# ------------------------------------------------------------------- forza

SESSIONE = re.compile(r"^SESSIONE ([AB])")
BLOCCO = re.compile(r"^BLOCCO (\d)\s*·?\s*(.*)$")
CARD = re.compile(r"^([RABFS]\d)\.\s+(.+)$")
SOLO = re.compile(r"\*\(solo ([AB])\)\*")
VEDI = re.compile(r"\[vedi ([RABFS]\d)\]")


def pulisci(titolo):
    return re.sub(r"\s*—.*$", "", SOLO.sub("", titolo)).strip()


def indice_blocco(corpo):
    """La tabella riassuntiva del blocco: sigla -> quanto/recupero della seduta."""
    out = {}
    for r in celle(corpo)[2:]:
        if len(r) >= 3 and re.fullmatch(r"[RABFS]\d", r[0]):
            out[r[0]] = (r[2], r[3] if len(r) > 3 else "")
    return out


def leggi_forza(testo):
    schede, blocchi = [], {}
    tagli = list(TITOLI.finditer(testo))
    sez, num, indice = "comune", 0, {}

    for i, m in enumerate(tagli):
        fine = tagli[i + 1].start() if i + 1 < len(tagli) else len(testo)
        corpo, titolo = testo[m.end():fine], m.group(2)

        if s := SESSIONE.match(titolo):
            sez = s.group(1)
            continue
        if b := BLOCCO.match(titolo):
            num = int(b.group(1))
            if num in (0, 4):
                sez = "comune"          # riscaldamento e scarico stanno in A e B
            indice = indice_blocco(corpo)
            testo_nota = nota(corpo)
            giri, riposo = GIRI.search(testo_nota), RECUPERO_GIRO.search(testo_nota)
            blocchi[(sez, num)] = {
                "nome": b.group(2), "nota": testo_nota,
                "giri": int(giri.group(1)) if giri else 1,
                "recupero_giro_s": int(riposo.group(1)) if riposo else 0,
            }
            continue
        if not (c := CARD.match(titolo)):
            continue

        sigla = c.group(1)
        d = scheda(pulisci(c.group(2)), corpo)
        solo = SOLO.search(titolo)
        vedi = VEDI.search(corpo)
        d.update(sigla=sigla, sezione=sez, blocco=num,
                 solo=solo.group(1) if solo else "", vedi=vedi.group(1) if vedi else "")
        if sigla in indice and not d["quanto"]:
            d["quanto"], d["recupero"] = indice[sigla]
        schede.append(d)

    per_sigla = {}
    for d in schede:
        per_sigla.setdefault(d["sigla"], []).append(d)
    for d in schede:
        if d["vedi"]:
            madri = per_sigla.get(d["vedi"], [])
            if len(madri) != 1:
                raise Errore(f"{d['sigla']} «{d['nome']}» rimanda a "
                             f"{d['vedi']}, che ha {len(madri)} schede: serve una sigla unica")
            eredita(d, madri[0])
    return schede, blocchi


def seduta_forza(schede, quale):
    """Blocco 0 -> blocchi della sessione -> blocco 4 filtrato. Ordine del file."""
    fuori = []
    for d in schede:
        if d["sezione"] == "comune":
            if d["solo"] and d["solo"] != quale:
                continue
        elif d["sezione"] != quale:
            continue
        fuori.append(d)
    return fuori


# --------------------------------------------------------------- mattutina

ROUTINE = re.compile(r"^M([123])\s*·\s*(.+)$")
LINK = re.compile(r"\[(.+?)\]\(#(.+?)\)")
COMPLETA = re.compile(r"\[Scheda completa\]\(allenamento-forza\.md\)")


def secondi(cella):
    m = re.search(r"(\d+)", cella)
    return int(m.group(1)) if m else 0


def leggi_mattutina(testo):
    routine, carte = {}, {}
    tagli = list(TITOLI.finditer(testo))

    for i, m in enumerate(tagli):
        fine = tagli[i + 1].start() if i + 1 < len(tagli) else len(testo)
        corpo, titolo, liv = testo[m.end():fine], m.group(2), len(m.group(1))

        if liv == 1 and (r := ROUTINE.match(titolo)):
            esercizi, minuti = [], 0
            for riga in celle(corpo)[2:]:
                if not riga[0]:                       # riga del totale
                    minuti = secondi(riga[-1])
                    continue
                link = LINK.search(riga[1])
                if not link:
                    raise Errore(f"M{r.group(1)}, riga {riga[0]}: "
                                 f"«{riga[1]}» non e' un link a una scheda")
                esercizi.append({"chiave": "M:" + link.group(2), "nome": link.group(1),
                                 "quanto": riga[2], "cue": riga[3],
                                 "tempo_s": secondi(riga[4])})
            routine[f"M{r.group(1)}"] = {"tipo": "mattutina", "titolo": r.group(2),
                                         "minuti": minuti, "esercizi": esercizi}
        elif liv == 3:
            d = scheda(titolo, corpo)
            d["completa"] = bool(COMPLETA.search(corpo))
            carte[ancora(titolo)] = d
    return routine, carte


# ------------------------------------------------------------------ regole

def controlla(dati, schede_f):
    for nome, r in dati["sedute"].items():
        if r["tipo"] != "mattutina":
            continue
        if len(r["esercizi"]) > MAX_ESERCIZI_ROUTINE:
            raise Errore(f"{nome}: {len(r['esercizi'])} esercizi, il massimo e' "
                         f"{MAX_ESERCIZI_ROUTINE} (CLAUDE.md sezione 7)")
        durata = max(r["minuti"], round(sum(e["tempo_s"] for e in r["esercizi"]) / 60))
        if durata > MAX_MINUTI_ROUTINE:
            raise Errore(f"{nome}: {durata} minuti, il massimo e' {MAX_MINUTI_ROUTINE} "
                         f"(CLAUDE.md sezione 7)")
        for e in r["esercizi"]:
            if e["chiave"] not in dati["esercizi"]:
                raise Errore(f"{nome}, esercizio «{e['nome']}»: manca la scheda "
                             f"### con ancora #{e['chiave'][2:]} in routine-mattutina.md")

    for quale in ("A", "B"):
        conta = {}
        for d in seduta_forza(schede_f, quale):
            conta[d["blocco"]] = conta.get(d["blocco"], 0) + 1
        for blocco in (1, 2):
            if conta.get(blocco, 0) > MAX_ESERCIZI_BLOCCO:
                raise Errore(f"sessione {quale}, blocco {blocco}: {conta[blocco]} esercizi, "
                             f"il massimo e' {MAX_ESERCIZI_BLOCCO} (CLAUDE.md sezione 7)")

    for chiave, d in dati["esercizi"].items():
        eti = f"{chiave} «{d['nome']}»"
        if not d["figura"]:
            raise Errore(f"{eti}: manca la figura ![...](img/....svg)")
        if not (IMG / d["figura"]).exists():
            raise Errore(f"{eti}: la figura img/{d['figura']} non esiste. "
                         f"Aggiungila a img/genera_figure.py e rigenera")
        richiesti = ["come", "attenzione", "sfruttare"]
        if not (d.get("sigla") or d.get("da_sigla", "")).startswith(("F", "S")):
            richiesti.append("progredire")     # finisher e scarico non progrediscono
        for k in richiesti:
            if not d.get(k):
                etichetta = [e for e, v in PARAGRAFI.items() if v == k][0]
                raise Errore(f"{eti}: manca il paragrafo **{etichetta}.**")


# ------------------------------------------------------------------- build

def costruisci():
    schede_f, blocchi = leggi_forza((BASE / "allenamento-forza.md").read_text(encoding="utf-8"))
    routine, carte_m = leggi_mattutina((BASE / "routine-mattutina.md").read_text(encoding="utf-8"))

    esercizi = {}
    for d in schede_f:
        esercizi[f"{d['sezione']}:{d['sigla']}"] = d
    per_nome = {}
    for d in schede_f:
        per_nome.setdefault(d["nome"].lower(), []).append(d)
    for slug, d in carte_m.items():
        if d.pop("completa"):
            madri = per_nome.get(d["nome"].lower(), [])
            if len(madri) != 1:
                raise Errore(f"«{d['nome']}» rimanda alla scheda completa in "
                             f"allenamento-forza.md, dove ha {len(madri)} corrispondenze")
            eredita(d, madri[0])
        esercizi["M:" + slug] = d

    sedute = dict(routine)
    for quale in ("A", "B"):
        lista = seduta_forza(schede_f, quale)
        sedute[quale] = {
            "tipo": "forza",
            "titolo": "spinta e verticale" if quale == "A" else "trazione, core e L-sit",
            "blocchi": {str(n): b for (s, n), b in blocchi.items() if s in ("comune", quale)},
            "esercizi": [{"chiave": f"{d['sezione']}:{d['sigla']}", "sigla": d["sigla"],
                          "blocco": d["blocco"]} for d in lista],
        }

    for d in esercizi.values():        # dopo tutti gli override di quanto/recupero
        d.update(numeri(d["quanto"], d["recupero"]))
    # la routine prescrive il suo quanto (il gatto-cammello e' 8 in M1 e 6 in M2):
    # i numeri della riga battono quelli della scheda, il recupero resta della scheda
    for r in routine.values():
        for e in r["esercizi"]:
            # .get: se la scheda manca lo dice controlla(), non un KeyError
            e.update(numeri(e["quanto"], esercizi.get(e["chiave"], {}).get("recupero", "")))

    usate = sorted({d["figura"] for d in esercizi.values() if d["figura"]})
    dati = {
        "build": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "sedute": sedute,
        "esercizi": esercizi,
        "figure": {f: (IMG / f).read_text(encoding="utf-8").strip()
                   for f in usate if (IMG / f).exists()},
    }
    controlla(dati, schede_f)
    return dati


def scrivi(dati):
    modello = (QUI / "modello.html").read_text(encoding="utf-8")
    if "/*DATI*/" not in modello:
        raise Errore("modello.html: manca il segnaposto /*DATI*/")
    testo = json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
    html = modello.replace("/*DATI*/", testo.replace("</", "<\\/"))
    (QUI / "index.html").write_text(html, encoding="utf-8")
    return len(html.encode("utf-8"))


def main():
    dati = costruisci()
    _demo(dati)
    peso = scrivi(dati)
    conteggio = " · ".join(f"{n} {len(s['esercizi'])}" for n, s in dati["sedute"].items())
    print(f"{conteggio} · figure {len(dati['figure'])}")
    print(f"index.html scritto, {peso // 1024} KB")


# ---------------------------------------------------------------- autotest

MD = """
# BLOCCO 0 · Riscaldamento (uguale in A e B)

2 minuti.

| # | Esercizio | Quanto |
|---|---|---|
| R1 | Finta | 30 s |

## R1. Finta

![Finta](img/finta.svg)

| Serie × tempo | Recupero | Attrezzi |
|---|---|---|
| 30 s | 15 s | nessuno |

**Come si fa.** Niente. **Poi**: davvero niente.

**Attenzione a.** Nulla.

\U0001f3a5 [Cerca il video](http://x)

# SESSIONE A — prova

## BLOCCO 3 · Finisher A

**2 giri**, 45 s di recupero tra un giro e l'altro.

| # | Esercizio | Quanto |
|---|---|---|
| F1 | Eco | 10 s |

### F1. Eco

→ [vedi R1](#r1-finta). 10 s.

# BLOCCO 4 · Scarico

### S1. Solo in A *(solo A)*

![Solo](img/solo.svg)

| Quanto | Attrezzi |
|---|---|
| 40 s | nessuno |

**Come si fa.** Nulla.
"""


def _autotest():
    assert ancora("Respirazione 90/90") == "respirazione-9090"
    assert ancora("Stretch dei flessori dell'anca") == "stretch-dei-flessori-dellanca"
    assert secondi("75 s") == 75 and secondi("≈ 8 min") == 8

    def n(quanto, recupero=""):
        d = numeri(quanto, recupero)
        return d["serie"], d["secondi"], d["per_lato"], d["recupero_s"]

    assert n("3 × 10-20 s", "60 s") == (3, 20, False, 60)      # del range il massimo
    assert n("2 giri × 20 s per direzione") == (2, 20, False, 0)
    assert n("3 × 20-30 s per lato", "40 s") == (3, 30, True, 40)
    assert n("45 s per lato") == (1, 45, True, 0)
    assert n("60 s statici", "nessuno") == (1, 60, False, 0)
    assert n("2 × 30 s", "15 s tra le due") == (2, 30, False, 15)
    # a ripetizioni: i secondi citati sono per ripetizione, non un countdown
    assert n("8 ripetizioni, 3 s ciascuna") == (1, 0, False, 0)
    assert n("3 × 3 (5 s di discesa)", "90 s") == (3, 0, False, 90)
    assert n("30-40 passi (~60 s)") == (1, 0, False, 0)
    assert n("4 × 6-12", "75 s") == (4, 0, False, 75)
    assert n("2 × 10 per gamba", "60 s") == (2, 0, True, 60)
    assert n("3 × (8 Y + 8 T)", "45 s") == (3, 0, False, 45)
    assert n("6 respiri lenti") == (1, 0, False, 0)
    # il recupero di fine giro appartiene al blocco, non all'esercizio
    assert n("30 s", "45 s a fine giro") == (1, 30, False, 0)
    assert n("30 s", "0 (poi F2)") == (1, 30, False, 0)

    schede, blocchi = leggi_forza(MD)
    per_sigla = {d["sigla"]: d for d in schede}
    assert list(per_sigla) == ["R1", "F1", "S1"], list(per_sigla)
    assert blocchi[("comune", 0)]["nota"] == "2 minuti."
    assert blocchi[("comune", 0)]["giri"] == 1
    assert blocchi[("A", 3)]["nome"] == "Finisher A"
    assert blocchi[("A", 3)]["giri"] == 2
    assert blocchi[("A", 3)]["recupero_giro_s"] == 45

    r1 = per_sigla["R1"]
    assert r1["quanto"] == "30 s" and r1["recupero"] == "15 s"
    # il grassetto a meta' riga non e' un paragrafo
    assert r1["come"].startswith("Niente. **Poi**"), r1["come"]
    assert r1["video"] == "http://x"

    f1 = per_sigla["F1"]                       # eredita figura e testi, non i tempi
    assert f1["figura"] == "finta.svg" and f1["come"] == r1["come"]
    assert f1["quanto"] == "10 s" and f1["recupero"] == ""

    # il blocco 4 e' condiviso ma filtrato, il blocco 0 no
    assert [d["sigla"] for d in seduta_forza(schede, "A")] == ["R1", "F1", "S1"]
    assert [d["sigla"] for d in seduta_forza(schede, "B")] == ["R1"]


def _demo(dati):
    """Gli assert sui file veri: se saltano, si e' rotto qualcosa nelle schede."""
    m1 = dati["sedute"]["M1"]
    assert len(m1["esercizi"]) == 8, len(m1["esercizi"])
    assert dati["esercizi"]["A:A1"]["nome"] == "L-sit", dati["esercizi"]["A:A1"]["nome"]
    assert dati["esercizi"]["A:F1"]["nome"] != dati["esercizi"]["B:F1"]["nome"]
    for chiave, d in dati["esercizi"].items():
        assert d["figura"] in dati["figure"], f"{chiave}: figura non incorporata"
        assert d["come"] and d["attenzione"] and d["sfruttare"], chiave
    # i timer: l'L-sit e' 3 serie da 20 s con 60 s di recupero, i piegamenti
    # sono 4 serie a ripetizioni (nessun countdown)
    assert [dati["esercizi"]["A:A1"][k] for k in ("serie", "secondi", "recupero_s")] == [3, 20, 60]
    assert [dati["esercizi"]["A:A4"][k] for k in ("serie", "secondi")] == [4, 0]
    assert dati["esercizi"]["comune:S2"]["per_lato"] is True
    # la riga della routine ha i suoi numeri: il dead hang mattutino e' 2 × 30 s
    dh = next(e for e in dati["sedute"]["M2"]["esercizi"] if e["nome"] == "Dead hang")
    assert [dh[k] for k in ("serie", "secondi", "recupero_s")] == [2, 30, 15], dh
    assert dati["sedute"]["B"]["blocchi"]["3"]["giri"] == 2
    for quale in ("A", "B"):
        sigle = [e["sigla"] for e in dati["sedute"][quale]["esercizi"]]
        assert sigle[:5] == ["R1", "R2", "R3", "R4", "R5"], sigle[:5]
        assert sigle[-1] == "S3", sigle
    assert [e["sigla"] for e in dati["sedute"]["B"]["esercizi"]][-3:] == ["S4", "S2", "S3"]


if __name__ == "__main__":
    _autotest()
    try:
        main()
    except Errore as e:
        sys.exit(f"\nBUILD FERMATO — {e}\n")
