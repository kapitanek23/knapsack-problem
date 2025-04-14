# main.py
import os
import copy # Potrzebne do głębokiego kopiowania przy MKP (choć nie w tym pliku)
from utils import (
    load_items_from_csv,
    get_example_items_small,
    get_example_items_large,
    measure_time
)
# Importy dla problemu 0/1
from algorithms.greedy import (
    greedy_knapsack_by_value,
    greedy_knapsack_by_weight,
    greedy_knapsack_by_density
)
from algorithms.brute_force import brute_force_knapsack
from algorithms.dynamic import dynamic_programming_knapsack
from algorithms.backtracking import backtracking_knapsack
# Import dla problemu MKP
from algorithms.mkp_backtracking import mkp_backtracking_knapsack
# Import dla wykresów (jeśli używane dla 0/1)
from analysis.comparison import plot_comparison
from utils import generate_random_items # Dodaj ten import
import json # Do zapisywania wyników analizy
import time as py_time # Zmieńmy alias, żeby nie kolidował z naszym 'time'd


# --- Funkcje pomocnicze do drukowania ---

def print_01_results(algo_name, result_tuple, exec_time):
    """Pomocnicza funkcja do ładnego drukowania wyników dla problemu 0/1."""
    if result_tuple is None:
        # Sprawdź, czy czas to -1 (błąd) czy -2 (pominięty)
        status = "Błąd wykonania" if exec_time == -1 else "Pominięto" if exec_time == -2 else "Brak wyniku"
        time_str = f"{abs(exec_time):.6f} s" if exec_time >= 0 else "N/A" # Pokaż czas błędu, jeśli >0
        print(f"--- {algo_name} [{status}] ---")
        if exec_time >= 0 and status == "Błąd wykonania":
             print(f"  (Czas do błędu: {time_str})")
        elif status == "Pominięto":
             print("  (Zbyt wiele przedmiotów lub inna przyczyna)")
        print("-" * (len(algo_name) + 6 + len(status) + 3)) # Dostosuj długość kreski
        return

    value, weight, items = result_tuple
    item_ids = sorted([item['id'] for item in items])

    print(f"--- {algo_name} ---")
    print(f"  Wybrane przedmioty ({len(item_ids)}): {item_ids}")
    print(f"  Łączna wartość: {value:.2f}")
    print(f"  Łączna waga: {weight}")
    print(f"  Czas wykonania: {exec_time:.6f} s")
    print("-" * (len(algo_name) + 6))

def print_mkp_results(algo_name, result_tuple, exec_time, capacities_list):
    """Pomocnicza funkcja do ładnego drukowania wyników dla problemu MKP."""
    if result_tuple is None:
        # Podobnie jak wyżej, obsługa błędów/pominięć
        status = "Błąd wykonania" if exec_time == -1 else "Pominięto" if exec_time == -2 else "Brak wyniku"
        time_str = f"{abs(exec_time):.6f} s" if exec_time >= 0 else "N/A"
        print(f"--- {algo_name} [{status}] ---")
        if exec_time >= 0 and status == "Błąd wykonania":
             print(f"  (Czas do błędu: {time_str})")
        print("-" * (len(algo_name) + 6 + len(status) + 3))
        return # Zakończ, jeśli nie ma wyniku

    # Ten kod wykonuje się tylko, jeśli result_tuple NIE jest None
    total_value, assignment_dict = result_tuple
    num_knapsacks = len(capacities_list)

    print(f"--- {algo_name} ---")
    print(f"  Optymalna łączna wartość: {total_value:.2f}")
    print(f"  Czas wykonania: {exec_time:.6f} s")
    print(f"  Przypisanie przedmiotów do {num_knapsacks} plecaków:")
    total_items_assigned = 0
    for k_idx in range(num_knapsacks):
        k_items = assignment_dict.get(k_idx, []) # Pobierz listę lub pustą, jeśli brak klucza
        ids = sorted([item['id'] for item in k_items])
        weight_sum = sum(item['weight'] for item in k_items)
        capacity = capacities_list[k_idx]
        print(f"    Plecak {k_idx} (Poj: {capacity}, Waga: {weight_sum}): {ids}")
        total_items_assigned += len(k_items)
    print(f"  Łączna liczba przypisanych przedmiotów: {total_items_assigned}")
    print("-" * (len(algo_name) + 6))


