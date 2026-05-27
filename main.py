import json
import os
import flet as ft

DATA_FILE = "serien_daten.json"

def main(page: ft.Page):
    try:
        page.title = "Serien Tracker Pro"
        page.scroll = ft.ScrollMode.AUTO

        # --- DATEN LADEN ---
        def laden():
            default_data = {
                "Highschool DxD": {"aktuelle_staffel": 3, "aktuelle_folge": 5, "staffeln": {"1": 12, "2": 12, "3": 12, "4": 13}, "zuletzt_geöffnet": False},
                "One Piece": {"aktuelle_staffel": 15, "aktuelle_folge": 52, "staffeln": {"1": 61, "2": 16, "3": 14, "4": 39, "5": 13, "6": 52, "7": 33, "8": 35, "9": 73, "10": 45, "11": 26, "12": 14, "13": 101, "14": 58, "15": 62, "16": 50, "17": 56, "18": 55, "19": 74, "20": 14, "21": 197, "22": 67}, "zuletzt_geöffnet": True},
                "YU-GI-OH! 5Ds": {"aktuelle_staffel": 1, "aktuelle_folge": 7, "staffeln": {"1": 26, "2": 38, "3": 28, "4": 24}, "zuletzt_geöffnet": False}
            }
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        rohdaten = json.load(f)
                        sortiertes_dict = {}
                        for key in sorted(rohdaten.keys()):
                            sortiertes_dict[key] = rohdaten[key]
                        return sortiertes_dict
                except:
                    return default_data
            return default_data

        data = laden()
        
        aktuelle_serie = list(data.keys())[0] if data else ""
        for k, v in data.items():
            if v.get("zuletzt_geöffnet", False):
                aktuelle_serie = k
                break

        dynamische_felder = []

        # --- SPEICHERN ---
        def speichern():
            try:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            except:
                pass

        # --- NEU: INPUT-FILTER FÜR REINE ZAHLEN ---
        def nur_zahlen_filter(e):
            # Filtert alle Zeichen heraus, die keine Ziffern sind
            gefilterter_text = "".join([char for char in e.control.value if char.isdigit()])
            if e.control.value != gefilterter_text:
                e.control.value = gefilterter_text
                e.control.update()

        # --- REFRESH FÜR DAS DROPDOWN ---
        def dropdown_aktualisieren(neuer_wert):
            dropdown.options = [ft.dropdown.Option(k) for k in data.keys()]
            dropdown.value = neuer_wert
            dropdown.update()

        # --- ANZEIGE AKTUALISIEREN ---
        def update_anzeige():
            nonlocal aktuelle_serie
            loesch_warnung.visible = False
            btn_loeschen_bestaetigen.visible = False
            
            if aktuelle_serie and aktuelle_serie in data:
                s = data[aktuelle_serie]
                status_label.value = f"{aktuelle_serie}\nStaffel {s['aktuelle_staffel']} | Folge {s['aktuelle_folge']}"
                for k in data.keys():
                    data[k]["zuletzt_geöffnet"] = (k == aktuelle_serie)
                speichern()
            else:
                status_label.value = "Keine Serien vorhanden."
            page.update()

        # --- EVENT HANDLER ---
        def serie_wechseln_button(e):
            nonlocal aktuelle_serie
            if dropdown.value:
                aktuelle_serie = dropdown.value
                update_anzeige()

        def loeschen_start_klick(e):
            if not aktuelle_serie or aktuelle_serie not in data: return
            loesch_warnung.visible = True
            btn_loeschen_bestaetigen.visible = True
            page.update()

        def loeschen_bestaetigen_klick(e):
            nonlocal aktuelle_serie
            if not aktuelle_serie or aktuelle_serie not in data: return

            del data[aktuelle_serie]
            speichern()

            aktuelle_serie = list(data.keys())[0] if data else ""
            dropdown_aktualisieren(aktuelle_serie if aktuelle_serie else None)
            update_anzeige()

        def folge_erhoehen(e):
            if not aktuelle_serie or aktuelle_serie not in data: return
            s = data[aktuelle_serie]
            text_st = str(s["aktuelle_staffel"])
            if text_st not in s["staffeln"]: return
            
            if s["aktuelle_folge"] < s["staffeln"][text_st]:
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

        def springe_zu_klick(e):
            if not aktuelle_serie or aktuelle_serie not in data: return
            s = data[aktuelle_serie]
            
            if not jump_st_input.value or not jump_fo_input.value: return
            
            ziel_st = int(jump_st_input.value)
            ziel_fo = int(jump_fo_input.value)

            text_st = str(ziel_st)
            if text_st in s["staffeln"]:
                max_folgen = s["staffeln"][text_st]
                if 1 <= ziel_fo <= max_folgen:
                    s["aktuelle_staffel"] = ziel_st
                    s["aktuelle_folge"] = ziel_fo
                    speichern()
                    
                    jump_st_input.value = ""
                    jump_fo_input.value = ""
                    page.update()
                    
                    update_anzeige()

        def staffeln_generieren(e):
            name = name_input.value.strip()
            if not name or name in data: return
            if not staffeln_input.value: return
            
            anzahl_st = int(staffeln_input.value)
            if anzahl_st <= 0 or anzahl_st > 50: return

            dynamischer_bereich.controls.clear()
            dynamische_felder.clear()

            for i in range(1, anzahl_st + 1):
                # Auch hier binden wir den Filter ein!
                feld = ft.TextField(
                    label=f"Folgen für Staffel {i}", 
                    keyboard_type=ft.KeyboardType.NUMBER, 
                    width=350,
                    on_change=nur_zahlen_filter
                )
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
                    if not feld.value: return
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
            
            temp_sortiert = {}
            for key in sorted(data.keys()):
                temp_sortiert[key] = data[key]
            data.clear()
            data.update(temp_sortiert)
            
            speichern()
            
            nonlocal aktuelle_serie
            aktuelle_serie = name
            
            name_input.value = ""
            staffeln_input.value = ""
            dynamischer_bereich.controls.clear()
            dynamische_felder.clear()
            btn_add.visible = False
            
            dropdown_aktualisieren(name)
            update_anzeige()

        # --- UI STRUKTUR ---
        app_titel = ft.Text("SERIEN TRACKER PRO", size=16, weight=ft.FontWeight.BOLD)
        
        dropdown = ft.Dropdown(
            label="Wähle eine Serie",
            width=350,
            options=[ft.dropdown.Option(k) for k in data.keys()],
            value=aktuelle_serie if aktuelle_serie in data else None
        )

        btn_waehlen = ft.ElevatedButton("Serie laden / wechseln", on_click=serie_wechseln_button, width=350, height=40)
        btn_loeschen_start = ft.ElevatedButton("Serie loeschen 🗑️", on_click=loeschen_start_klick, width=350, height=40)
        loesch_warnung = ft.Text("Wirklich loeschen?", size=14, color="red", weight=ft.FontWeight.BOLD, visible=False)
        btn_loeschen_bestaetigen = ft.ElevatedButton("[ JA - Bestaetigen ]", on_click=loeschen_bestaetigen_klick, width=350, height=40, visible=False)
        status_label = ft.Text(value="", size=20)
        
        btn_vor = ft.ElevatedButton("Gesehen >>", on_click=folge_erhoehen, width=350, height=50)
        btn_zurueck = ft.ElevatedButton("<< Zurück", on_click=folge_zurueck, width=350, height=50)

        # HIER DIE GEFILTERTEN JUMP-INPUTS: on_change blockiert alles außer Zahlen
        jump_st_input = ft.TextField(
            label="St.", keyboard_type=ft.KeyboardType.NUMBER, width=80, 
            text_align=ft.TextAlign.CENTER, on_change=nur_zahlen_filter
        )
        jump_fo_input = ft.TextField(
            label="Flg.", keyboard_type=ft.KeyboardType.NUMBER, width=80, 
            text_align=ft.TextAlign.CENTER, on_change=nur_zahlen_filter
        )
        btn_jump = ft.ElevatedButton("Go 🚀", on_click=springe_zu_klick, width=160, height=50)
        
        jump_row = ft.Row(
            controls=[jump_st_input, jump_fo_input, btn_jump],
            width=350,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        trenner = ft.Text("----------------------------------------")
        add_titel = ft.Text("Neue Serie hinzufügen:", size=16, weight=ft.FontWeight.BOLD)
        name_input = ft.TextField(label="Serienname", width=350)
        
        # AUCH HIER: Der Filter für das "Anzahl Staffeln gesamt"-Feld
        staffeln_input = ft.TextField(
            label="Anzahl Staffeln gesamt", keyboard_type=ft.KeyboardType.NUMBER, 
            width=350, on_change=nur_zahlen_filter
        )
        
        btn_generate = ft.ElevatedButton("Folgen-Felder anzeigen", on_click=staffeln_generieren, width=350, height=40)
        dynamischer_bereich = ft.Column()
        btn_add = ft.ElevatedButton("Serie speichern", on_click=neue_serie_speichern, width=350, height=50, visible=False)

        page.add(
            app_titel, dropdown, btn_waehlen, btn_loeschen_start, loesch_warnung, 
            btn_loeschen_bestaetigen, status_label, btn_vor, btn_zurueck, jump_row, trenner, 
            add_titel, name_input, staffeln_input, btn_generate, dynamischer_bereich, btn_add
        )
        
        update_anzeige()

    except Exception as e:
        page.clean()
        page.add(ft.Text(f"Fehler:\n{str(e)}", color="red"))
        page.update()

ft.app(target=main)
