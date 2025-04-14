# app_streamlit.py
import streamlit as st
import pandas as pd
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import json

# Importuj logikę z twoich modułów
from utils import (
    load_items_from_csv,
    get_example_items_small,
    get_example_items_large,
    # generate_random_items, # Już niepotrzebne tutaj
    measure_time
)
from algorithms.greedy import *
from algorithms.brute_force import brute_force_knapsack
from algorithms.dynamic import dynamic_programming_knapsack
from algorithms.backtracking import backtracking_knapsack
from algorithms.mkp_backtracking import mkp_backtracking_knapsack
from algorithms.mkp_dynamic_m2 import mkp_dynamic_programming_m2

# Importuj (zmodyfikowane) funkcje do wykresów
# Upewnij się, że te funkcje ZWRACAJĄ figury Matplotlib
from analysis.comparison import plot_comparison, plot_scalability

# --- Funkcje pomocnicze do wyświetlania w Streamlit (bez zmian) ---

def display_01_results(algo_name, result_tuple, exec_time):
    """Wyświetla wyniki algorytmu 0/1 w Streamlit."""
    st.subheader(f"Wyniki: {algo_name}")
    if result_tuple is None:
        status = "Błąd" if exec_time == -1 else "Pominięto" if exec_time == -2 else "Brak wyniku"
        st.warning(f"Status: {status}")
        if exec_time >= 0 and status == "Błąd": st.write(f"(Czas do błędu: {exec_time:.6f} s)")
        return

    value, weight, items = result_tuple
    item_ids = sorted([item['id'] for item in items])

    col1, col2, col3 = st.columns(3)
    col1.metric("Łączna Wartość", f"{value:.2f}")
    col2.metric("Łączna Waga", f"{weight}")
    col3.metric("Czas Wykonania", f"{exec_time:.6f} s")
    with st.expander(f"Wybrane przedmioty ({len(item_ids)})"):
        if items:
            df_items = pd.DataFrame(items)[['id', 'value', 'weight']]
            st.dataframe(df_items.sort_values(by='id'), use_container_width=True)
        else:
            st.write("Brak wybranych przedmiotów.")

def display_mkp_results(algo_name, result_tuple, exec_time, capacities_list):
    """Wyświetla wyniki algorytmu MKP w Streamlit."""
    st.subheader(f"Wyniki: {algo_name}")
    if result_tuple is None:
        status = "Błąd" if exec_time == -1 else "Pominięto" if exec_time == -2 else "Brak wyniku"
        st.warning(f"Status: {status}")
        if exec_time >= 0 and status == "Błąd": st.write(f"(Czas do błędu: {exec_time:.6f} s)")
        return

    total_value, assignment_dict = result_tuple
    num_knapsacks = len(capacities_list)

    col1, col2 = st.columns(2)
    col1.metric("Optymalna Łączna Wartość", f"{total_value:.2f}")
    col2.metric("Czas Wykonania", f"{exec_time:.6f} s")

    st.write(f"**Przypisanie przedmiotów do {num_knapsacks} plecaków:**")
    total_items_assigned = 0
    for k_idx in range(num_knapsacks):
        k_items = assignment_dict.get(k_idx, [])
        weight_sum = sum(item['weight'] for item in k_items)
        capacity = capacities_list[k_idx]
        total_items_assigned += len(k_items)
        with st.expander(f"Plecak {k_idx} (Poj: {capacity}, Waga: {weight_sum}, Przedmioty: {len(k_items)})"):
             if k_items:
                  df_items = pd.DataFrame(k_items)[['id', 'value', 'weight']]
                  st.dataframe(df_items.sort_values(by='id'), use_container_width=True)
             else:
                  st.write("Brak przypisanych przedmiotów.")
    st.write(f"**Łączna liczba przypisanych przedmiotów:** {total_items_assigned}")

# --- Główna aplikacja Streamlit ---
st.set_page_config(layout="wide")
st.title("🎁 Analizator Problemu Plecakowego")

# --- Inicjalizacja stanu sesji ---
# Używamy teraz nowej nazwy klucza 'current_knapsack_items'
if 'current_knapsack_items' not in st.session_state:
    st.session_state.current_knapsack_items = get_example_items_large() # Domyślnie ładuj 'large'
    st.session_state.data_source_loaded = 'large' # Zapisz, co zostało załadowane
