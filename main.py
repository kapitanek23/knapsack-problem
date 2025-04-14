# main.py
from analysis.comparison import plot_comparison

import os # Do operacji na ścieżkach
from utils import (
    load_items_from_csv,
    get_example_items_small,
    get_example_items_large,
    measure_time
)
from algorithms.greedy import (
    greedy_knapsack_by_value,
    greedy_knapsack_by_weight,
    greedy_knapsack_by_density
)
from algorithms.brute_force import brute_force_knapsack
from algorithms.dynamic import dynamic_programming_knapsack

def print_results(algo_name, result_tuple, exec_time):
    """Pomocnicza funkcja do ładnego drukowania wyników."""
    if result_tuple is None:
        print(f"--- {algo_name} ---")
        print("  Błąd podczas wykonywania algorytmu.")
        print(f"  Czas wykonania: {exec_time:.6f} s (czas do wystąpienia błędu)")
        print("-" * (len(algo_name) + 6))
        return

    value, weight, items = result_tuple
    item_ids = sorted([item['id'] for item in items]) # Sortujemy ID dla spójności

    print(f"--- {algo_name} ---")
    print(f"  Wybrane przedmioty ({len(item_ids)}): {item_ids}")
    print(f"  Łączna wartość: {value:.2f}") # Formatowanie do 2 miejsc po przecinku
    print(f"  Łączna waga: {weight}")
    print(f"  Czas wykonania: {exec_time:.6f} s")
    print("-" * (len(algo_name) + 6))

if __name__ == "__main__":
    print("===== Uruchamianie Algorytmów Problemu Plecakowego =====")

    # --- Konfiguracja ---
    # Wybierz źródło danych: 'small', 'large', 'csv_small', 'csv_large'
    data_source = 'large' # Możesz zmienić na inne np. 'csv_large'
    knapsack_capacity = 5 # Ustaw odpowiednią pojemność

    # Ścieżki do plików CSV (jeśli używane)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path_small = os.path.join(script_dir, 'data', 'example_items.csv')
    csv_path_large = os.path.join(script_dir, 'data', 'items_large.csv')

    # --- Wczytywanie danych ---
    items = None
    print(f"\n--- Wczytywanie danych (źródło: {data_source}) ---")
    if data_source == 'small':
        items = get_example_items_small()
        print(f"Wczytano {len(items)} przedmiotów (mały zestaw predefiniowany).")
    elif data_source == 'large':
        items = get_example_items_large()
        print(f"Wczytano {len(items)} przedmiotów (duży zestaw predefiniowany).")
    elif data_source == 'csv_small':
        items = load_items_from_csv(csv_path_small)
        if items:
             print(f"Wczytano {len(items)} przedmiotów z {csv_path_small}.")
    elif data_source == 'csv_large':
        items = load_items_from_csv(csv_path_large)
        if items:
             print(f"Wczytano {len(items)} przedmiotów z {csv_path_large}.")
    else:
        print(f"Błąd: Nieznane źródło danych '{data_source}'.")

    if items is None:
        print("Błąd wczytywania danych. Prerywanie.")
    else:
        print(f"Pojemność plecaka: {knapsack_capacity}")
        print("-" * 40)

        # --- Uruchamianie algorytmów ---
        print("\n--- Uruchamianie algorytmów ---")

        # Zbieranie wyników (opcjonalnie, do późniejszej analizy)
        results = {}

        # Algorytmy Zachłanne
        try:
            result_gv, time_gv = measure_time(greedy_knapsack_by_value, items, knapsack_capacity)
            print_results("Zachłanny (Wartość)", result_gv, time_gv)
            results['greedy_value'] = {'result': result_gv, 'time': time_gv}
        except Exception as e:
            print(f"Błąd wykonania Zachłanny (Wartość): {e}")
            results['greedy_value'] = {'result': None, 'time': -1} # Oznaczenie błędu

        try:
            result_gw, time_gw = measure_time(greedy_knapsack_by_weight, items, knapsack_capacity)
            print_results("Zachłanny (Waga)", result_gw, time_gw)
            results['greedy_weight'] = {'result': result_gw, 'time': time_gw}
        except Exception as e:
            print(f"Błąd wykonania Zachłanny (Waga): {e}")
            results['greedy_weight'] = {'result': None, 'time': -1}

        try:
            result_gd, time_gd = measure_time(greedy_knapsack_by_density, items, knapsack_capacity)
            print_results("Zachłanny (Gęstość)", result_gd, time_gd)
            results['greedy_density'] = {'result': result_gd, 'time': time_gd}
        except Exception as e:
            print(f"Błąd wykonania Zachłanny (Gęstość): {e}")
            results['greedy_density'] = {'result': None, 'time': -1}

        # Brute Force
        # Uwaga: Może być bardzo wolny dla dużych zestawów danych (n > 20-25)!
        num_items = len(items)
        if num_items > 20: # Próg bezpieczeństwa
            print("\n--- Brute Force ---")
            print(f"  Pominięto: Zbyt wiele przedmiotów ({num_items}) dla Brute Force.")
            print("-" * 18)
            results['brute_force'] = {'result': None, 'time': -2} # Oznaczenie pominięcia
        else:
            try:
                result_bf, time_bf = measure_time(brute_force_knapsack, items, knapsack_capacity)
                print_results("Brute Force", result_bf, time_bf)
                results['brute_force'] = {'result': result_bf, 'time': time_bf}
            except Exception as e:
                print(f"Błąd wykonania Brute Force: {e}")
                results['brute_force'] = {'result': None, 'time': -1}


        # Programowanie Dynamiczne
        try:
            # Sprawdzenie, czy pojemność jest int (wymagane przez DP)
            if not isinstance(knapsack_capacity, int):
                 raise TypeError("Pojemność plecaka musi być liczbą całkowitą dla Programowania Dynamicznego.")
            result_dp, time_dp = measure_time(dynamic_programming_knapsack, items, knapsack_capacity)
            print_results("Programowanie Dynamiczne", result_dp, time_dp)
            results['dynamic'] = {'result': result_dp, 'time': time_dp}
        except (ValueError, TypeError) as e: # Obsługa błędów specyficznych dla DP
             print(f"\n--- Programowanie Dynamiczne ---")
             print(f"  Błąd: {e}")
             print(f"  Upewnij się, że pojemność i wagi przedmiotów są nieujemnymi liczbami całkowitymi.")
             print("-" * 29)
             results['dynamic'] = {'result': None, 'time': -1}
        except Exception as e:
            print(f"Błąd wykonania Programowanie Dynamiczne: {e}")
            results['dynamic'] = {'result': None, 'time': -1}


        print("\n===== Zakończono uruchamianie algorytmów =====")

        # --- Generowanie wykresów porównawczych ---
        if results: # Sprawdź, czy słownik results nie jest pusty
            # Użyj nazwy źródła danych i pojemności w nazwie pliku dla unikalności
            plot_filename_prefix = f"comparison_{data_source}_cap{knapsack_capacity}"
            try:
                # Wywołanie funkcji z comparison.py
                plot_comparison(results, knapsack_capacity, data_source, filename_prefix=plot_filename_prefix)
            except Exception as e:
                 print(f"\nBłąd podczas generowania wykresów: {e}")
        else: # Ten blok wykonuje się TYLKO jeśli 'results' jest puste
            print("\nNie zebrano żadnych wyników, pomijanie generowania wykresów.")

        print("\n===== Koniec programu =====") # Dodajmy końcowy komunikat