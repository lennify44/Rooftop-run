# Rooftop Run

Ein 3D-Parkour-Lauf in dritter Person oder aus der Ich-Perspektive über die Dächer einer Stadt bei Sonnenuntergang. Neun Abschnitte mit
Säulen, Balken, beweglichen Platten, Wandlauf, Kamin, Sprungpads und einem Rutschdach führen zum goldenen Dach.
Wer fällt, startet am letzten Checkpoint neu.

Alles steckt in einer einzigen Datei: `index.html` im Browser öffnen und losspielen. Keine Installation, kein Build.
Läuft am Rechner mit Maus und Tastatur und am Handy mit Touch-Steuerung.

## Steuerung

Sprung und Rutschen liegen auf denselben Tasten wie in Fire Escape (dessen Dash-Tasten rutschen hier).
Nach vorn wird immer gerannt.

| Tastatur / Maus | Gamepad | Touch | Aktion |
|---|---|---|---|
| W A S D | linker Stick, Steuerkreuz | linke Hälfte: Daumen auflegen und ziehen (Stick wandert mit) | laufen; nach vorn rennen |
| Maus, Pfeiltasten | rechter Stick | rechte Hälfte ziehen | umschauen |
| Leertaste, Z, C, J | A, Y | rechte Hälfte tippen (oberer Streifen schaut nur) | springen – kurz tippen = Hüpfer, halten = hoch; an einer Wand in der Luft: Wandsprung |
| X, Shift, K | B, X, RB, RT | Slide-Kreis | beim Rennen rutschen, im Stand ducken |
| Sprung während des Rutschens | | Daumen vom Slide-Kreis auf die rechte Hälfte rollen | Slide-Sprung, behält das Tempo |
| W in der Luft an der rosa Wand | Stick nach vorn | Stick nach vorn | Wandlauf |
| S in der Luft | Stick zurück | Stick zurück | in der Luft bremsen |
| V | LB, rechter Stick drücken | Cam | dritte Person / Ich-Perspektive |
| R | Select | R | zurück zum Checkpoint |
| P / Esc | Start | II | Pause |
| M | – | – | Ton an/aus |
| F2 | – | – | Maus-Check (zeigt, was der Browser an Mausbewegung liefert) |

- **Dritte Person** ist Standard: Die Kamera hängt hinter dem Läufer und rückt näher, statt durch Wände zu gehen.
  Ein dunkler Fleck unter dem Läufer zeigt, wo ein Sprung landet. Im Menü: Kamera, Blickwinkel (FOV) und
  invertierte Auf-und-ab-Steuerung.
- **Laternen:** In jedem Abschnitt hängt eine Papierlaterne dort, wo nur ein voller, gut gezielter Sprung hinkommt.
  Gezählt wird pro Lauf; das Menü zeigt, wie viele man über alle Läufe gefunden hat.
- **Maussteuerung:** „Capture“ fängt den Mauszeiger ein. Lässt der Browser das nicht zu oder hält er den Zeiger nicht
  wirklich fest (Firefox auf manchen Linux-Desktops meldet dann die Zeigerposition statt der Bewegung, und die Kamera
  schaut nur noch nach oben), schaltet das Spiel selbst auf „Follow cursor“ um: Die Ansicht folgt dem Zeiger, am linken
  und rechten Bildschirmrand dreht sie weiter.
- **Handy:** Seite im Handy-Browser öffnen: https://lennify44.github.io/Rooftop-run/ – Touch-Steuerung schaltet sich
  von selbst ein. Auf Android geht das Spiel beim Tippen auf Play in den Vollbildmodus und quer.
- **Als App installieren:** Android (Chrome): Menü → „Zum Startbildschirm hinzufügen“ bzw. „App installieren“.
  iPhone (Safari): Teilen → „Zum Home-Bildschirm“. Danach startet Rooftop Run mit eigenem Symbol im Vollbild und quer.
- **Übungsmodus:** Im Menü an jedem Checkpoint starten (zählt nicht als Bestzeit).
- Bestzeit, Zwischenzeiten und ein Geist des besten Laufs werden im Browser gespeichert (localStorage).

## Tests

`tests/run.sh` spielt die Strecke in einem unsichtbaren Firefox (Selenium) durch: Ein Bot springt jeden Abschnitt mit
der echten Spielphysik, danach werden Checkpoints, Ziel, Bestzeit, Respawn, Übungsmodus, Pause und die Touch-Steuerung
geprüft (auch über Firefox' echte Touch-Eingabe mit zwei Fingern gleichzeitig, inklusive Slide-Sprung per Daumenrollen), dass jede Laterne erreichbar ist, dazu die Maussteuerung mit Firefox' eigenem Eingabeweg (auch ein „Capture“, das den Zeiger nicht festhält).
Beim ersten Lauf legt das Skript eine Python-Umgebung unter `~/.cache/rooftop-run-tests` an.

`tests/real-mouse.sh` prüft die Maus am echten GNOME-Desktop: Firefox öffnet sich im Vollbild und der echte Mauszeiger
wird bewegt. Nur starten, wenn man am Rechner sitzt, und die Maus bis zum Ende nicht anfassen.

Die Lücken der Strecke sind gegen gemessene Sprungweiten gesetzt (Kommentar über dem Streckenaufbau in `index.html`).

Das App-Symbol (`icons/`) zeichnet `python3 tools/make-icons.py` (braucht Pillow).
