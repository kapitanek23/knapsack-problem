# app_streamlit.py
import streamlit as st
import pandas as pd
import os
import time # Do measure_time i st.spinner
import numpy as np # Potrzebne dla DP m=2
import matplotlib.pyplot as plt
import json

# --- Importuj logikę z twoich modułów ---
# Zakładamy, że ścieżki są poprawne, jeśli uruchamiasz z głównego folderu projektu
try:
    from utils import (
        load_items_from_csv,
        get_example_items_small,
        get_example_items_large,
        generate_random_items, # Potrzebne dla SCALABILITY
        measure_time
    )
    from algorithms.greedy import *
    from algorithms.brute_force import brute_force_knapsack
    from algorithms.dynamic import dynamic_programming_knapsack
    from algorithms.backtracking import backtracking_knapsack
    from algorithms.mkp_backtracking import mkp_backtracking_knapsack
    from algorithms.mkp_dynamic_m2 import mkp_dynamic_programming_m2
    from analysis.comparison import plot_comparison, plot_scalability
except ImportError as e:
    st.error(f"Błąd importu modułu: {e}")
    st.error("Upewnij się, że uruchamiasz aplikację z głównego folderu projektu ('knapsack_problem') i że wszystkie pliki .py istnieją w odpowiednich podfolderach ('algorithms', 'analysis', 'utils').")
    st.stop() # Zatrzymaj aplikację, jeśli importy się nie powiodły

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
        # Bezpieczne pobranie pojemności
        capacity = capacities_list[k_idx] if k_idx < len(capacities_list) else '?'
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
# Używajmy jednej nazwy klucza dla danych
if 'current_knapsack_items' not in st.session_state:
    st.session_state.current_knapsack_items = get_example_items_large()
    st.session_state.data_source_loaded = 'large'
    st.session_state.last_uploaded_file_name = None # Do śledzenia przesłanego pliku
if 'results_01' not in st.session_state: st.session_state.results_01 = {}
if 'results_mkp' not in st.session_state: st.session_state.results_mkp = {}
if 'scalability_results_data' not in st.session_state: st.session_state.scalability_results_data = None
if 'config' not in st.session_state: st.session_state.config = {} # Ogólna konfiguracja
# Domyślne parametry dla generatora i skalowalności
if 'gen_params' not in st.session_state:
     st.session_state.gen_params = {'num': 20, 'vmin': 1.0, 'vmax': 100.0, 'wmin': 1, 'wmax': 50}
if 'scale_params' not in st.session_state:
    st.session_state.scale_params = {
        'n_values': [5, 10, 15, 20, 25],
        'W_values': [50, 100, 200, 400, 800],
        'fixed_W': 500,
        'fixed_n': 20,
        'algos': ['dynamic', 'backtracking']
    }

