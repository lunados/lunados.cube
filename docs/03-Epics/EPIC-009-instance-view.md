# EPIC-009 — Instanzsicht

Status: done · Milestone: [MILE-009](../02-Milestones/MILE-009-instance-view.md) · Voraussetzung: [EPIC-008](EPIC-008-control-flow.md)

## Ergebnis

Deklarierte Prozessspuren lassen sich je Instanz lesen: welcher Pfad genommen wurde, welche Eingänge eines Joins da sind und welcher Token aus einer fremden Instanz stammt. Das Urteil kommt aus lunados.lib, die Sicht zeichnet es.

## Umfang

- Paket VP-11 `cube.instances` (P2);
- G6-Anbindung (lokal);
- kurze Sichtprüfung.

Keine neue Prüfsemantik, keine Änderung an P0, P1, VP-07–VP-10 oder lunados.lib-Einträgen.

## Akzeptanz

- BPMN-01/02/03 sind als Instanzsicht lesbar; Zustände unterscheiden sich ohne Farbe.
- Ohne LIB-Ergebnis zeigt die Sicht „nicht geprüft“, nie ein Urteil.
- Vorhandene Printer byte-gleich.

## Stories

- [US-028 — Instanz und genommenen Pfad sehen](../04-US/US-028-instance-path-view.md)
- [US-029 — Join je Eingang sehen](../04-US/US-029-join-input-view.md)
