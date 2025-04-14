# analysis/comparison.py

import matplotlib.pyplot as plt
import os
import numpy as np
import json # Potrzebne tylko w bloku testowym, jeśli go używasz

# Katalog na wyniki nie jest już potrzebny do zapisu z tych funkcji
# results_dir = os.path.join(os.path.dirname(__file__), 'results')
# os.makedirs(results_dir, exist_ok=True)

def plot_comparison(results_data, capacity, data_source_name): # Usunięto filename_prefix
    """
    Generuje wykresy porównujące wyniki (wartość) i czasy wykonania
    różnych algorytmów plecakowych i ZWRACA figury Matplotlib.

    Args:
        results_data (dict): Słownik z wynikami.
        capacity (int/float): Pojemność plecaka.
        data_source_name (str): Nazwa użytego źródła danych.

    Returns:
        tuple: Krotka zawierająca dwie figury Matplotlib: (fig_values, fig_times).
               Zwraca (None, None) jeśli brak danych.
    """
    # Usunięto printy, logika wyświetlania jest teraz w Streamlit
    # print("\n--- Generowanie wykresów porównawczych ---")

    algorithms = list(results_data.keys())
    values = []
    times = []
    labels = []

    label_map = {
        'greedy_value': 'Zachłanny\n(Wartość)',
        'greedy_weight': 'Zachłanny\n(Waga)',
        'greedy_density': 'Zachłanny\n(Gęstość)',
        'brute_force': 'Brute Force\n(Optymalny)',
        'backtracking': 'Backtracking\n(Optymalny)',
        'dynamic': 'Dynamiczny\n(Optymalny)',
        # Dodaj mapowania dla MKP, jeśli chcesz je tu obsługiwać
        # 'mkp_backtracking': 'BT MKP',
        # 'mkp_dp_m2': 'DP MKP (m=2)'
    }

    valid_algorithms = []
    for algo in algorithms:
        data = results_data.get(algo)
        label = label_map.get(algo, algo)

        # Uwzględniamy tylko wyniki z poprawnym czasem (>=0)
        if data and data.get('result') is not None and data.get('time', -1) >= 0:
            value, _, _ = data['result']
            time = data['time']
            values.append(value)
            times.append(time)
            labels.append(label)
            valid_algorithms.append(algo)
        # else: # Komunikaty o błędach/pominięciach są teraz w Streamlit
        #     pass

    if not valid_algorithms:
        # print("  Brak poprawnych wyników do wygenerowania wykresów.")
        return None, None # Zwróć None, jeśli nie ma co rysować

    # --- Wykres 1: Porównanie Wartości ---
    fig_values = plt.figure(figsize=(10, 6)) # Przypisz obiekt Figure
    ax_values = fig_values.add_subplot(111) # Dodaj osie
    x_pos = np.arange(len(labels))

    colors = ['skyblue', 'lightgreen', 'salmon', 'gold', 'mediumpurple', 'lightcoral']
    bars_values = ax_values.bar(x_pos, values, color=colors[:len(labels)])
    ax_values.set_ylabel('Łączna wartość')
    ax_values.set_title(f'Porównanie wartości uzyskanej przez algorytmy\n(Pojemność: {capacity}, Zestaw danych: {data_source_name})')
    ax_values.set_xticks(x_pos)
    ax_values.set_xticklabels(labels, rotation=15, ha="right")
    ax_values.grid(axis='y', linestyle='--')

    for bar in bars_values:
        yval = bar.get_height()
        ax_values.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', ha='center')

    fig_values.tight_layout()
    # USUNIĘTE: plt.savefig(...)
    # USUNIĘTE: plt.show()
    # USUNIĘTE: plt.close(fig_values) # Zamykamy w Streamlit po użyciu

    # --- Wykres 2: Porównanie Czasów Wykonania ---
    fig_times = plt.figure(figsize=(10, 6)) # Przypisz obiekt Figure
    ax_times = fig_times.add_subplot(111) # Dodaj osie
    x_pos_time = np.arange(len(labels))

    use_log_scale = max(times) / min(t for t in times if t > 0) > 100 if any(t > 0 for t in times) else False

    bars_times = ax_times.bar(x_pos_time, times, color=colors[:len(labels)])
    ax_times.set_ylabel('Czas wykonania (s)' + (' [skala log]' if use_log_scale else ''))
    ax_times.set_title(f'Porównanie czasu wykonania algorytmów\n(Pojemność: {capacity}, Zestaw danych: {data_source_name})')
    ax_times.set_xticks(x_pos_time)
    ax_times.set_xticklabels(labels, rotation=15, ha="right")
    ax_times.grid(axis='y', linestyle='--')

    if use_log_scale:
        ax_times.set_yscale('log')

    for bar in bars_times:
        yval = bar.get_height()
        time_str = f'{yval:.6f}' if yval < 0.1 else f'{yval:.4f}'
        ax_times.text(bar.get_x() + bar.get_width()/2.0, yval, time_str, va='bottom', ha='center', fontsize=9)

    fig_times.tight_layout()
    # USUNIĘTE: plt.savefig(...)
    # USUNIĘTE: plt.close('all') # Zamykamy w Streamlit

    # Zwróć obie figury
    return fig_values, fig_times


