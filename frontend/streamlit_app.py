import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="PV24 Forecast Prototype", layout="wide")

st.title("PV24 Forecast – локaler Prototyp")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Aktionen")

    run_date = st.text_input("Run-Date (YYYY-MM-DD, leer = heute)", value="")
    if st.button("Run Daily Pipeline"):
        params = {}
        if run_date.strip():
            params["run_date"] = run_date.strip()
        r = requests.post(f"{API_BASE}/jobs/run-daily", params=params, timeout=60)
        if r.status_code != 200:
            st.error(f"Fehler: {r.status_code} – {r.text}")
        else:
            st.success("Pipeline erfolgreich ausgeführt.")
            st.session_state["latest"] = r.json()

    if st.button("Load Latest Output"):
        r = requests.get(f"{API_BASE}/outputs/latest", timeout=30)
        if r.status_code != 200:
            st.error(f"Fehler: {r.status_code} – {r.text}")
        else:
            st.session_state["latest"] = r.json()

with col2:
    st.subheader("Ergebnis")

    data = st.session_state.get("latest")
    if not data:
        st.info("Noch kein Output geladen. Klicke links auf 'Run Daily Pipeline' oder 'Load Latest Output'.")
    else:
        st.caption(data.get("note", ""))

        df = pd.DataFrame(data["points"])
        df["time"] = pd.to_datetime(df["iso_time"])
        df = df.sort_values("time")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### PV Forecast (kW)")
            fig = plt.figure()
            plt.plot(df["time"], df["pv_kw"])
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        with c2:
            st.markdown("### Preis (EUR/kWh) – optional")
            if df["price_eur_per_kwh"].notna().any():
                fig2 = plt.figure()
                plt.plot(df["time"], df["price_eur_per_kwh"])
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig2)
            else:
                st.info("Keine Preise verfügbar (ENTSO-E Key nicht gesetzt / Client ist optional).")

        st.markdown("### Tabelle")
        show_cols = ["time", "pv_kw", "price_eur_per_kwh", "recommendation"]
        st.dataframe(df[show_cols], use_container_width=True)
