# algorithms/brute_force.py
import itertools # Można użyć itertools, ale zrobimy to ręcznie z bitmaską

def brute_force_knapsack(items, capacity):
    """
    Rozwiązuje problem plecakowy 0/1 za pomocą algorytmu Brute Force.
    Sprawdza wszystkie możliwe kombinacje przedmiotów.

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
        capacity (int or float): Maksymalna pojemność plecaka.

    Returns:
        tuple: Krotka zawierająca:
            - max_value (int or float): Największa znaleziona wartość.
            - best_weight (int or float): Łączna waga najlepszej kombinacji.
            - best_combination (list): Lista słowników przedmiotów w najlepszej kombinacji.
            Gwarantuje znalezienie optymalnego rozwiązania.
    """
    n = len(items)
    max_value = 0
    best_weight = 0
    best_combination_indices = [] # Przechowamy indeksy najlepszej kombinacji

    # Iterujemy przez wszystkie możliwe podzbiory (od 0 do 2^n - 1)
    # Każda liczba 'i' reprezentuje jeden podzbiór za pomocą swoich bitów
    for i in range(2**n):
        current_value = 0
        current_weight = 0
        current_combination_indices = []

        # Sprawdzamy, które przedmioty należą do bieżącego podzbioru (i)
        for j in range(n):
            # Sprawdzamy, czy j-ty bit w 'i' jest ustawiony (równy 1)
            # Jeśli tak, to j-ty przedmiot należy do tej kombinacji
            if (i >> j) & 1:
                item = items[j]
                current_value += item['value']
                current_weight += item['weight']
                current_combination_indices.append(j)

        # Sprawdzamy, czy bieżąca kombinacja mieści się w plecaku
        if current_weight <= capacity:
            # Jeśli tak, sprawdzamy, czy jest lepsza od dotychczas najlepszej
            if current_value > max_value:
                max_value = current_value
                best_weight = current_weight
                best_combination_indices = current_combination_indices

    # Odtwarzamy listę przedmiotów na podstawie najlepszych indeksów
    best_combination_items = [items[idx] for idx in best_combination_indices]

    return max_value, best_weight, best_combination_items

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

    print("--- Test Algorytmu Brute Force ---")
    print(f"Przedmioty: {example_items}")
    print(f"Pojemność plecaka: {max_capacity}\n")

    bf_value, bf_weight, bf_items = brute_force_knapsack(example_items, max_capacity)

    print(f"Brute Force:")
    # Sortowanie wyników dla spójności (nie jest konieczne, ale ułatwia porównanie)
    selected_ids = sorted([item['id'] for item in bf_items])
    print(f"  Wybrane przedmioty: {selected_ids}")
    print(f"  Optymalna wartość: {bf_value}")
    print(f"  Waga przy optymalnej wartości: {bf_weight}\n")

    # Porównanie z wynikami zachłannymi (wymaga uruchomienia z głównego folderu lub importu)
    try:
        # Zakładamy, że uruchamiamy z głównego folderu projektu
        from algorithms.greedy import greedy_knapsack_by_value, greedy_knapsack_by_weight, greedy_knapsack_by_density

        print("--- Porównanie z Algorytmami Zachłannymi ---")
        val_value, _, _ = greedy_knapsack_by_value(example_items, max_capacity)
        wei_value, _, _ = greedy_knapsack_by_weight(example_items, max_capacity)
        den_value, _, _ = greedy_knapsack_by_density(example_items, max_capacity)
        print(f"  Zachłanny (Wartość): {val_value}")
        print(f"  Zachłanny (Waga):    {wei_value}")
        print(f"  Zachłanny (Gęstość): {den_value}")
        print(f"  Brute Force (Opt.): {bf_value}")

    except ImportError:
        print("Nie można zaimportować algorytmów zachłannych. Uruchom testy z głównego folderu projektu.")