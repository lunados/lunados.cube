# MILE-011 — Sichtprüfung der Herkunftslinie (TASK-068)

Stand: 2026-11-02 · Profil `P2-VP-MIGRATION/0.7.6` · Bilder aus den Vektoren OL-02, OL-03a/b, OL-05 und OL-11 (synthetisch, keine Kundendaten).

Kurze angeleitete Prüfung (D-8), keine Lesbarkeitsstudie. Jede Frage mit **ja** oder **nein** beantworten, bei „nein“ ein Satz dazu. Erst die Bilder ansehen, dann die Legende lesen.

| Bild | Inhalt |
|---|---|
| [A1-declared.svg](A1-declared.svg) | `api → db`, deklariert |
| [A2-derived.svg](A2-derived.svg) | dieselbe Kante, abgeleitet aus s-1 und s-2 |
| [B-mixed-1.svg](B-mixed-1.svg), [B-mixed-2.svg](B-mixed-2.svg) | eine Aussagenmenge mit deklariert, Herkunft unbekannt und nicht gebunden |
| [C-aggregated.svg](C-aggregated.svg) | Verdichtung aus lunados.lib (MILE-007): abgeleitete Kante mit Quellen |
| [D-german.svg](D-german.svg) | A2 mit `locale de` |

## Fragen

| Nr. | Frage | Antwort |
|---|---|---|
| S-1 | A1 neben A2: Siehst du **ohne die Legende**, dass A2 nicht als festgelegte Beziehung gemeint ist? | **ja** |
| S-2 | A2 und B-mixed-1: Lassen sich **gestrichelt** (abgeleitet) und **gepunktet** (unbekannt oder nicht gebunden) sicher unterscheiden? | **ja** |
| S-3 | Ist der Herkunftstext an jeder Kante **vollständig lesbar** (nichts abgeschnitten, nichts überdeckt)? | **ja** |
| S-4 | C-aggregated: Ist klar, **worauf** die abgeleitete Kante beruht? | **ja** |
| S-5 | Legende: Die Überschrift „ORIGIN · declared assertions · no truth or authority claim“ steht direkt über „solid · declared“. Ist das **in Ordnung** (nein = als Doppelbedeutung ändern; dann neue G5-Bereitstellung)? | **ja** |
| S-6 | D-german: Sind die deutschen Texte verständlich, und ist die **englische** Legendenüberschrift dort in Ordnung (der Lauf meldet `VP07_LOCALE_FALLBACK`)? | **ja** |

## Auswertung

Antworten des Nutzers am 2026-11-02: **S-1 bis S-6 ja**. Kein Befund; 0.7.6 bleibt unverändert, keine neue G5-Bereitstellung. Die englische Legendenüberschrift unter `locale de` (`VP07_LOCALE_FALLBACK`) und das Wort „declared“ in der Legendenüberschrift sind damit bewusst angenommen.