# --- Pasek Boczny (Sidebar) do Konfiguracji ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")

    # --- Wybór trybu ---
    # Odczytaj poprzedni wybór lub ustaw domyślny
    mode_options = ['01', 'MKP', 'SCALABILITY']
    current_mode_index = mode_options.index(st.session_state.config.get('mode', '01'))
    mode = st.selectbox("Wybierz tryb pracy:", mode_options, index=current_mode_index, key='mode_selector')

    # Zapisz nowy wybór i zresetuj wyniki jeśli tryb się zmienił
    if mode != st.session_state.config.get('mode'):
        st.session_state.config['mode'] = mode
        st.session_state.results_01 = {}
        st.session_state.results_mkp = {}
        st.session_state.scalability_results_data = None
        # st.experimental_rerun() # Wymuś przeładowanie po zmianie trybu

    st.subheader(f"Parametry dla trybu: {mode}")

    # --- Opcje ładowania danych ---
    data_source_options = {
        'small': "Zestaw testowy 'small'",
        'large': "Zestaw testowy 'large'",
        'csv_upload': "Prześlij plik CSV",
        'generate': "Generuj losowo" # Przywrócono opcję
    }
    # Odczytaj poprzedni wybór źródła
    current_ds_key = st.session_state.get('data_source_loaded', 'large')
    # Sprawdź, czy klucz istnieje w opcjach, jeśli nie, użyj domyślnego
    if current_ds_key not in data_source_options:
        current_ds_key = 'large'
    current_ds_index = list(data_source_options.keys()).index(current_ds_key)

    data_source = st.selectbox(
        "Źródło danych:",
        options=list(data_source_options.keys()),
        format_func=lambda x: data_source_options[x],
        index=current_ds_index,
        key='data_source_selector'
    )

    # --- Logika ładowania/generowania danych ---
    # Wykonuje się, jeśli zmieniono źródło LUB dane są None
    if data_source != st.session_state.get('data_source_loaded') or st.session_state.current_knapsack_items is None:
        st.session_state.my_knapsack_items = None # Resetuj
        st.info(f"Wybrano źródło: {data_source}. Przygotowywanie danych...")

        if data_source == 'small':
            try:
                st.session_state.current_knapsack_items = get_example_items_small()
                st.session_state.data_source_loaded = 'small'
            except Exception as e: st.error(f"Błąd ładowania 'small': {e}")
        elif data_source == 'large':
            try:
                 st.session_state.current_knapsack_items = get_example_items_large()
                 st.session_state.data_source_loaded = 'large'
            except Exception as e: st.error(f"Błąd ładowania 'large': {e}")
        elif data_source == 'csv_upload':
             # Wyświetl uploader, przetwarzanie nastąpi poniżej
             st.session_state.data_source_loaded = 'csv_upload' # Zaznacz oczekiwanie na upload
             pass # Nie ładuj nic od razu
        elif data_source == 'generate':
             # Wyświetl opcje generatora, generowanie po kliknięciu poniżej
             st.session_state.data_source_loaded = 'generate' # Zaznacz oczekiwanie na generację
             pass # Nie generuj nic od razu

        # Po zmianie źródła, zresetuj wyniki
        st.session_state.results_01 = {}
        st.session_state.results_mkp = {}
        st.session_state.scalability_results_data = None
        # st.experimental_rerun() # Wymuś przeładowanie, aby odświeżyć interfejs

    # --- Elementy interfejsu specyficzne dla źródła danych ---
    if data_source == 'csv_upload':
        uploaded_file = st.file_uploader("Wybierz plik CSV", type=['csv'], key='csv_uploader')
        if uploaded_file is not None:
            # Przetwarzaj tylko jeśli plik się zmienił
            if uploaded_file.name != st.session_state.get('last_uploaded_file_name'):
                 with st.spinner("Przetwarzanie pliku CSV..."):
                    try:
                        df = pd.read_csv(uploaded_file)
                        if not {'id', 'value', 'weight'}.issubset(df.columns):
                            st.error("Plik CSV musi zawierać kolumny: id, value, weight")
                            st.session_state.current_knapsack_items = None
                        else:
                            df['value'] = pd.to_numeric(df['value'], errors='coerce')
                            df['weight'] = pd.to_numeric(df['weight'], errors='coerce').astype('Int64')
                            df = df.dropna(subset=['value', 'weight'])
                            df = df[ (df['value'] >= 0) & (df['weight'] >= 0) ]
                            st.session_state.current_knapsack_items = df.to_dict('records')
                            st.session_state.last_uploaded_file_name = uploaded_file.name
                            st.success(f"Wczytano {len(st.session_state.current_knapsack_items)} przedmiotów z pliku.")
                    except Exception as e:
                        st.error(f"Błąd wczytywania pliku CSV: {e}")
                        st.session_state.current_knapsack_items = None
                        st.session_state.last_uploaded_file_name = None

    elif data_source == 'generate':
        st.write("Ustaw parametry:")
        p = st.session_state.gen_params # Skrót
        p['num'] = st.number_input("Liczba przedmiotów:", min_value=1, value=p['num'], step=1, key='gen_n')
        p['vmin'] = st.number_input("Min wartość:", value=p['vmin'], step=1.0, key='gen_val_min')
        p['vmax'] = st.number_input("Max wartość:", value=p['vmax'], step=1.0, key='gen_val_max')
        p['wmin'] = st.number_input("Min waga:", min_value=1, value=p['wmin'], step=1, key='gen_wei_min')
        p['wmax'] = st.number_input("Max waga:", min_value=1, value=p['wmax'], step=1, key='gen_wei_max')

        if st.button("Generuj Dane", key='gen_button'):
             try:
                 generated_data = generate_random_items(p['num'], (p['vmin'], p['vmax']), (p['wmin'], p['wmax']))
                 st.session_state.current_knapsack_items = generated_data
                 st.success(f"Wygenerowano {len(st.session_state.current_knapsack_items)} przedmiotów.")
                 # st.experimental_rerun() # Może być potrzebne do odświeżenia stanu przycisku "Uruchom"
             except Exception as e:
                  st.error(f"Błąd generowania: {e}")
                  st.session_state.current_knapsack_items = None

    # --- Konfiguracja specyficzna dla trybu ---
    if mode == '01':
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
    elif mode == 'SCALABILITY':
        sp = st.session_state.scale_params # Skrót
        scale_param = st.selectbox("Analiza wg:", ['n', 'W'], index=0 if sp.get('param','n')=='n' else 1, key='scale_param')
        sp['param'] = scale_param # Zapisz wybór

        if scale_param == 'n':
             n_vals_input = st.text_input("Wartości 'n':", value=" ".join(map(str, sp['n_values'])), key='n_vals')
             fixed_w = st.number_input("Stałe 'W':", min_value=1, value=sp['fixed_W'], step=1, key='fixed_w')
             try: sp['n_values'] = [int(v.strip()) for v in n_vals_input.split() if v.strip()]
             except ValueError: st.error("Wprowadź poprawne liczby dla 'n'")
             sp['fixed_W'] = fixed_w
        else: # scale_param == 'W'
             w_vals_input = st.text_input("Wartości 'W':", value=" ".join(map(str, sp['W_values'])), key='w_vals')
             fixed_n = st.number_input("Stałe 'n':", min_value=1, value=sp['fixed_n'], step=1, key='fixed_n')
             try: sp['W_values'] = [int(v.strip()) for v in w_vals_input.split() if v.strip()]
             except ValueError: st.error("Wprowadź poprawne liczby dla 'W'")
             sp['fixed_n'] = fixed_n

        algo_options = ['dynamic', 'backtracking', 'brute_force']
        algos_to_scale = st.multiselect("Algorytmy:", algo_options, default=sp['algos'], key='scale_algos')
        sp['algos'] = algos_to_scale

