import streamlit as st
import pandas as pd
import os
from io import BytesIO
import base64
from collections import defaultdict, Counter
from datetime import datetime

# 📥 Daten aus Excel laden
def load_data():
    if os.path.exists("rezepte.xlsx"):
        return pd.read_excel("rezepte.xlsx", sheet_name="Gerichte")
    else:
        return pd.DataFrame(columns=["Gericht", "Kategorie", "Zutaten", "Zubereitungszeit", "Quelle"])

def save_data(df):
    df.to_excel("rezepte.xlsx", sheet_name="Gerichte", index=False)

# 📦 Kategorien für Zutaten
kategorien_mapping = {
    "Banane": "🥝 Obst",
    "Apfel": "🥝 Obst",
    "Karotte": "🥕 Gemüse",
    "Zucchini": "🥕 Gemüse",
    "Milch": "🥛 Milchprodukte",
    "Joghurt": "🥛 Milchprodukte",
    "Hähnchen": "🥩 Fleisch",
    "Rindfleisch": "🥩 Fleisch",
    "Eier": "🥚 Eier",
    "Haferflocken": "🌾 Getreide",
    "Nudeln": "🌾 Getreide",
}

def get_kategorie(zutat):
    for key, value in kategorien_mapping.items():
        if key.lower() in zutat.lower():
            return value
    return "📦 Sonstiges"

