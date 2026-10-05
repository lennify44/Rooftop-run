# Rooftop Run

Ein 3D-Parkour-Lauf aus der Ich-Perspektive über die Dächer einer Stadt bei Sonnenuntergang. Neun Abschnitte mit
Säulen, Balken, beweglichen Platten, Wandlauf, Kamin, Sprungpads und einem Rutschdach führen zum goldenen Dach.
Wer fällt, startet am letzten Checkpoint neu.

Alles steckt in einer einzigen Datei: `index.html` im Browser öffnen und losspielen. Keine Installation, kein Build.
Läuft am Rechner mit Maus und Tastatur und am Handy mit Touch-Steuerung.

## Steuerung

| Tastatur / Maus | Touch | Aktion |
|---|---|---|
| W A S D | linker Daumen: irgendwo links ziehen | laufen |
| Maus (oder Pfeiltasten) | rechter Daumen: ziehen | umschauen |
| Shift | Stick bis zum Rand schieben | sprinten |
| Leertaste | Jump | springen (halten = volle Höhe) |
| C | Slide | beim Sprinten rutschen, sonst ducken |
| W + Shift in der Luft an einer Wand | Stick nach vorn am Rand, an einer Wand | Wandlauf |
| Leertaste in der Luft an einer Wand | Jump an einer Wand | Wandsprung |
| S in der Luft | Stick nach hinten | in der Luft bremsen |
| R | R | zurück zum Checkpoint |
| P / Esc | II | Pause |
| M | – | Ton an/aus |
| F2 | – | Maus-Check (zeigt, was der Browser an Mausbewegung liefert) |

- **Maussteuerung:** „Capture“ fängt den Mauszeiger ein. Lässt der Browser das nicht zu, schaltet das Spiel selbst auf
  „Follow cursor“ um: Die Ansicht folgt dem Zeiger, am Bildschirmrand dreht sie weiter.
- **Handy:** Auf Android geht das Spiel beim Tippen auf Play in den Vollbildmodus und quer. Auf dem iPhone über
  Teilen → Zum Home-Bildschirm für Vollbild.
- **Übungsmodus:** Im Menü an jedem Checkpoint starten (zählt nicht als Bestzeit).
- Bestzeit, Zwischenzeiten und ein Geist des besten Laufs werden im Browser gespeichert (localStorage).

## Tests

`tests/run.sh` spielt die Strecke in einem unsichtbaren Firefox (Selenium) durch: Ein Bot springt jeden Abschnitt mit
der echten Spielphysik, danach werden Checkpoints, Ziel, Bestzeit, Respawn, Übungsmodus, Pause und die Touch-Steuerung
geprüft. Beim ersten Lauf legt das Skript eine Python-Umgebung unter `~/.cache/rooftop-run-tests` an.

Die Lücken der Strecke sind gegen gemessene Sprungweiten gesetzt (Kommentar über dem Streckenaufbau in `index.html`).
