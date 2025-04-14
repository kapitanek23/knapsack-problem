# algorithms/dynamic.py

def dynamic_programming_knapsack(items, capacity):
    """
    Rozwiązuje problem plecakowy 0/1 za pomocą programowania dynamicznego.
    Gwarantuje znalezienie optymalnego rozwiązania.

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
                      Zakłada się, że wagi są liczbami całkowitymi >= 0.
                      Pojemność również powinna być liczbą całkowitą >= 0.
        capacity (int): Maksymalna pojemność plecaka (całkowita).

    Returns:
        tuple: Krotka zawierająca:
            - max_value (int): Optymalna łączna wartość przedmiotów.
            - total_weight (int): Łączna waga przedmiotów w optymalnym rozwiązaniu.
            - selected_items (list): Lista słowników przedmiotów wybranych do plecaka.
    """
    n = len(items)
    # Wagi i pojemność muszą być całkowite dla tej implementacji DP
    # Można dostosować do float, ale wymaga to innych struktur lub skalowania
    if not isinstance(capacity, int) or capacity < 0:
         raise ValueError("Pojemność musi być nieujemną liczbą całkowitą dla tej implementacji DP.")
    for item in items:
         if not isinstance(item['weight'], int) or item['weight'] < 0:
              raise ValueError(f"Waga przedmiotu {item['id']} musi być nieujemną liczbą całkowitą.")

    # Inicjalizacja tabeli DP wymiarów (n+1) x (capacity+1) zerami
    # dp[i][w] przechowuje max wartość dla pierwszych 'i' przedmiotów przy pojemności 'w'
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Wypełnianie tabeli DP
    for i in range(1, n + 1):  # Iteracja po przedmiotach (od 1 do n)
        # Pobieramy dane i-tego przedmiotu (indeks i-1 w liście 'items')
        current_item = items[i-1]
        weight = current_item['weight']
        value = current_item['value']

        for w in range(capacity + 1):  # Iteracja po pojemnościach (od 0 do capacity)
            if weight > w:
                # Przedmiot i-ty jest za ciężki, nie mieści się
                dp[i][w] = dp[i-1][w]
            else:
                # Przedmiot i-ty mieści się, wybieramy lepszą opcję:
                # 1. Nie brać i-tego przedmiotu
                # 2. Wziąć i-ty przedmiot
                dp[i][w] = max(dp[i-1][w], value + dp[i-1][w - weight])

    # Maksymalna wartość znajduje się w ostatniej komórce tabeli
    max_value = dp[n][capacity]

    # Odtworzenie wybranych przedmiotów (backtracking)
    selected_items = []
    total_weight = 0
    w = capacity # Zaczynamy od pełnej pojemności
    for i in range(n, 0, -1): # Idziemy od ostatniego przedmiotu do pierwszego
        # Sprawdzamy, czy wartość dp[i][w] pochodzi z uwzględnienia i-tego przedmiotu
        # Jeśli dp[i][w] jest RÓŻNE od dp[i-1][w], to znaczy, że i-ty przedmiot został wzięty
        # Musimy też upewnić się, że w ogóle jest jakaś wartość (większa od 0)
        if dp[i][w] > dp[i-1][w]:
            item = items[i-1]
            selected_items.append(item)
            total_weight += item['weight']
            w -= item['weight'] # Zmniejszamy dostępną pojemność o wagę wziętego przedmiotu

        # Jeśli w spadnie do 0, nie możemy wziąć więcej przedmiotów
        if w == 0:
            break

    # Odwracamy listę, bo dodawaliśmy przedmioty od końca
    selected_items.reverse()

    return max_value, total_weight, selected_items


# Blok testowy
if __name__ == "__main__":
    # Dane z naszej ręcznej analizy
    example_items = [
        {'id': 'A', 'value': 60, 'weight': 5},
        {'id': 'B', 'value': 50, 'weight': 3},
        {'id': 'C', 'value': 70, 'weight': 4},
        {'id': 'D', 'value': 30, 'weight': 2},
    ]
    max_capacity = 10 # Musi być int

    print("--- Test Algorytmu Programowania Dynamicznego ---")
    print(f"Przedmioty: {example_items}")
    print(f"Pojemność plecaka: {max_capacity}\n")

    try:
        dp_value, dp_weight, dp_items = dynamic_programming_knapsack(example_items, max_capacity)

        print(f"Programowanie Dynamiczne:")
        selected_ids = sorted([item['id'] for item in dp_items])
        print(f"  Wybrane przedmioty: {selected_ids}")
        print(f"  Optymalna wartość: {dp_value}")
        print(f"  Waga przy optymalnej wartości: {dp_weight}\n")

        # Porównanie z Brute Force i Zachłannymi
        from algorithms.brute_force import brute_force_knapsack
        from algorithms.greedy import greedy_knapsack_by_value, greedy_knapsack_by_weight, greedy_knapsack_by_density

        bf_value, _, _ = brute_force_knapsack(example_items, max_capacity)
        val_value, _, _ = greedy_knapsack_by_value(example_items, max_capacity)
        wei_value, _, _ = greedy_knapsack_by_weight(example_items, max_capacity)
        den_value, _, _ = greedy_knapsack_by_density(example_items, max_capacity)

        print("--- Porównanie Wyników ---")
        print(f"  Zachłanny (Wartość): {val_value}")
        print(f"  Zachłanny (Waga):    {wei_value}")
        print(f"  Zachłanny (Gęstość): {den_value}")
        print(f"  Brute Force (Opt.):  {bf_value}")
        print(f"  Dynamiczne (Opt.):   {dp_value}")

    except ValueError as e:
        print(f"Błąd: {e}")
    except ImportError:
         print("Nie można zaimportować innych algorytmów. Uruchom testy z głównego folderu projektu.")