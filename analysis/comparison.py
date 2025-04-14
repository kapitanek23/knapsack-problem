# analysis/comparison.py

import matplotlib.pyplot as plt
import os
import numpy as np # Potrzebny do ustawiania pozycji słupków

# Upewnij się, że folder na wyniki istnieje
results_dir = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(results_dir, exist_ok=True) # exist_ok=True zapobiega błędowi, jeśli folder już istnieje

def plot_comparison(results_data, capacity, data_source_name, filename_prefix="comparison"):
    """
    Generuje i zapisuje wykresy porównujące wyniki (wartość) i czasy wykonania
    różnych algorytmów plecakowych.

    Args:
        results_data (dict): Słownik z wynikami z main.py.
                             Klucze to nazwy algorytmów (np. 'greedy_value'),
                             Wartości to słowniki {'result': (value, weight, items), 'time': exec_time}.
                             Wartość 'result' może być None, a 'time' może być < 0 w przypadku błędu/pominięcia.
        capacity (int/float): Pojemność plecaka użyta w eksperymencie.
        data_source_name (str): Nazwa użytego źródła danych (np. 'large', 'csv_small').
        filename_prefix (str): Prefiks dla nazw plików z wykresami.
    """
    print("\n--- Generowanie wykresów porównawczych ---")

    algorithms = list(results_data.keys())
    values = []
    times = []
    labels = [] # Krótsze etykiety na wykresy

    # Mapowanie kluczy na czytelne etykiety i zbieranie danych
    label_map = {
        'greedy_value': 'Zachłanny\n(Wartość)',
        'greedy_weight': 'Zachłanny\n(Waga)',
        'greedy_density': 'Zachłanny\n(Gęstość)',
        'brute_force': 'Brute Force\n(Optymalny)',
        'dynamic': 'Dynamiczny\n(Optymalny)'
    }

    # Filtrowanie algorytmów, które faktycznie zwróciły wynik
    valid_algorithms = []
    for algo in algorithms:
        data = results_data.get(algo)
        label = label_map.get(algo, algo) # Użyj klucza, jeśli nie ma w mapie

        if data and data.get('result') is not None and data.get('time', -1) >= 0:
            value, _, _ = data['result']
            time = data['time']
            values.append(value)
            times.append(time)
            labels.append(label)
            valid_algorithms.append(algo)
        elif data and data.get('time', -1) == -2: # Brute force pominięty
            print(f"  Informacja: Algorytm '{label}' został pominięty (nie będzie na wykresach).")
        elif data and data.get('time', -1) == -1: # Błąd wykonania
             print(f"  Ostrzeżenie: Algorytm '{label}' zakończył się błędem (nie będzie na wykresach).")
        # else: pomijamy algorytmy, których brakuje w wynikach

    if not valid_algorithms:
        print("  Brak poprawnych wyników do wygenerowania wykresów.")
        return

    # --- Wykres 1: Porównanie Wartości ---
    plt.figure(figsize=(10, 6)) # Rozmiar wykresu
    x_pos = np.arange(len(labels)) # Pozycje słupków

    bars_values = plt.bar(x_pos, values, color=['skyblue', 'lightgreen', 'salmon', 'gold', 'lightcoral'])
    plt.ylabel('Łączna wartość')
    plt.title(f'Porównanie wartości uzyskanej przez algorytmy\n(Pojemność: {capacity}, Zestaw danych: {data_source_name})')
    plt.xticks(x_pos, labels, rotation=15, ha="right") # Etykiety osi X, lekko obrócone
    plt.grid(axis='y', linestyle='--') # Siatka pozioma

    # Dodanie wartości nad słupkami
    for bar in bars_values:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', ha='center') # Wyświetl wartość

    plt.tight_layout() # Dopasowanie elementów wykresu
    values_plot_path = os.path.join(results_dir, f'{filename_prefix}_values.png')
    plt.savefig(values_plot_path)
    print(f"  Zapisano wykres wartości: {values_plot_path}")
    # plt.show() # Opcjonalnie: pokaż wykres od razu

    # --- Wykres 2: Porównanie Czasów Wykonania ---
    plt.figure(figsize=(10, 6))
    x_pos_time = np.arange(len(labels)) # Pozycje słupków

    # Użycie skali logarytmicznej, jeśli czasy bardzo się różnią (np. Brute Force vs Reszta)
    use_log_scale = max(times) / min(t for t in times if t > 0) > 100 if any(t > 0 for t in times) else False

    bars_times = plt.bar(x_pos_time, times, color=['skyblue', 'lightgreen', 'salmon', 'gold', 'lightcoral'])
    plt.ylabel('Czas wykonania (s)' + (' [skala log]' if use_log_scale else ''))
    plt.title(f'Porównanie czasu wykonania algorytmów\n(Pojemność: {capacity}, Zestaw danych: {data_source_name})')
    plt.xticks(x_pos_time, labels, rotation=15, ha="right")
    plt.grid(axis='y', linestyle='--')

    if use_log_scale:
        plt.yscale('log') # Ustawienie skali logarytmicznej dla osi Y

    # Dodanie wartości nad słupkami
    for bar in bars_times:
        yval = bar.get_height()
        # Formatowanie czasu - bardziej precyzyjne dla małych wartości
        time_str = f'{yval:.6f}' if yval < 0.1 else f'{yval:.4f}'
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, time_str, va='bottom', ha='center', fontsize=9)

    plt.tight_layout()
    times_plot_path = os.path.join(results_dir, f'{filename_prefix}_times.png')
    plt.savefig(times_plot_path)
    print(f"  Zapisano wykres czasów: {times_plot_path}")
    plt.close('all') # Zamknij wszystkie figury, aby nie wisiały w pamięci

