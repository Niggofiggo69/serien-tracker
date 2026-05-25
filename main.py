import json
import os
import flet as ft

DATA_FILE = "serien_daten.json"

def main(page: ft.Page):
    try:
        page.title = "Serien Tracker Pro"
        page.scroll = ft.ScrollMode.AUTO
        
        # FIX FÜR PADDING IN FLET 0.85.1:
        # Wir nutzen page.window_padding oder setzen es direkt als Zahl/Kombination,
        # um den alten Bug komplett zu umgehen.
        page.padding = 10 

        # --- DATEN LADEN ---
        def laden():
            default_data = {
                "One Piece": {
                    "aktuelle_staffel": 15, "aktuelle_folge": 52,
                    "staffeln": {"1": 61, "2": 16, "3": 14, "4": 39, "5": 13, "6": 52, "7": 33, "8": 35, "9": 73, "10": 45, "11": 26, "12": 14, "13": 101, "14": 58, "15": 62, "16": 50, "17": 56, "18": 55, "19": 74, "20": 14, "21": 197, "22": 67},
                    "zuletzt_geöffnet": True
                },
                "YU-GI-OH! 5Ds": {
                    "aktuelle_staffel": 1, "aktuelle_folge": 7,
                    "staffeln": {"1": 26, "2": 38, "3": 28, "4": 24},
                    "zuletzt_geöffnet": False
                },
                "Highschool DxD": {
                    "aktuelle_staffel": 3, "aktuelle_folge": 5,
                    "staffeln": {"1": 12, "2": 12, "3": 12, "4": 13},
                    "zuletzt_geöffnet": False
                }
            }
            try:
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
            except:
                return default_data
            return default_data

        data = laden()
        if not isinstance(data, dict) or not data:
            data = {"One Piece": {"aktuelle_staffel": 1, "aktuelle_folge": 1, "staffeln": {"1": 20}, "zuletzt_geöffnet": True}}
            
        # --- FEATURE: ZULETZT GESCHAUTE SERIE ERMITTELN ---
        aktuelle_serie = list(data.keys())[0]
        for k, v in data.items():
            if v.get("zuletzt_geöffnet", False):
                aktuelle_serie = k
                break

        dynamische_felder = []

        # --- DATEN SPEICHERN ---
        def speichern():
            try:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            except:
                pass

        # --- ANZEIGE AKTUALISIEREN ---
        def update_anzeige():
            nonlocal aktuelle_serie
            btn_loeschen.text = ""
            btn_loeschen.icon = ft.icons.DELETE_OUTLINE
            btn_loeschen.bgcolor = ft.colors.RED_50
            
            if aktuelle_serie and aktuelle_serie in data:
                s = data[aktuelle_serie]
                status_label.value = f"{aktuelle_serie}\n\nStaffel {s['aktuelle_staffel']}  |  Folge {s['aktuelle_folge']}"
                
                # Zuletzt geöffneten Status in den Daten aktualisieren
                for k in data.keys():
                    data[k]["zuletzt_geöffnet"] = (k == aktuelle_serie)
                speichern()
            else:
                status_label.value = "Keine Serien vorhanden."
            page.update()

        def serie_wechseln_button(e):
            nonlocal aktuelle_serie
            if dropdown.value:
                aktuelle_serie = dropdown.value
                update_anzeige()

        # --- SERIE LÖSCHEN ---
        def serie_loeschen_klick(e):
            nonlocal aktuelle_serie
            if not aktuelle_serie or aktuelle_serie not in data: return

            if btn_loeschen.text == "":
                btn_loeschen.text = "Wirklich löschen? [JA]"
                btn_loeschen.icon = ft.icons.DELETE_FOREVER
                btn_loeschen.bgcolor = ft.colors.RED_700
                page.update()
            else:
                del data[aktuelle_serie]
                speichern()

                dropdown.options = [ft.dropdown.Option(k) for k in data.keys()]
                
                if data:
                    aktuelle_serie = list(data.keys())[0]
                    dropdown.value = aktuelle_serie
                else:
                    aktuelle_serie = ""
                    dropdown.value = None
                
                update_anzeige()

        def folge_erhoehen(e):
            if not aktuelle_serie or aktuelle_serie not in data: return
            s = data[aktuelle_serie]
            akt_st = str(s["aktuelle_staffel"])
            
            if akt_st not in s["staffeln"]: return
            max_folgen = s["staffeln"][akt_st]

            if s["aktuelle_folge"] < max_folgen:
                s["aktuelle_folge"] += 1
            elif str(s["aktuelle_staffel"] + 1) in s["staffeln"]:
                s["aktuelle_staffel"] += 1
                s["aktuelle_folge"] = 1
            
            speichern()
            update_anzeige()

        def folge_zurueck(e):
            if not aktuelle_serie or aktuelle_serie not in data: return
            s = data[aktuelle_serie]
            
            if s["aktuelle_folge"] > 1:
                s["aktuelle_folge"] -= 1
            elif s["aktuelle_staffel"] > 1:
                prev_st = str(s["aktuelle_staffel"] - 1)
                if prev_st in s["staffeln"]:
                    s["aktuelle_staffel"] -= 1
                    s["aktuelle_folge"] = s["staffeln"][prev_st]
            
            speichern()
            update_anzeige()

        def staffeln_generieren(e):
            name = name_input.value.strip()
            if not name or name in data: return
            try:
                anzahl_st = int(staffeln_input.value)
                if anzahl_st <= 0 or anzahl_st > 50: return
            except:
                return

            dynamischer_bereich.controls.clear()
            dynamische_felder.clear()

            for i in range(1, anzahl_st + 1):
                feld = ft.TextField(label=f"Folgen für Staffel {i}", keyboard_type=ft.KeyboardType.NUMBER, width=350)
                dynamische_felder.append((str(i), feld))
                dynamischer_bereich.controls.append(feld)
            
            btn_add.visible = True
            page.update()

        def neue_serie_speichern(e):
            name = name_input.value.strip()
            if not name or name in data: return
            
            staffel_mapping = {}
            try:
                for st_nr, feld in dynamische_felder:
                    folgen = int(feld.value)
                    if folgen <= 0: return
                    staffel_mapping[st_nr] = folgen
            except:
                return
            
            data[name] = {
                "aktuelle_staffel": 1,
                "aktuelle_folge": 1,
                "staffeln": staffel_mapping,
                "zuletzt_geöffnet": True
            }
            speichern()
            
            dropdown.options.append(ft.dropdown.Option(name))
            dropdown.value = name
            nonlocal aktuelle_serie
            aktuelle_serie = name
            
            name_input.value = ""
            staffeln_input.value = ""
            dynamischer_bereich.controls.clear()
            dynamische_felder.clear()
            btn_add.visible = False
            
            update_anzeige()

        # UI Elemente Hauptseite
        dropdown = ft.Dropdown(
            label="Wähle eine Serie",
            width=350,
            options=[ft.dropdown.Option(k) for k in data.keys()],
            value=aktuelle_serie
        )

        btn_waehlen = ft.ElevatedButton("Serie laden / wechseln", on_click=serie_wechseln_button, width=280, height=40)
        
        btn_loeschen = ft.IconButton(
            icon=ft.icons.DELETE_OUTLINE,
            icon_color=ft.colors.RED_900,
            bgcolor=ft.colors.RED_50,
            on_click=serie_loeschen_klick,
            width=60,
            height=40
        )

        status_label = ft.Text(value="", size=20, text_align=ft.TextAlign.CENTER)
        status_container = ft.Container(content=status_label, padding=20, border_radius=10, width=350, height=150)
        btn_zurueck = ft.ElevatedButton("<< Zurück", on_click=folge_zurueck, width=160, height=50)
        btn_vor = ft.ElevatedButton("Gesehen >>", on_click=folge_erhoehen, width=160, height=50)

        name_input = ft.TextField(label="Serienname", width=350)
        staffeln_input = ft.TextField(label="Anzahl Staffeln gesamt", keyboard_type=ft.KeyboardType.NUMBER, width=350)
        btn_generate = ft.ElevatedButton("Folgen-Felder anzeigen", on_click=staffeln_generieren, width=350, height=40)
        dynamischer_bereich = ft.Column(spacing=10)
        btn_add = ft.ElevatedButton("Serie endgültig speichern", on_click=neue_serie_speichern, width=350, height=50, visible=False)

        # FIX FÜR ANDROID-LEISTE: Ein schicker Header-Container ganz oben, 
        # der 40 Pixel hoch ist und die Android-Statusleiste elegant nach unten drückt.
        header_puffer = ft.Container(
            content=ft.Text("SERIEN TRACKER PRO", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_GREY_400),
            alignment=ft.alignment.center,
            height=40,
            margin=0
        )

        # Layout aufbauen
        page.add(
            header_puffer, # Fängt die Statusleiste ab!
            dropdown,
            ft.Row([btn_waehlen, btn_loeschen], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            status_container,
            ft.Row([btn_zurueck, btn_vor], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Text("Neue Serie hinzufügen:", size=16, weight=ft.FontWeight.BOLD),
            name_input,
            staffeln_input,
            btn_generate,
            dynamischer_bereich,
            ft.Container(height=10),
            btn_add
        )
        
        if aktuelle_serie:
            s = data[aktuelle_serie]
            status_label.value = f"{aktuelle_serie}\n\nStaffel {s['aktuelle_staffel']}  |  Folge {s['aktuelle_folge']}"
        
        page.update()

    except Exception as e:
        page.clean()
        page.add(ft.Text(f"Kritischer Flet-Fehler abgefangen:\n\n{str(e)}", color="red", size=16))
        page.update()

ft.app(target=main)