# --- Funkcja do zapisu wyników skalowalności ---
# Ta funkcja jest teraz całkowicie oddzielna od print_mkp_results
def save_scalability_results(results, filepath):
    """Zapisuje wyniki analizy skalowalności do pliku JSON."""
    try:
        # 1. Utwórz katalog, jeśli nie istnieje
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 2. Otwórz plik do zapisu
        with open(filepath, 'w') as f:
            # 3. Zapisz cały słownik 'results' do pliku JSON
            json.dump(results, f, indent=4)

        # 4. Wydrukuj komunikat o sukcesie
        print(f"  Zapisano wyniki analizy skalowalności do: {filepath}")

    except Exception as e:
        # 5. Obsłuż ewentualne błędy zapisu
        print(f"  Błąd podczas zapisu wyników analizy skalowalności: {e}")



# --- Główny blok wykonawczy ---
if __name__ == "__main__":
    print("===== Uruchamianie Algorytmów Problemu Plecakowego =====")

    # --- Konfiguracja ---
    # Zmień 'mode', aby wybrać typ problemu: '01', 'MKP' lub 'SCALABILITY'
    mode = 'SCALABILITY'  # <--- Zmień tryb

    # !!! PRZENIEŚ DEFINICJĘ script_dir TUTAJ !!!
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Konfiguracja dla trybu '01' (jeden plecak)
    knapsack_capacity_01 = 10 # Ustaw pojemność dla problemu 0/1
    data_source_01 = 'large' # 'small', 'large', 'csv_small', 'csv_large'

    # Konfiguracja dla trybu 'MKP' (wiele plecaków)
    knapsack_capacities_mkp = [10, 12] # Lista pojemności dla MKP
    data_source_mkp = 'large' # 'small', 'large', 'csv_small', 'csv_large'

    # Konfiguracja dla trybu 'SCALABILITY'
    scalability_param = 'n' # Analizuj wg 'n' (liczba przedmiotów) lub 'W' (pojemność)
    n_values = [5, 10, 15, 20, 25, 30] # Wartości 'n' do przetestowania
    W_values = [50, 100, 200, 400, 800, 1000] # Wartości 'W' do przetestowania
    fixed_W_for_n_analysis = 500 # Stała pojemność przy zmianie 'n'
    fixed_n_for_W_analysis = 20   # Stała liczba przedmiotów przy zmianie 'W'
    value_gen_range = (1, 100)
    weight_gen_range = (1, 50)
    algorithms_to_scale = ['dynamic', 'backtracking']
    # Teraz 'script_dir' jest zdefiniowane i można go użyć poniżej
    scalability_results_file = os.path.join(script_dir, 'analysis', 'results', 'scalability_results.json')

    # Ścieżki do plików CSV (mogą zostać tutaj, bo używają script_dir)
    csv_path_small = os.path.join(script_dir, 'data', 'example_items.csv')
    csv_path_large = os.path.join(script_dir, 'data', 'items_large.csv')

# --- Wczytywanie/Generowanie danych (zależne od trybu) ---
items = None # Resetuj items na początku
if mode != 'SCALABILITY':
    # Logika wczytywania dla trybów 0/1 i MKP
    data_source = data_source_01 if mode == '01' else data_source_mkp
    print(f"\n--- Wczytywanie danych (Tryb: {mode}, Źródło: {data_source}) ---")

    if data_source == 'small':
        items = get_example_items_small()
    elif data_source == 'large':
        items = get_example_items_large()
    elif data_source == 'csv_small':
        items = load_items_from_csv(csv_path_small)
    elif data_source == 'csv_large':
        items = load_items_from_csv(csv_path_large)
    else:
        print(f"Błąd: Nieznane źródło danych '{data_source}'.")

    if items:
        print(f"Wczytano {len(items)} przedmiotów.")
    else:
         # Jeśli nie jesteśmy w SCALABILITY i nie udało się wczytać, ustaw items na None
         items = None