# 🎨 HTML für Wochenplan + Einkaufsliste mit A4 Styling
def build_html(wochenplan, rezepte):
    today_str = datetime.now().strftime("Stand: %d. %B %Y")
    tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    mahlzeiten = ["Frühstück", "Mittagessen", "Snack", "Abendessen", "To-Go"]
    icons = {"Frühstück": "🥣", "Mittagessen": "🍝", "Snack": "🍎", "Abendessen": "🍽️", "To-Go": "🎒"}

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm 1.5cm;
            }}
            body {{
                font-family: Comic Sans MS, cursive, sans-serif;
                color: #333;
            }}
            header {{
                text-align: right;
                font-size: 0.9em;
                color: #888;
                margin-bottom: 10px;
            }}
            h1 {{
                text-align: center;
                color: #ff6f61;
                margin-top: 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background-color: #ffccbc;
                color: #fff;
                padding: 8px;
                border: 1px solid #ffab91;
            }}
            td {{
                border: 1px solid #ffccbc;
                padding: 8px;
                vertical-align: top;
                background-color: #fff3e0;
                font-size: 0.95em;
            }}
            h2 {{
                color: #4caf50;
                margin-top: 30px;
                page-break-before: always;
            }}
            h3 {{
                color: #2e7d32;
                margin-top: 15px;
            }}
            ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            li {{
                background: #e8f5e9;
                margin: 5px 0;
                padding: 6px;
                border-radius: 4px;
            }}
            footer {{
                position: fixed;
                bottom: 1cm;
                width: 100%;
                text-align: center;
                font-size: 0.8em;
                color: #aaa;
            }}
        </style>
    </head>
    <body>
        <header>{today_str}</header>
        <h1>🍽️ Knuppis Wochenplan</h1>
        <table>
            <tr>
    """
    for tag in tage:
        html += f"<th>{tag}</th>"
    html += "</tr>"

    for m in mahlzeiten:
        html += "<tr>"
        for tag in tage:
            gericht = wochenplan[tag][m]
            if gericht and gericht != "-":
                row = rezepte[rezepte["Gericht"] == gericht]
                zeit = row["Zubereitungszeit"].values[0] if not row.empty else "-"
                quelle = row["Quelle"].values[0] if not row.empty else "-"
                html += f"<td><b>{icons[m]} {gericht}</b><br><small>⏱️ {zeit}<br>📖 {quelle}</small></td>"
            else:
                html += "<td>-</td>"
        html += "</tr>"
    html += "</table>"

    # 🛒 Einkaufsliste
    zutaten = []
    for tag in tage:
        for m in mahlzeiten:
            gericht = wochenplan[tag][m]
            if gericht and gericht != "-":
                row = rezepte[rezepte["Gericht"] == gericht]
                if not row.empty:
                    zutaten_str = row["Zutaten"].values[0]
                    zutaten += [z.strip() for z in zutaten_str.split(";") if z.strip()]

    zutaten_counter = Counter(zutaten)
    kategorien_dict = defaultdict(list)
    for zutat, count in zutaten_counter.items():
        kategorie = get_kategorie(zutat)
        kategorien_dict[kategorie].append((zutat, count))

    html += """
        <h2>🛒 Einkaufsliste</h2>
    """
    for kategorie, items in sorted(kategorien_dict.items()):
        html += f"<h3>{kategorie}</h3><ul>"
        for zutat, count in items:
            menge_str = f" ({count}x)" if count > 1 else ""
            html += f"<li>✅ {zutat}{menge_str}</li>"
        html += "</ul>"

    html += """
        <footer> Wochenplaner – Seite 1</footer>
    </body>
    </html>
    """
    return html

# 📄 HTML → Base64 PDF
def html_to_base64_pdf(html):
    b64 = base64.b64encode(html.encode()).decode()
    return f"data:text/html;base64,{b64}"

# 📅 App-Logik
rezepte = load_data()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
mahlzeiten = ["Frühstück", "Mittagessen", "Snack", "Abendessen", "To-Go"]

st.title("🍽️ Knuppis Wochenplaner")

tab1, tab2, tab3, tab4 = st.tabs(["📖 Rezepte", "🗓️ Wochenplan", "📥 PDF Download", "➕ Neues Rezept"])

# 📖 Tab 1 – Rezepte & Löschen
with tab1:
    st.header("📖 Rezept-Explorer & Verwaltung")
    if rezepte.empty:
        st.info("ℹ️ Noch keine Rezepte vorhanden.")
    else:
        kf = st.selectbox("Kategorie", ["Alle"] + sorted(rezepte["Kategorie"].dropna().unique()))
        df = rezepte.copy()
        if kf != "Alle":
            df = df[df["Kategorie"] == kf]
        st.dataframe(df, use_container_width=True)

        st.subheader("🗑️ Rezept löschen")

        # 👉 Dropdown mit Platzhalter
        rezepte_liste = ["--- Bitte wählen ---"] + rezepte["Gericht"].tolist()
        zu_loeschen = st.selectbox("Wähle ein Rezept zum Löschen:", rezepte_liste)

        # 👉 Löschen nur aktiv, wenn ein Rezept gewählt ist
        if zu_loeschen != "--- Bitte wählen ---":
            if st.button("❌ Löschen"):
                if zu_loeschen in rezepte["Gericht"].values:
                    rezepte = rezepte[rezepte["Gericht"] != zu_loeschen]
                    save_data(rezepte)
                    st.success(f"✅ Rezept '{zu_loeschen}' wurde gelöscht!")
                    st.rerun()
                else:
                    st.error("⚠️ Dieses Rezept existiert nicht mehr.")
        else:
            st.warning("⚠️ Bitte wähle ein Rezept aus, um es zu löschen.")


# 🗓️ Tab 2
with tab2:
    st.header("🗓️ Wochenplan erstellen")
    wochenplan = {}
    for tag in tage:
        st.subheader(tag)
        wochenplan[tag] = {}
        for m in mahlzeiten:
            if not rezepte.empty:
                gerichte_kat = rezepte[rezepte["Kategorie"] == m]["Gericht"].dropna().tolist()
                optionen = ["-"] + gerichte_kat if gerichte_kat else ["-"]
            else:
                optionen = ["-"]
            sel = st.selectbox(f"{m} auswählen", optionen, key=f"{tag}_{m}")
            wochenplan[tag][m] = sel

# 📥 Tab 3
with tab3:
    st.header("📥 Übersicht Wochenplan & Einkaufsliste")
    html = build_html(wochenplan, rezepte)
    st.markdown(html, unsafe_allow_html=True)

    pdf_url = html_to_base64_pdf(html)
    st.markdown(
        f'<a href="{pdf_url}" download="Wochenplan_A4.html" target="_blank" style="display: inline-block; margin-top: 20px; background-color: #4caf50; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">📥 Download DIN A4 PDF</a>',
        unsafe_allow_html=True
    )

# ➕ Tab 4
with tab4:
    st.header("➕ Neues Rezept hinzufügen")
    with st.form("neues_rezept_formular"):
        gericht_name = st.text_input("Gerichtname")
        kategorie = st.selectbox("Kategorie", mahlzeiten)
        zutaten = st.text_area("Zutaten (mit Semikolon getrennt)")
        zubereitungszeit = st.text_input("Zubereitungszeit (z.B. 15 Minuten)")
        quelle = st.text_input("Quelle (optional)", placeholder="z.B. GU Breifrei Kochbuch")
        submitted = st.form_submit_button("✅ Rezept hinzufügen")

    if submitted:
        if gericht_name and kategorie and zutaten:
            new_entry = pd.DataFrame([{
                "Gericht": gericht_name.strip(),
                "Kategorie": kategorie,
                "Zutaten": zutaten.strip(),
                "Zubereitungszeit": zubereitungszeit.strip(),
                "Quelle": quelle.strip()
            }])
            rezepte = pd.concat([rezepte, new_entry], ignore_index=True)
            save_data(rezepte)
            rezepte = load_data()
            st.success(f"🎉 Rezept '{gericht_name}' wurde hinzugefügt!")
        else:
            st.error("⚠️ Bitte fülle alle Pflichtfelder aus.")