if 'results_01' not in st.session_state: st.session_state.results_01 = {}
if 'results_mkp' not in st.session_state: st.session_state.results_mkp = {}
if 'scalability_results_data' not in st.session_state: st.session_state.scalability_results_data = None
if 'config' not in st.session_state: st.session_state.config = {}


# --- Pasek Boczny (Sidebar) do Konfiguracji ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")

    # --- Wybór trybu ---
    mode = st.selectbox("Wybierz tryb pracy:", ['01', 'MKP'], # Usunięto 'SCALABILITY' dla uproszczenia - można dodać później
                        key='mode_select', index=0) # Domyślnie '01'
    st.session_state.config['mode'] = mode

    st.subheader(f"Parametry dla trybu: {mode}")

    # --- Opcje ładowania danych (Uproszczone) ---
    # Usunięto 'generate'
    data_source_options = {
        'small': "Zestaw testowy 'small'",
        'large': "Zestaw testowy 'large'",
        'csv_upload': "Prześlij plik CSV"
    }
    # Użyj kluczy jako wartości w selectbox
    data_source = st.selectbox(
        "Źródło danych:",
        options=list(data_source_options.keys()),
        format_func=lambda x: data_source_options[x], # Pokaż pełne opisy
        key='data_source_selector'
    )

    # --- Logika ładowania danych ---
    # Resetuj wyniki, jeśli zmieniono źródło danych LUB dane nie istnieją
    if data_source != st.session_state.get('data_source_loaded') or st.session_state.current_knapsack_items is None:
        st.session_state.current_knapsack_items = None # Resetuj
        st.session_state.results_01 = {} # Resetuj wyniki
        st.session_state.results_mkp = {}
        st.session_state.scalability_results_data = None

        if data_source == 'small':
            try:
                st.session_state.current_knapsack_items = get_example_items_small()
                st.session_state.data_source_loaded = 'small' # Zapisz, co załadowano
            except Exception as e: st.error(f"Błąd ładowania 'small': {e}")
        elif data_source == 'large':
             try:
                 st.session_state.current_knapsack_items = get_example_items_large()
                 st.session_state.data_source_loaded = 'large'
             except Exception as e: st.error(f"Błąd ładowania 'large': {e}")
        # Dla 'csv_upload' ładowanie poniżej

    # --- Obsługa przesyłania CSV ---
    if data_source == 'csv_upload':
        uploaded_file = st.file_uploader("Wybierz plik CSV", type=['csv'], key='csv_uploader')
        # Przetwarzaj tylko jeśli przesłano NOWY plik
        if uploaded_file is not None and uploaded_file != st.session_state.get('last_uploaded_file'):
             with st.spinner("Przetwarzanie pliku CSV..."):
                try:
                    df = pd.read_csv(uploaded_file)
                    if not {'id', 'value', 'weight'}.issubset(df.columns):
                        st.error("Plik CSV musi zawierać kolumny: id, value, weight")
                        st.session_state.current_knapsack_items = None
                    else:
                        # Konwersja i walidacja
                        df['value'] = pd.to_numeric(df['value'], errors='coerce')
                        df['weight'] = pd.to_numeric(df['weight'], errors='coerce').astype('Int64')
                        df = df.dropna(subset=['value', 'weight'])
                        df = df[ (df['value'] >= 0) & (df['weight'] >= 0) ]
                        st.session_state.current_knapsack_items = df.to_dict('records')
                        st.session_state.data_source_loaded = 'csv_upload' # Zapisz, że załadowano z CSV
                        st.session_state.last_uploaded_file = uploaded_file # Zapisz info o pliku
                        st.success(f"Wczytano {len(st.session_state.current_knapsack_items)} przedmiotów z pliku.")
                except Exception as e:
                    st.error(f"Błąd wczytywania pliku CSV: {e}")
                    st.session_state.current_knapsack_items = None
                    st.session_state.data_source_loaded = None
                    st.session_state.last_uploaded_file = None


    # --- Konfiguracja specyficzna dla trybu ---
    if mode == '01':
        # Użyj wartości ze stanu, jeśli istnieje, inaczej domyślna
        default_cap01 = st.session_state.config.get('capacity01', 10)
        capacity01 = st.number_input("Pojemność plecaka:", min_value=1, value=default_cap01, step=1, key='cap01')
        st.session_state.config['capacity01'] = capacity01
    elif mode == 'MKP':
        default_caps_mkp_str = " ".join(map(str, st.session_state.config.get('capacities_mkp', [10, 12])))
        cap_input = st.text_input("Pojemności plecaków (oddzielone spacją):", value=default_caps_mkp_str, key='cap_mkp')
        try:
             capacities_mkp = [int(c.strip()) for c in cap_input.split() if c.strip()]
             if not all(c >= 0 for c in capacities_mkp): raise ValueError("Pojemności muszą być nieujemne.")
             st.session_state.config['capacities_mkp'] = capacities_mkp
             if len(capacities_mkp) != 2: st.warning("DP MKP działa tylko dla 2 plecaków.")
        except ValueError:
             st.error("Wprowadź liczby całkowite oddzielone spacją.")
             # Nie zmieniaj configu, jeśli wpis jest błędny
             # st.session_state.config['capacities_mkp'] = [] # Reset? Może lepiej nie

    # Usunięto konfigurację SCALABILITY