# Sprawdzenie danych przed główną logiką trybów
# Jeśli jesteśmy w trybie innym niż SCALABILITY i nie mamy przedmiotów, to błąd.
if items is None and mode != 'SCALABILITY':
    print("Błąd wczytywania danych. Prerywanie.")
else:
    # Jeśli jesteśmy w trybie SCALABILITY, dane będą generowane w pętli,
    # więc nie potrzebujemy ich teraz. Drukujemy separator.
    print("-" * 40)

    # --- Rozdzielenie logiki dla trybu 0/1, MKP i SCALABILITY ---

    if mode == '01':
        # --- Uruchamianie algorytmów dla problemu 0/1 ---
        print(f"\n--- Uruchamianie algorytmów dla Problemu 0/1 (Pojemność: {knapsack_capacity_01}) ---")
        results_01 = {} # Słownik na wyniki tylko dla 0/1

        # Algorytmy Zachłanne
        try:
            res, time = measure_time(greedy_knapsack_by_value, items, knapsack_capacity_01)
            print_01_results("Zachłanny (Wartość)", res, time)
            results_01['greedy_value'] = {'result': res, 'time': time}
        except Exception as e: print(f"Błąd Zachłanny (Wartość): {e}"); results_01['greedy_value'] = {'result': None, 'time': -1}

        try:
            res, time = measure_time(greedy_knapsack_by_weight, items, knapsack_capacity_01)
            print_01_results("Zachłanny (Waga)", res, time)
            results_01['greedy_weight'] = {'result': res, 'time': time}
        except Exception as e: print(f"Błąd Zachłanny (Waga): {e}"); results_01['greedy_weight'] = {'result': None, 'time': -1}

        try:
            res, time = measure_time(greedy_knapsack_by_density, items, knapsack_capacity_01)
            print_01_results("Zachłanny (Gęstość)", res, time)
            results_01['greedy_density'] = {'result': res, 'time': time}
        except Exception as e: print(f"Błąd Zachłanny (Gęstość): {e}"); results_01['greedy_density'] = {'result': None, 'time': -1}

        # Brute Force
        num_items = len(items)
        if num_items > 20:
            print_01_results("Brute Force", None, -2) # -2 oznacza pominięty
            results_01['brute_force'] = {'result': None, 'time': -2}
        else:
            try:
                res, time = measure_time(brute_force_knapsack, items, knapsack_capacity_01)
                print_01_results("Brute Force", res, time)
                results_01['brute_force'] = {'result': res, 'time': time}
            except Exception as e: print(f"Błąd Brute Force: {e}"); results_01['brute_force'] = {'result': None, 'time': -1}

        # Backtracking 0/1
        try:
            res, time = measure_time(backtracking_knapsack, items, knapsack_capacity_01)
            print_01_results("Backtracking (0/1)", res, time)
            results_01['backtracking'] = {'result': res, 'time': time}
        except RecursionError:
             print_01_results("Backtracking (0/1)", None, -1); results_01['backtracking'] = {'result': None, 'time': -1}
             print("  (Przekroczono głębokość rekursji)")
        except Exception as e: print(f"Błąd Backtracking (0/1): {e}"); results_01['backtracking'] = {'result': None, 'time': -1}

        # Programowanie Dynamiczne
        try:
            if not isinstance(knapsack_capacity_01, int): raise TypeError("Pojemność musi być int dla DP.")
            res, time = measure_time(dynamic_programming_knapsack, items, knapsack_capacity_01)
            print_01_results("Programowanie Dynamiczne", res, time)
            results_01['dynamic'] = {'result': res, 'time': time}
        except (ValueError, TypeError) as e:
             print_01_results("Programowanie Dynamiczne", None, -1); results_01['dynamic'] = {'result': None, 'time': -1}
             print(f"  (Błąd wymagań DP: {e})")
        except Exception as e: print(f"Błąd Prog. Dynamiczne: {e}"); results_01['dynamic'] = {'result': None, 'time': -1}

        print("\n===== Zakończono uruchamianie algorytmów 0/1 =====")

        # --- Generowanie wykresów TYLKO dla problemu 0/1 ---
        if results_01:
            # Filtruj wyniki, usuwając te z czasem < 0
            valid_results_01 = {k: v for k, v in results_01.items() if v and v.get('time', -1) >= 0}
            if valid_results_01:
                 plot_filename_prefix = f"comparison_{data_source}_01_cap{knapsack_capacity_01}"
                 try:
                     # Używamy oryginalnej funkcji plot_comparison
                     plot_comparison(valid_results_01, knapsack_capacity_01, data_source, filename_prefix=plot_filename_prefix)
                 except Exception as e:
                      print(f"\nBłąd podczas generowania wykresów 0/1: {e}")
            else:
                 print("\nBrak poprawnych wyników 0/1 do wygenerowania wykresów.")
        else:
            print("\nNie zebrano żadnych wyników 0/1, pomijanie generowania wykresów.")


    elif mode == 'MKP':
        # --- Uruchamianie algorytmów dla problemu MKP ---
        print(f"\n--- Uruchamianie algorytmów dla Problemu MKP (Pojemności: {knapsack_capacities_mkp}) ---")
        results_mkp = {} # Osobny słownik na wyniki MKP

        # Backtracking MKP
        try:
            res, time = measure_time(mkp_backtracking_knapsack, items, knapsack_capacities_mkp)
            # Używamy nowej funkcji do drukowania wyników MKP
            print_mkp_results("Backtracking (MKP)", res, time, knapsack_capacities_mkp)
            results_mkp['mkp_backtracking'] = {'result': res, 'time': time}
        except RecursionError:
             print_mkp_results("Backtracking (MKP)", None, -1, knapsack_capacities_mkp); results_mkp['mkp_backtracking'] = {'result': None, 'time': -1}
             print("  (Przekroczono głębokość rekursji)")
        except Exception as e: print(f"Błąd Backtracking (MKP): {e}"); results_mkp['mkp_backtracking'] = {'result': None, 'time': -1}

        # Dodaj tutaj wywołania innych algorytmów MKP, jeśli je zaimplementujesz

        print("\n===== Zakończono uruchamianie algorytmów MKP =====")

        # --- Generowanie Wykresów/Analizy dla MKP (jeśli potrzebne) ---
        if results_mkp:
            print("\n--- Analiza wyników MKP (dalsze kroki) ---")
            print("  Zebrano wyniki dla MKP.")
             # Można dodać zapis do pliku itp.
        else:
            print("\nNie zebrano żadnych wyników MKP.")


    elif mode == 'SCALABILITY':
        print(f"\n--- Uruchamianie Analizy Skalowalności (parametr: {scalability_param}) ---")
        scalability_results = {'param': scalability_param, 'values': [], 'times': {algo: [] for algo in algorithms_to_scale}}

        if scalability_param == 'n':
            param_values_to_test = n_values
            fixed_capacity = fixed_W_for_n_analysis
            print(f"Analiza czasu w zależności od liczby przedmiotów 'n' (stała pojemność W={fixed_capacity})")
            scalability_results['fixed_param'] = 'W'
            scalability_results['fixed_value'] = fixed_capacity

            for n in param_values_to_test:
                print(f"\nTestowanie dla n = {n}...")
                try:
                     current_items = generate_random_items(n, value_gen_range, weight_gen_range)
                     print(f"  Wygenerowano {len(current_items)} przedmiotów.")
                     scalability_results['values'].append(n)

                     for algo_name in algorithms_to_scale:
                         algo_func = None
                         if algo_name == 'dynamic': algo_func = dynamic_programming_knapsack
                         elif algo_name == 'backtracking': algo_func = backtracking_knapsack
                         elif algo_name == 'brute_force': algo_func = brute_force_knapsack

                         if algo_func:
                             if algo_name == 'brute_force' and n > 20:
                                 print(f"  Pominięto Brute Force dla n={n}")
                                 time = -2
                             else:
                                 # Sprawdzenie dla DP czy pojemność jest int
                                 capacity_arg = fixed_capacity
                                 if algo_name == 'dynamic' and not isinstance(capacity_arg, int):
                                      print(f"  Błąd: Pojemność {capacity_arg} nie jest int dla DP.")
                                      time = -1
                                 else:
                                     # Uruchomienie algorytmu
                                     try:
                                         res, time = measure_time(algo_func, current_items, capacity_arg)
                                     except RecursionError:
                                         print(f"  Błąd rekursji dla {algo_name} przy n={n}")
                                         time = -1 # Oznacz błąd
                                     except Exception as e_inner:
                                         print(f"  Błąd wykonania {algo_name} dla n={n}: {e_inner}")
                                         time = -1 # Oznacz błąd
                         else:
                             print(f"  Nieznany algorytm w analizie: {algo_name}")
                             time = -1

                         print(f"  {algo_name}: czas = {time:.6f} s" if time >= 0 else f"  {algo_name}: {'Pominięto' if time==-2 else 'Błąd'}")
                         scalability_results['times'][algo_name].append(time)

                except Exception as e:
                    print(f"  Błąd podczas testowania dla n={n}: {e}")
                    for algo_name in algorithms_to_scale:
                         if len(scalability_results['times'][algo_name]) < len(scalability_results['values']):
                            scalability_results['times'][algo_name].append(-1)


        elif scalability_param == 'W':
            param_values_to_test = W_values
            fixed_n = fixed_n_for_W_analysis
            print(f"Analiza czasu w zależności od pojemności 'W' (stała liczba przedmiotów n={fixed_n})")
            scalability_results['fixed_param'] = 'n'
            scalability_results['fixed_value'] = fixed_n

            print(f"Generowanie stałego zestawu {fixed_n} przedmiotów...")
            try:
                current_items = generate_random_items(fixed_n, value_gen_range, weight_gen_range)
                print(f"  Wygenerowano {len(current_items)} przedmiotów.")

                for W in param_values_to_test:
                    print(f"\nTestowanie dla W = {W}...")
                    scalability_results['values'].append(W)

                    for algo_name in algorithms_to_scale:
                         algo_func = None
                         if algo_name == 'dynamic': algo_func = dynamic_programming_knapsack
                         elif algo_name == 'backtracking': algo_func = backtracking_knapsack
                         elif algo_name == 'brute_force': algo_func = brute_force_knapsack

                         if algo_func:
                             if algo_name == 'brute_force' and fixed_n > 20:
                                 time = -2 # Pominięty
                             else:
                                 # Sprawdzenie dla DP czy W jest int
                                 capacity_arg = W
                                 if algo_name == 'dynamic' and not isinstance(capacity_arg, int):
                                      print(f"  Błąd: Pojemność {capacity_arg} nie jest int dla DP.")
                                      time = -1
                                 else:
                                     try:
                                         res, time = measure_time(algo_func, current_items, capacity_arg)
                                     except Exception as e_inner:
                                         print(f"  Błąd wykonania {algo_name} dla W={W}: {e_inner}")
                                         time = -1
                         else:
                             time = -1 # Błąd nieznanego algorytmu

                         print(f"  {algo_name}: czas = {time:.6f} s" if time >= 0 else f"  {algo_name}: {'Pominięto' if time==-2 else 'Błąd'}")
                         scalability_results['times'][algo_name].append(time)

            except Exception as e:
                print(f"Błąd podczas generowania przedmiotów lub testowania dla analizy W: {e}")


        else:
            print(f"Błąd: Nieznany parametr analizy skalowalności '{scalability_param}'. Wybierz 'n' lub 'W'.")

        # Zapisz wyniki analizy do pliku JSON
        if scalability_results.get('values'): # Sprawdź, czy lista wartości nie jest pusta
             save_scalability_results(scalability_results, scalability_results_file)
        else:
             print("\nNie zebrano żadnych danych do analizy skalowalności.")

        print("\n===== Zakończono analizę skalowalności =====")


    else:
         print(f"Błąd: Nieznany tryb '{mode}'. Wybierz '01', 'MKP' lub 'SCALABILITY'.")


print("\n===== Koniec programu =====") # Ten print jest teraz na końcu, po całej logice if/elif/else dla mode