# Przykład użycia (głównie do testowania tego pliku)
if __name__ == "__main__":
    print("--- Testowanie comparison.py ---")
    # Przykładowe dane wejściowe - takie jak mogłyby przyjść z main.py
    mock_results = {
        'greedy_value': {'result': (130.0, 9, [{'id': 'C', 'value': 70.0, 'weight': 4}, {'id': 'A', 'value': 60.0, 'weight': 5}]), 'time': 0.000123},
        'greedy_weight': {'result': (150.0, 9, [{'id': 'D', 'value': 30.0, 'weight': 2}, {'id': 'B', 'value': 50.0, 'weight': 3}, {'id': 'C', 'value': 70.0, 'weight': 4}]), 'time': 0.000180},
        'greedy_density': {'result': (150.0, 9, [{'id': 'C', 'value': 70.0, 'weight': 4}, {'id': 'B', 'value': 50.0, 'weight': 3}, {'id': 'D', 'value': 30.0, 'weight': 2}]), 'time': 0.000250},
        'brute_force': {'result': (150.0, 9, [{'id': 'B', 'value': 50.0, 'weight': 3}, {'id': 'C', 'value': 70.0, 'weight': 4}, {'id': 'D', 'value': 30.0, 'weight': 2}]), 'time': 0.001500},
        # 'brute_force': {'result': None, 'time': -2}, # Przetestuj pominięcie BF
        'dynamic': {'result': (150.0, 9, [{'id': 'B', 'value': 50.0, 'weight': 3}, {'id': 'C', 'value': 70.0, 'weight': 4}, {'id': 'D', 'value': 30.0, 'weight': 2}]), 'time': 0.000800},
        # 'dynamic': {'result': None, 'time': -1}, # Przetestuj błąd DP
    }
    mock_capacity = 10
    mock_data_source = 'small_test'

    plot_comparison(mock_results, mock_capacity, mock_data_source, filename_prefix="test_comparison")

    print("\nTest z brakującymi/błędnymi danymi:")
    mock_results_missing = {
         'greedy_value': {'result': (130.0, 9, []), 'time': 0.0001},
         'brute_force': {'result': None, 'time': -2}, # Pominięty
         'dynamic': {'result': None, 'time': -1}, # Błąd
    }
    plot_comparison(mock_results_missing, mock_capacity, "missing_test", filename_prefix="test_missing")