# --- Koniec bloku with st.sidebar ---


# --- Główny Obszar Aplikacji ---
st.header("📊 Wyniki Analizy")

# Wyświetl wczytane/wygenerowane przedmioty
current_items_display = st.session_state.get('current_knapsack_items')
items_available = isinstance(current_items_display, list) and bool(current_items_display)

if items_available:
    with st.expander("Pokaż/Ukryj listę przedmiotów", expanded=False):
         try:
            st.dataframe(pd.DataFrame(current_items_display), use_container_width=True)
         except Exception as e:
             st.warning(f"Nie można wyświetlić DataFrame przedmiotów: {e}")
else:
    st.warning("Brak wczytanych danych. Wybierz źródło danych w panelu bocznym.")

# Przycisk do uruchomienia analizy
if st.button("Uruchom Analizę", type="primary", disabled=(not items_available)):

    # Pobierz dane i config ze stanu sesji
    items = st.session_state.get('current_knapsack_items')
    config = st.session_state.get('config', {})
    mode = config.get('mode')

    # Podwójne sprawdzenie (chociaż disabled powinien wystarczyć)
    if not items or not config or not mode:
         st.error("Błąd: Brak danych lub konfiguracji do uruchomienia analizy.")
    else:
        # Resetuj poprzednie wyniki
        st.session_state.results_01 = {}
        st.session_state.results_mkp = {}
        # st.session_state.scalability_results_data = None # Już niepotrzebne

        st.info(f"Uruchamianie analizy w trybie: {mode}...")
        with st.spinner("Trwa wykonywanie obliczeń..."):
            # --- Logika dla trybu 01 ---
            if mode == '01':
                capacity = config.get('capacity01')
                if capacity is None:
                     st.error("Błąd: Brak pojemności ('capacity01') w konfiguracji.")
                else:
                     results_01_temp = {}
                     # Wywołaj algorytmy 0/1 (bloki try...except jak wcześniej)
                     try: res, time = measure_time(greedy_knapsack_by_value, items, capacity); results_01_temp['greedy_value'] = {'result': res, 'time': time}
                     except Exception as e: results_01_temp['greedy_value'] = {'result': None, 'time': -1}; st.error(f"Błąd Greedy (Val): {e}")
                     try: res, time = measure_time(greedy_knapsack_by_weight, items, capacity); results_01_temp['greedy_weight'] = {'result': res, 'time': time}
                     except Exception as e: results_01_temp['greedy_weight'] = {'result': None, 'time': -1}; st.error(f"Błąd Greedy (Weight): {e}")
                     try: res, time = measure_time(greedy_knapsack_by_density, items, capacity); results_01_temp['greedy_density'] = {'result': res, 'time': time}
                     except Exception as e: results_01_temp['greedy_density'] = {'result': None, 'time': -1}; st.error(f"Błąd Greedy (Density): {e}")
                     if len(items) <= 20:
                          try: res, time = measure_time(brute_force_knapsack, items, capacity); results_01_temp['brute_force'] = {'result': res, 'time': time}
                          except Exception as e: results_01_temp['brute_force'] = {'result': None, 'time': -1}; st.error(f"Błąd BF: {e}")
                     else: results_01_temp['brute_force'] = {'result': None, 'time': -2}
                     try: res, time = measure_time(backtracking_knapsack, items, capacity); results_01_temp['backtracking'] = {'result': res, 'time': time}
                     except RecursionError: results_01_temp['backtracking'] = {'result': None, 'time': -1}; st.error("Błąd rekursji BT 0/1")
                     except Exception as e: results_01_temp['backtracking'] = {'result': None, 'time': -1}; st.error(f"Błąd BT 0/1: {e}")
                     try:
                          if not isinstance(capacity, int): raise TypeError("Pojemność musi być int dla DP.")
                          res, time = measure_time(dynamic_programming_knapsack, items, capacity); results_01_temp['dynamic'] = {'result': res, 'time': time}
                     except (ValueError, TypeError) as e: results_01_temp['dynamic'] = {'result': None, 'time': -1}; st.error(f"Błąd DP 0/1: {e}")
                     except Exception as e: results_01_temp['dynamic'] = {'result': None, 'time': -1}; st.error(f"Błąd DP 0/1: {e}")
                     st.session_state.results_01 = results_01_temp

            # --- Logika dla trybu MKP ---
            elif mode == 'MKP':
                capacities = config.get('capacities_mkp')
                if capacities is None or not isinstance(capacities, list) or not capacities:
                     st.error("Błąd: Brak lub niepoprawny format pojemności ('capacities_mkp') dla trybu MKP.")
                else:
                     results_mkp_temp = {}
                     # Wywołaj algorytmy MKP (bloki try...except jak wcześniej)
                     try: res, time = measure_time(mkp_backtracking_knapsack, items, capacities); results_mkp_temp['mkp_backtracking'] = {'result': res, 'time': time}
                     except RecursionError: results_mkp_temp['mkp_backtracking'] = {'result': None, 'time': -1}; st.error("Błąd rekursji BT MKP")
                     except Exception as e: results_mkp_temp['mkp_backtracking'] = {'result': None, 'time': -1}; st.error(f"Błąd BT MKP: {e}")
                     if len(capacities) == 2:
                          try:
                               cap1, cap2 = capacities
                               if not isinstance(cap1, int) or not isinstance(cap2, int): raise TypeError("Pojemności dla DP MKP m=2 muszą być int.")
                               res, time = measure_time(mkp_dynamic_programming_m2, items, cap1, cap2); results_mkp_temp['mkp_dp_m2'] = {'result': res, 'time': time}
                          except ImportError: results_mkp_temp['mkp_dp_m2'] = {'result': None, 'time': -1}; st.error("Brak NumPy dla DP MKP m=2")
                          except (ValueError, TypeError) as e: results_mkp_temp['mkp_dp_m2'] = {'result': None, 'time': -1}; st.error(f"Błąd DP MKP m=2: {e}")
                          except Exception as e: results_mkp_temp['mkp_dp_m2'] = {'result': None, 'time': -1}; st.error(f"Błąd DP MKP m=2: {e}")
                     else:
                          results_mkp_temp['mkp_dp_m2'] = {'result': None, 'time': -2}
                     st.session_state.results_mkp = results_mkp_temp

            # Usunięto blok elif mode == 'SCALABILITY'

        st.success("Analiza zakończona!") # Poza blokiem if/elif mode


