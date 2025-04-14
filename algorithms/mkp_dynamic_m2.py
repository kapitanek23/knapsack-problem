# algorithms/mkp_dynamic_m2.py
import numpy as np # Użyjemy numpy dla łatwiejszej obsługi tabeli 3D

def mkp_dynamic_programming_m2(items, capacity1, capacity2):
    """
    Rozwiązuje Problem Wielu Plecaków (MKP) 0/1 dla DOKŁADNIE DWÓCH PLECAKÓW
    za pomocą programowania dynamicznego.

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
                      Wagi muszą być liczbami całkowitymi >= 0.
        capacity1 (int): Pojemność pierwszego plecaka (całkowita >= 0).
        capacity2 (int): Pojemność drugiego plecaka (całkowita >= 0).

    Returns:
        tuple: Krotka zawierająca:
            - max_total_value (float): Maksymalna łączna wartość przedmiotów.
            - assignment (dict): Słownik {0: [item_list_1], 1: [item_list_2]}
                                 z przypisaniem przedmiotów.
    """
    n = len(items)

    # Walidacja typów wejściowych
    if not isinstance(capacity1, int) or capacity1 < 0 or \
       not isinstance(capacity2, int) or capacity2 < 0:
        raise ValueError("Pojemności plecaków muszą być nieujemnymi liczbami całkowitymi.")
    for item in items:
        if not isinstance(item['weight'], int) or item['weight'] < 0:
            raise ValueError(f"Waga przedmiotu {item['id']} musi być nieujemną liczbą całkowitą.")

    # Inicjalizacja tabeli DP: (n+1) x (cap1+1) x (cap2+1)
    # Wypełniamy wartością -1, aby odróżnić stany nieosiągalne od wartości 0
    dp = np.full((n + 1, capacity1 + 1, capacity2 + 1), -1.0, dtype=float)
    # Stan początkowy: 0 przedmiotów, 0 wagi, 0 wartości
    dp[0, 0, 0] = 0.0

    # Wypełnianie tabeli DP
    for i in range(1, n + 1):
        item = items[i-1]
        item_w = item['weight']
        item_v = item['value']

        for w1 in range(capacity1 + 1):
            for w2 in range(capacity2 + 1):
                # Opcja 1: Nie bierz przedmiotu i
                # Wartość dziedziczona z poprzedniego przedmiotu przy tych samych wagach
                value_dont_take = dp[i-1, w1, w2]

                # Opcja 2: Weź przedmiot i do plecaka 1
                value_take_1 = -1.0 # Wartość niemożliwa na start
                if w1 >= item_w and dp[i-1, w1 - item_w, w2] != -1: # Czy stan źródłowy był osiągalny?
                    value_take_1 = item_v + dp[i-1, w1 - item_w, w2]

                # Opcja 3: Weź przedmiot i do plecaka 2
                value_take_2 = -1.0 # Wartość niemożliwa na start
                if w2 >= item_w and dp[i-1, w1, w2 - item_w] != -1: # Czy stan źródłowy był osiągalny?
                    value_take_2 = item_v + dp[i-1, w1, w2 - item_w]

                # Wybierz maksimum z możliwych opcji
                # Upewnij się, że bierzemy pod uwagę tylko osiągalne stany (wartości >= 0)
                possible_values = [v for v in [value_dont_take, value_take_1, value_take_2] if v >= 0]
                dp[i, w1, w2] = max(possible_values) if possible_values else -1.0


    # Znajdź maksymalną wartość w ostatniej warstwie tabeli
    # (może nie być możliwe zapełnienie obu plecaków do pełna)
    max_total_value = np.max(dp[n, :, :])
    if max_total_value < 0: # Jeśli żadna kombinacja nie jest możliwa (np. wszystkie przedmioty za ciężkie)
         max_total_value = 0.0

    # Odtworzenie przypisania (backtracking)
    assignment = {0: [], 1: []}
    if max_total_value > 0: # Tylko jeśli znaleziono jakieś rozwiązanie
        # Znajdź indeksy w1, w2, gdzie występuje max_total_value
        w1, w2 = np.unravel_index(np.argmax(dp[n, :, :], axis=None), dp[n, :, :].shape)

        for i in range(n, 0, -1):
            item = items[i-1]
            item_w = item['weight']
            item_v = item['value']
            current_dp_val = dp[i, w1, w2]

            # Sprawdź, czy wartość pochodzi z NIE wzięcia przedmiotu i
            if current_dp_val == dp[i-1, w1, w2]:
                continue # Przejdź do poprzedniego przedmiotu

            # Sprawdź, czy wartość pochodzi z wzięcia do plecaka 1
            elif w1 >= item_w and dp[i-1, w1 - item_w, w2] != -1 and \
                 abs(current_dp_val - (item_v + dp[i-1, w1 - item_w, w2])) < 1e-9: # Porównanie float
                assignment[0].append(item)
                w1 -= item_w
                continue # Przejdź do poprzedniego przedmiotu

            # Sprawdź, czy wartość pochodzi z wzięcia do plecaka 2
            elif w2 >= item_w and dp[i-1, w1, w2 - item_w] != -1 and \
                 abs(current_dp_val - (item_v + dp[i-1, w1, w2 - item_w])) < 1e-9: # Porównanie float
                assignment[1].append(item)
                w2 -= item_w
                continue # Przejdź do poprzedniego przedmiotu

            # Jeśli żaden warunek nie pasuje, może być błąd lub problem z floatami
            # print(f"Ostrzeżenie: Problem z backtrackingiem przy przedmiocie {i-1}")


    # Odwróć listy, bo dodawaliśmy od końca
    assignment[0].reverse()
    assignment[1].reverse()

    return max_total_value, assignment

