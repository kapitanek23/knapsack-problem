# algorithms/mkp_backtracking.py
import copy # Do głębokiego kopiowania stanu

def mkp_backtracking_knapsack(items, capacities):
    """
    Rozwiązuje Problem Wielu Plecaków (MKP) 0/1 za pomocą backtrackingu.

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
        capacities (list): Lista pojemności poszczególnych plecaków [W_1, W_2, ..., W_m].

    Returns:
        tuple: Krotka zawierająca:
            - max_total_value (float): Maksymalna łączna wartość przedmiotów we wszystkich plecakach.
            - best_assignment (dict): Słownik, gdzie klucze to indeksy plecaków (0 do m-1),
                                      a wartości to listy przedmiotów przypisanych do danego plecaka.
                                      Np. {0: [item1, item3], 1: [item2], ...}
    """
    n = len(items)
    m = len(capacities)

    max_total_value = 0
    # Przechowuje najlepszy znaleziony podział przedmiotów między plecaki
    # Format: {knapsack_idx: [item_dict, ...], ...}
    best_assignment_dict = {k: [] for k in range(m)}

    # Funkcja rekurencyjna
    def _backtrack(item_index, current_capacities, current_value, current_assignment_dict):
        nonlocal max_total_value, best_assignment_dict

        # Sprawdzenie, czy obecne rozwiązanie jest lepsze (robimy to tutaj i w bazie)
        if current_value > max_total_value:
            max_total_value = current_value
            # Musimy zrobić głęboką kopię słownika przypisań!
            best_assignment_dict = copy.deepcopy(current_assignment_dict)

        # Warunek bazowy rekurencji: rozważono wszystkie przedmioty
        if item_index == n:
            return

        current_item = items[item_index]
        item_weight = current_item['weight']
        item_value = current_item['value']

        # --- Decyzje dla przedmiotu item_index ---

        # 1. Opcja: NIE BIERZ przedmiotu
        _backtrack(item_index + 1, current_capacities, current_value, current_assignment_dict)

        # 2. Opcja: SPRÓBUJ WZIĄĆ przedmiot i umieścić w plecaku k (dla k = 0 do m-1)
        for k in range(m):
            # Sprawdź, czy przedmiot zmieści się w plecaku k
            if current_capacities[k] >= item_weight:
                # "Włóż" przedmiot do plecaka k
                current_capacities[k] -= item_weight
                current_assignment_dict[k].append(current_item)

                # Wywołanie rekurencyjne dla następnego przedmiotu
                _backtrack(item_index + 1,
                           current_capacities,
                           current_value + item_value, # Wartość zwiększa się globalnie
                           current_assignment_dict)

                # BACKTRACK: "Wyjmij" przedmiot z plecaka k
                # Usuń ostatnio dodany przedmiot (czyli current_item)
                current_assignment_dict[k].pop()
                current_capacities[k] += item_weight # Przywróć pojemność


    # Inicjalizacja i start
    initial_capacities = list(capacities) # Kopia listy pojemności
    initial_assignment = {k: [] for k in range(m)}
    _backtrack(0, initial_capacities, 0, initial_assignment)

    return max_total_value, best_assignment_dict

# Blok testowy
if __name__ == "__main__":
    # Przykładowe dane dla MKP
    items_mkp = [
        {'id': 'A', 'value': 8, 'weight': 5},
        {'id': 'B', 'value': 10, 'weight': 8},
        {'id': 'C', 'value': 6, 'weight': 4},
        {'id': 'D', 'value': 4, 'weight': 3},
        {'id': 'E', 'value': 7, 'weight': 6},
    ]
    # Dwa plecaki o różnych pojemnościach
    knapsack_capacities_mkp = [10, 12]

    print("--- Test Algorytmu Backtracking dla MKP ---")
    print(f"Przedmioty: {items_mkp}")
    print(f"Pojemności plecaków: {knapsack_capacities_mkp}\n")

    import time
    start_time = time.perf_counter()
    mkp_value, mkp_assignment = mkp_backtracking_knapsack(items_mkp, knapsack_capacities_mkp)
    end_time = time.perf_counter()
    exec_time = end_time - start_time

    print(f"Backtracking MKP:")
    print(f"  Optymalna łączna wartość: {mkp_value}")
    print(f"  Czas wykonania: {exec_time:.6f} s")
    print(f"  Przypisanie przedmiotów:")
    total_weight_check = 0
    for k_idx, k_items in mkp_assignment.items():
        ids = [item['id'] for item in k_items]
        weight_sum = sum(item['weight'] for item in k_items)
        total_weight_check += weight_sum
        print(f"    Plecak {k_idx} (Poj: {knapsack_capacities_mkp[k_idx]}, Waga: {weight_sum}): {ids}")

    # Uwaga: Porównanie z innymi algorytmami MKP wymagałoby ich implementacji (np. heurystyk).
    # Nie możemy bezpośrednio porównać z naszymi algorytmami 0/1.