# --- Funkcja do tworzenia wykresów skalowalności ---

def plot_scalability(data): # Zmieniono argument na słownik 'data'
    """
    Wczytuje wyniki analizy skalowalności ze słownika i ZWRACA figurę Matplotlib.

    Args:
        data (dict): Słownik z wynikami analizy (wcześniej wczytywany z JSON).
                     Oczekiwany format: {'param': 'n'/'W', 'values': [], 'times': {algo:[]}, ...}

    Returns:
        matplotlib.figure.Figure: Obiekt figury wykresu lub None w przypadku błędu/braku danych.
    """
    # Usunięto printy
    # print("\n--- Generowanie wykresów skalowalności ---")

    # Usunięto wczytywanie z pliku JSON
    # try: ... except ...

    param_name = data.get('param')
    param_values = data.get('values', [])
    times_data = data.get('times', {})
    fixed_param = data.get('fixed_param', '')
    fixed_value = data.get('fixed_value', '')

    if not param_name or not param_values or not times_data:
        # print("  Błąd: Niekompletne dane wejściowe.")
        return None # Zwróć None, jeśli dane są niekompletne

    algorithms = list(times_data.keys())

    # Utwórz figurę i osie
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    # Rysowanie linii dla każdego algorytmu
    for algo in algorithms:
        times = times_data.get(algo, [])
        valid_indices = [i for i, t in enumerate(times) if t >= 0]
        valid_params = [param_values[i] for i in valid_indices]
        valid_times = [times[i] for i in valid_indices]

        if valid_params:
            ax.plot(valid_params, valid_times, marker='o', linestyle='-', label=algo)

    ax.set_xlabel(f"Parametr: {param_name}")
    ax.set_ylabel('Czas wykonania (s)')
    title = f"Skalowalność algorytmów w zależności od '{param_name}'"
    if fixed_param:
        title += f"\n(stałe {fixed_param} = {fixed_value})"
    ax.set_title(title)
    ax.legend()
    ax.grid(True, linestyle='--')

    # Można dodać opcję skali logarytmicznej, jeśli potrzebne
    # min_time = min((t for t_list in times_data.values() for t in t_list if t > 0), default=1)
    # max_time = max((t for t_list in times_data.values() for t in t_list if t >= 0), default=1)
    # if max_time / min_time > 100 :
    #      ax.set_yscale('log')

    fig.tight_layout()

    # USUNIĘTE: plt.savefig(...)
    # USUNIĘTE: plt.close(fig) # Zamykamy w Streamlit

    # Zwróć figurę
    return fig


# --- Aktualizacja Bloku testowego (jeśli chcesz go zachować) ---
if __name__ == "__main__":
    # UWAGA: Ten blok testowy nie będzie działał poprawnie bez dodatkowych modyfikacji,
    # ponieważ funkcje nie zapisują już plików. Służył głównie do debugowania.
    # Najlepiej testować teraz przez uruchomienie `app_streamlit.py`.

    print("--- Testowanie comparison.py (tylko logika, bez zapisu/wyświetlania) ---")

    # Test plot_comparison
    mock_results = {
        'greedy_value': {'result': (130.0, 9, []), 'time': 0.000123},
        'dynamic': {'result': (150.0, 9, []), 'time': 0.000800},
    }
    mock_capacity = 10
    mock_data_source = 'small_test'
    fig_val, fig_time = plot_comparison(mock_results, mock_capacity, mock_data_source)
    if fig_val and fig_time:
         print("Test plot_comparison: Figury wygenerowane (niezapisane).")
         plt.close(fig_val) # Zamknij figury testowe
         plt.close(fig_time)
    else:
         print("Test plot_comparison: Nie wygenerowano figur (brak danych?).")


    # Test plot_scalability
    print("\n--- Testowanie plot_scalability (tylko logika) ---")
    mock_scalability_data = {
        'param': 'n',
        'values': [5, 10, 15],
        'times': {
            'dynamic': [0.001, 0.002, 0.003],
            'backtracking': [0.01, 0.1, 1.5]
        },
        'fixed_param': 'W',
        'fixed_value': 500
    }
    fig_scale = plot_scalability(mock_scalability_data)
    if fig_scale:
         print("Test plot_scalability: Figura wygenerowana (niezapisana).")
         plt.close(fig_scale)
    else:
         print("Test plot_scalability: Nie wygenerowano figury (brak danych?).")