# Design — Remote und geordnete Zellen

Status: decided · Umsetzung offen

## Context

Entscheidungen D-1–D-6 in [MILE-006](../../../docs/02-Milestones/MILE-006-remote-and-order.md).

## Decisions

- **G5 (D-2, D-3):** Der Kern übernimmt das unveränderte P1.12-Paket wie zuvor P1.11. Der lokale Adapter leitet `/8` bereits weiter, deshalb kommen nur das Paket, die Discovery und die Version hinzu. Bereitstellung durch den Nutzer, Abnahme durch den Agenten über den Connector.
- **Reihenfolge (D-4, D-5):** VP-10 0.10.1 ist ein opt-in-Profil im Paket `vpcells`; die Ausgaben von 0.10.0 werden vor jedem Code gepinnt. `axis_order` ordnet Zeilen und Spalten gleich; die Rückkopplungsmarke ist Text, kein Farbwert.
- **Lesbarkeit (D-6):** Fragen und Antworten werden vor der Durchführung committet; ausgewertet wird je Zustand. Die Ergebnisse sind ein Befund, kein Nachweis von Allgemeingültigkeit.

## Risks

- Bereitstellung hängt an Cloudflare-Zugang und Zeit des Nutzers.
- Wenige Testpersonen: Ergebnisse zeigen nur grobe Fehlleseweisen.