# --- Wyświetlanie Wyników ---
# Wyświetl wyniki 0/1, jeśli istnieją
if st.session_state.results_01:
    st.header("Wyniki dla Problemu 0/1")
    valid_results_01 = {k: v for k, v in st.session_state.results_01.items() if v and v.get('time', -1) >= 0}
    for algo_name, data in st.session_state.results_01.items():
        display_01_results(algo_name, data.get('result'), data.get('time'))
    if valid_results_01:
         try:
             fig_val, fig_time = plot_comparison(valid_results_01, st.session_state.config.get('capacity01', '?'), st.session_state.get('data_source_loaded', '?'))
             if fig_val and fig_time:
                 st.subheader("Wykresy Porównawcze (0/1)")
                 st.pyplot(fig_val)
                 st.pyplot(fig_time)
                 plt.close(fig_val)
                 plt.close(fig_time)
             # else: st.warning("Nie udało się wygenerować wykresów porównawczych.") # Opcjonalnie
         except Exception as e: st.error(f"Błąd generowania wykresów porównawczych: {e}")

# Wyświetl wyniki MKP, jeśli istnieją
if st.session_state.results_mkp:
    st.header("Wyniki dla Problemu Wielu Plecaków (MKP)")
    capacities = st.session_state.config.get('capacities_mkp', [])
    for algo_name, data in st.session_state.results_mkp.items():
        display_mkp_results(algo_name, data.get('result'), data.get('time'), capacities)

# Usunięto blok wyświetlania wyników SCALABILITY

# Stopka
st.markdown("---")
st.caption("Aplikacja Streamlit do analizy problemu plecakowego.")