# --- Koniec bloku with st.sidebar ---

# --- Główny Obszar Aplikacji ---
st.header("📊 Wyniki Analizy")

# Wyświetl wczytane/wygenerowane przedmioty
current_items_display = st.session_state.get('current_knapsack_items')
items_available = isinstance(current_items_display, list) and bool(current_items_display)

if items_available:
    with st.expander(f"Pokaż/Ukryj listę przedmiotów ({len(current_items_display)})", expanded=False):
         try:
            st.dataframe(pd.DataFrame(current_items_display), use_container_width=True)
         except Exception as e:
             st.warning(f"Nie można wyświetlić DataFrame przedmiotów: {e}")
else:
    st.warning("Brak wczytanych lub wygenerowanych danych. Wybierz źródło i przygotuj dane w panelu bocznym.")

# --- Przycisk do uruchomienia analizy ---
if st.button("Uruchom Analizę", type="primary", disabled=(not items_available)):

    items = st.session_state.current_knapsack_items # Pobierz aktualne dane
    config = st.session_state.config
    mode = config.get('mode')

    if not items or not config or not mode: # Podwójne sprawdzenie
         st.error("Błąd: Brak danych lub konfiguracji do uruchomienia analizy.")
    else:
        # Resetuj wyniki przed analizą
        st.session_state.results_01 = {}
        st.session_state.results_mkp = {}
        st.session_state.scalability_results_data = None
        st.info(f"Uruchamianie analizy w trybie: {mode}...")

        with st.spinner("Trwa wykonywanie obliczeń..."):
            # --- Logika dla trybu 01 ---
            if mode == '01':
                capacity = config.get('capacity01')
                if capacity is None: st.error("Błąd: Brak pojemności dla trybu 01.")
                else:
                     results_01_temp = {}
                     # Wywołaj algorytmy 0/1... (try/except jak w poprzedniej wersji)
                     # ... (skopiuj bloki try/except dla greedy, bf, bt, dp z poprzedniej wersji) ...
                     try: res, time = measure_time(greedy_knapsack_by_value, items, capacity); results_01_temp['greedy_value'] = {'result': res, 'time': time}
                     except Exception as e: results_01_temp['greedy_value'] = {'result': None, 'time': -1}; st.error(f"Błąd Greedy (Val): {e}")
                     try: res, time = measure_time(greedy_knapsack_by_weight, items, capacity); results_01_temp['greedy_weight'] = {'result': res, 'time': time}
                     except Exception as e: results_01_temp['greedy_weight'] = {'result': None, 'time': -1}; st.error(f"Błąd Greedy (Weight): {e}")
                     try: res, time = measure_time(greedy_knapsack_by_density, items, capacity); results_01_temp['greedy_density'] = {'result': res, 'time': time}
                     except Exception as e: results_01_temp['greedy_density'] = {'result': None, 'time': -1}; st.error(f"Błąd Greedy (Density): {e}")
                     if len(items) <= 20: # Używaj 'items' pobranego na początku
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
                     st.session_state.results_01 = results_01_temp # Zapisz do stanu

            # --- Logika dla trybu MKP ---
            elif mode == 'MKP':
                capacities = config.get('capacities_mkp')
                if not capacities or not isinstance(capacities, list): st.error("Błąd: Brak lub niepoprawne pojemności dla trybu MKP.")
                else:
                     results_mkp_temp = {}
                     # Wywołaj algorytmy MKP... (try/except jak w poprzedniej wersji)
                     # ... (skopiuj bloki try/except dla mkp_backtracking i mkp_dp_m2 z poprzedniej wersji) ...
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
                     else: results_mkp_temp['mkp_dp_m2'] = {'result': None, 'time': -2}
                     st.session_state.results_mkp = results_mkp_temp # Zapisz do stanu

            # --- Logika dla trybu SCALABILITY ---
            elif mode == 'SCALABILITY':
                scale_cfg = st.session_state.scale_params # Pobierz config skalowalności
                param = scale_cfg.get('param')
                algos = scale_cfg.get('algos')
                if not param or not algos: st.error("Błąd: Brak konfiguracji skalowalności.")
                else:
                    results_data = {'param': param, 'values': [], 'times': {algo: [] for algo in algos}}
                    progress_bar = st.progress(0, text="Rozpoczynanie analizy...")
                    total_steps = 0

                    # Logika analizy wg 'n'
                    if param == 'n':
                        values_to_test = scale_cfg.get('n_values')
                        fixed_capacity = scale_cfg.get('fixed_W')
                        if not values_to_test or fixed_capacity is None: st.error("Brak n_values/fixed_W w config"); values_to_test=[]
                        else:
                            results_data['fixed_param'] = 'W'; results_data['fixed_value'] = fixed_capacity
                            total_steps = len(values_to_test)
                            st.write(f"Analiza wg 'n' dla n={values_to_test}, W={fixed_capacity}...")

                            for i, n in enumerate(values_to_test):
                                progress_text = f"Testowanie n={n} ({i+1}/{total_steps})"
                                progress_bar.progress((i + 1) / total_steps, text=progress_text)
                                st.write(f"  {progress_text}") # Opcjonalnie log w głównym oknie
                                try:
                                    current_items_gen = generate_random_items(n) # Użyj zapisanych zakresów w gen_params
                                except Exception as e_gen:
                                    st.warning(f"Błąd generowania danych dla n={n}: {e_gen}")
                                    results_data['values'].append(n)
                                    for algo_name in algos: results_data['times'][algo_name].append(-1)
                                    continue

                                results_data['values'].append(n)
                                for algo_name in algos:
                                     algo_func = None; time = -1
                                     if algo_name == 'dynamic': algo_func = dynamic_programming_knapsack
                                     elif algo_name == 'backtracking': algo_func = backtracking_knapsack
                                     elif algo_name == 'brute_force': algo_func = brute_force_knapsack
                                     if algo_func:
                                          if algo_name == 'brute_force' and n > 20: time = -2
                                          elif algo_name == 'dynamic' and not isinstance(fixed_capacity, int): time = -1; st.warning("Pojemność nie jest int dla DP")
                                          else:
                                               try: _, time = measure_time(algo_func, current_items_gen, fixed_capacity)
                                               except RecursionError: time = -1; st.warning(f"Błąd rekursji {algo_name} dla n={n}")
                                               except Exception as e: time = -1; st.warning(f"Błąd {algo_name} dla n={n}: {e}")
                                     results_data['times'][algo_name].append(time)

                    # Logika analizy wg 'W'
                    elif param == 'W':
                        values_to_test = scale_cfg.get('W_values')
                        fixed_n = scale_cfg.get('fixed_n')
                        if not values_to_test or fixed_n is None: st.error("Brak W_values/fixed_n w config"); values_to_test=[]
                        else:
                            results_data['fixed_param'] = 'n'; results_data['fixed_value'] = fixed_n
                            total_steps = len(values_to_test)
                            st.write(f"Analiza wg 'W' dla W={values_to_test}, n={fixed_n}...")
                            try:
                                current_items_gen = generate_random_items(fixed_n) # Generuj raz
                            except Exception as e_gen:
                                 st.error(f"Błąd generowania danych dla n={fixed_n}: {e_gen}")
                                 current_items_gen = None

                            if current_items_gen:
                                 for i, W in enumerate(values_to_test):
                                      progress_text = f"Testowanie W={W} ({i+1}/{total_steps})"
                                      progress_bar.progress((i + 1) / total_steps, text=progress_text)
                                      st.write(f"  {progress_text}")
                                      results_data['values'].append(W)
                                      for algo_name in algos:
                                           algo_func = None; time = -1
                                           if algo_name == 'dynamic': algo_func = dynamic_programming_knapsack
                                           elif algo_name == 'backtracking': algo_func = backtracking_knapsack
                                           elif algo_name == 'brute_force': algo_func = brute_force_knapsack
                                           if algo_func:
                                                if algo_name == 'brute_force' and fixed_n > 20: time = -2
                                                elif algo_name == 'dynamic' and not isinstance(W, int): time = -1; st.warning("Pojemność nie jest int dla DP")
                                                else:
                                                     try: _, time = measure_time(algo_func, current_items_gen, W)
                                                     except RecursionError: time = -1; st.warning(f"Błąd rekursji {algo_name} dla W={W}")
                                                     except Exception as e: time = -1; st.warning(f"Błąd {algo_name} dla W={W}: {e}")
                                           results_data['times'][algo_name].append(time)
                            else: # Jeśli błąd generatora, zapisz błędy
                                 for W in values_to_test:
                                      results_data['values'].append(W)
                                      for algo_name in algos: results_data['times'][algo_name].append(-1)
                            progress_bar.progress(1.0, text="Błąd generowania danych!")


                    # Zapisz wyniki analizy skalowalności do stanu sesji
                    if results_data.get('values'): # Zapisz tylko jeśli są jakieś wartości
                         st.session_state.scalability_results_data = results_data
                    else:
                         st.warning("Nie przeprowadzono żadnych testów skalowalności.")


        # Komunikat o zakończeniu na końcu bloku 'with spinner'
        st.success("Analiza zakończona!")