# Blok testowy
if __name__ == "__main__":
    # Dane z testu MKP Backtracking
    items_mkp = [
        {'id': 'A', 'value': 8, 'weight': 5},
        {'id': 'B', 'value': 10, 'weight': 8},
        {'id': 'C', 'value': 6, 'weight': 4},
        {'id': 'D', 'value': 4, 'weight': 3},
        {'id': 'E', 'value': 7, 'weight': 6},
    ]
    knapsack_capacity1 = 10
    knapsack_capacity2 = 12

    print("--- Test Algorytmu DP dla MKP (m=2) ---")
    print(f"Przedmioty: {items_mkp}")
    print(f"Pojemności plecaków: [{knapsack_capacity1}, {knapsack_capacity2}]\n")

    import time
    start_time = time.perf_counter()

    try:
        # Zainstaluj numpy, jeśli go nie masz: pip install numpy
        dp_value, dp_assignment = mkp_dynamic_programming_m2(items_mkp, knapsack_capacity1, knapsack_capacity2)
        end_time = time.perf_counter()
        exec_time = end_time - start_time

        print(f"DP MKP (m=2):")
        print(f"  Optymalna łączna wartość: {dp_value:.2f}")
        print(f"  Czas wykonania: {exec_time:.6f} s")
        print(f"  Przypisanie przedmiotów:")
        for k_idx, k_items in dp_assignment.items():
            ids = [item['id'] for item in k_items]
            weight_sum = sum(item['weight'] for item in k_items)
            capacity = knapsack_capacity1 if k_idx == 0 else knapsack_capacity2
            print(f"    Plecak {k_idx} (Poj: {capacity}, Waga: {weight_sum}): {ids}")

        # Porównanie z Backtrackingiem MKP
        from mkp_backtracking import mkp_backtracking_knapsack
        print("\nPorównanie z Backtrackingiem MKP:")
        bt_value, _ = mkp_backtracking_knapsack(items_mkp, [knapsack_capacity1, knapsack_capacity2])
        print(f"  Wartość DP (m=2): {dp_value:.2f}")
        print(f"  Wartość BT:     {bt_value:.2f}")
        if abs(dp_value - bt_value) < 1e-9:
             print("  Wyniki zgodne.")
        else:
             print("  UWAGA: Różne wyniki!")

    except ImportError:
        print("\nBŁĄD: Biblioteka NumPy nie jest zainstalowana.")
        print("Uruchom: pip install numpy")
        print("Lub: pip3 install numpy")
    except ValueError as e:
        print(f"\nBŁĄD: {e}")
    except Exception as e:
         print(f"\nNieoczekiwany błąd: {e}")