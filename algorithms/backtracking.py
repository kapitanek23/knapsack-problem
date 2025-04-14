# algorithms/backtracking.py

def backtracking_knapsack(items, capacity):
    """
    Rozwiązuje problem plecakowy 0/1 za pomocą algorytmu z powrotami (backtracking).
    Gwarantuje znalezienie optymalnego rozwiązania.

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
        capacity (int or float): Maksymalna pojemność plecaka.

    Returns:
        tuple: Krotka zawierająca:
            - max_value (int or float): Największa znaleziona wartość.
            - best_weight (int or float): Łączna waga najlepszej kombinacji.
            - best_combination_items (list): Lista słowników przedmiotów w najlepszej kombinacji.
    """
    n = len(items)
    max_value_found = 0
    best_selection_mask = [False] * n # Maska boolowska śledząca najlepszą kombinację

    # Funkcja rekurencyjna (helper)
    def _backtrack(index, current_weight, current_value, current_selection_mask):
        nonlocal max_value_found, best_selection_mask

        # Warunek podstawowy: Jeśli doszliśmy do końca przedmiotów lub przekroczyliśmy pojemność
        # (chociaż przekroczenie pojemności obsługujemy przed wywołaniem rekurencyjnym)
        # Sprawdzamy, czy obecne rozwiązanie jest lepsze od najlepszego dotychczas
        if current_value > max_value_found:
             max_value_found = current_value
             # Zapisujemy kopię maski obecnego najlepszego wyboru
             best_selection_mask = list(current_selection_mask)

        # Warunek podstawowy - koniec eksploracji tej gałęzi
        if index == n:
            return

        # --- Rozważenie przedmiotu o indeksie 'index' ---

        # 1. Opcja: NIE BIERZ przedmiotu items[index]
        # Po prostu przechodzimy do następnego przedmiotu
        _backtrack(index + 1, current_weight, current_value, current_selection_mask)

        # 2. Opcja: SPRÓBUJ WZIĄĆ przedmiot items[index]
        item = items[index]
        if current_weight + item['weight'] <= capacity:
            # Oznaczamy przedmiot jako wzięty w tej ścieżce
            current_selection_mask[index] = True
            # Wywołanie rekurencyjne dla następnego przedmiotu z zaktualizowaną wagą i wartością
            _backtrack(index + 1, current_weight + item['weight'], current_value + item['value'], current_selection_mask)
            # BACKTRACK: Cofa wybór - oznaczamy przedmiot jako NIE wzięty, aby
            # umożliwić eksplorację innych ścieżek (głównie ważne dla wyższych poziomów rekurencji)
            current_selection_mask[index] = False


    # Inicjalizacja i start rekurencji
    initial_mask = [False] * n
    _backtrack(0, 0, 0, initial_mask)

    # Odtworzenie listy przedmiotów i wagi na podstawie najlepszej maski
    best_combination_items = []
    best_weight = 0
    for i in range(n):
        if best_selection_mask[i]:
            item = items[i]
            best_combination_items.append(item)
            best_weight += item['weight']

    return max_value_found, best_weight, best_combination_items

# Blok testowy
if __name__ == "__main__":
    # Dane z naszej ręcznej analizy
    example_items = [
        {'id': 'A', 'value': 60, 'weight': 5},
        {'id': 'B', 'value': 50, 'weight': 3},
        {'id': 'C', 'value': 70, 'weight': 4},
        {'id': 'D', 'value': 30, 'weight': 2},
    ]
    max_capacity = 10

    print("--- Test Algorytmu Backtracking ---")
    print(f"Przedmioty: {example_items}")
    print(f"Pojemność plecaka: {max_capacity}\n")

    # Mierzenie czasu wykonania (opcjonalne, ale przydatne)
    import time
    start_time = time.perf_counter()
    bt_value, bt_weight, bt_items = backtracking_knapsack(example_items, max_capacity)
    end_time = time.perf_counter()
    exec_time = end_time - start_time

    print(f"Backtracking:")
    selected_ids = sorted([item['id'] for item in bt_items])
    print(f"  Wybrane przedmioty: {selected_ids}")
    print(f"  Optymalna wartość: {bt_value}")
    print(f"  Waga przy optymalnej wartości: {bt_weight}")
    print(f"  Czas wykonania: {exec_time:.6f} s\n")

    # Porównanie z innymi algorytmami
    try:
        from algorithms.brute_force import brute_force_knapsack
        from algorithms.dynamic import dynamic_programming_knapsack

        bf_value, _, _ = brute_force_knapsack(example_items, max_capacity)
        dp_value, _, _ = dynamic_programming_knapsack(example_items, max_capacity)

        print("--- Porównanie Wyników (Wartość) ---")
        print(f"  Backtracking: {bt_value}")
        print(f"  Brute Force:  {bf_value}")
        print(f"  Dynamiczne:   {dp_value}")
        if bt_value == bf_value == dp_value:
             print("  Wyniki optymalne zgodne.")
        else:
             print("  UWAGA: Różne wyniki optymalne!")

    except ImportError:
        print("Nie można zaimportować innych algorytmów do porównania.")
    except Exception as e:
        print(f"Błąd podczas porównywania: {e}")