# --- Wyświetlanie Wyników (zawsze po bloku przycisku, na podstawie stanu sesji) ---

# Wyświetl wyniki 0/1, jeśli istnieją
if st.session_state.results_01:
    st.header("Wyniki dla Problemu 0/1")
    valid_results_01 = {k: v for k, v in st.session_state.results_01.items() if v and v.get('time', -1) >= 0}
    for algo_name, data in st.session_state.results_01.items():
        display_01_results(algo_name, data.get('result'), data.get('time'))
    if valid_results_01:
         try:
             # Upewnij się, że funkcje w comparison.py zwracają figury!
             # Bezpieczne pobieranie konfiguracji do tytułu wykresu
             plot_capacity = st.session_state.config.get('capacity01', 'N/A')
             plot_ds = st.session_state.get('data_source_loaded', 'N/A')
             fig_val, fig_time = plot_comparison(valid_results_01, plot_capacity, plot_ds)
             if fig_val and fig_time:
                 st.subheader("Wykresy Porównawcze (0/1)")
                 st.pyplot(fig_val)
                 st.pyplot(fig_time)
                 plt.close(fig_val)
                 plt.close(fig_time)
             else: st.warning("Nie udało się wygenerować wykresów porównawczych (brak poprawnych danych?).")
         except Exception as e: st.error(f"Błąd generowania wykresów porównawczych: {e}")

# Wyświetl wyniki MKP, jeśli istnieją
if st.session_state.results_mkp:
    st.header("Wyniki dla Problemu Wielu Plecaków (MKP)")
    capacities = st.session_state.config.get('capacities_mkp', [])
    for algo_name, data in st.session_state.results_mkp.items():
        display_mkp_results(algo_name, data.get('result'), data.get('time'), capacities)

# Wyświetl wyniki skalowalności, jeśli istnieją
if st.session_state.scalability_results_data:
    st.header("Wyniki Analizy Skalowalności")
    # st.json(st.session_state.scalability_results_data) # Opcjonalnie: pokaż surowe dane JSON
    try:
         # Upewnij się, że plot_scalability zwraca figurę!
         fig_scale = plot_scalability(st.session_state.scalability_results_data)
         if fig_scale:
             st.pyplot(fig_scale)
             plt.close(fig_scale)
         else: st.warning("Nie udało się wygenerować wykresu skalowalności (brak poprawnych danych?).")
    except Exception as e: st.error(f"Błąd generowania wykresu skalowalności: {e}")

# Stopka
st.markdown("---")
st.caption("Aplikacja do analizy problemu plecakowego. / Autorzy: Anna Oleszko, Bartosz Kawalec, Kacper Saj")