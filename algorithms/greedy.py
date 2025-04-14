# algorithms/greedy.py

def greedy_knapsack_by_value(items, capacity):
    """
    Rozwiązuje problem plecakowy 0/1 za pomocą algorytmu zachłannego
    sortującego przedmioty według WARTOŚCI (malejąco).

    Args:
        items (list): Lista słowników, gdzie każdy słownik reprezentuje przedmiot
                      i musi zawierać klucze 'id', 'value' i 'weight'.
                      Np. [{'id': 'A', 'value': 60, 'weight': 5}, ...]
        capacity (int or float): Maksymalna pojemność plecaka.

    Returns:
        tuple: Krotka zawierająca:
            - total_value (int or float): Łączna wartość przedmiotów w plecaku.
            - total_weight (int or float): Łączna waga przedmiotów w plecaku.
            - selected_items (list): Lista słowników przedmiotów wybranych do plecaka.
    """
    # Sortuj przedmioty według wartości malejąco
    # Używamy kopii listy, aby nie modyfikować oryginalnej listy przedmiotów
    sorted_items = sorted(items, key=lambda item: item['value'], reverse=True)

    knapsack = []
    current_weight = 0
    total_value = 0

    for item in sorted_items:
        # Sprawdź, czy przedmiot zmieści się w pozostałej pojemności
        if current_weight + item['weight'] <= capacity:
            knapsack.append(item)
            current_weight += item['weight']
            total_value += item['value']

    return total_value, current_weight, knapsack

def greedy_knapsack_by_weight(items, capacity):
    """
    Rozwiązuje problem plecakowy 0/1 za pomocą algorytmu zachłannego
    sortującego przedmioty według WAGI (rosnąco).

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
        capacity (int or float): Maksymalna pojemność plecaka.

    Returns:
        tuple: (total_value, total_weight, selected_items)
    """
    # Sortuj przedmioty według wagi rosnąco
    sorted_items = sorted(items, key=lambda item: item['weight'])

    knapsack = []
    current_weight = 0
    total_value = 0

    for item in sorted_items:
        if current_weight + item['weight'] <= capacity:
            knapsack.append(item)
            current_weight += item['weight']
            total_value += item['value']

    return total_value, current_weight, knapsack

def greedy_knapsack_by_density(items, capacity):
    """
    Rozwiązuje problem plecakowy 0/1 za pomocą algorytmu zachłannego
    sortującego przedmioty według STOSUNKU WARTOŚĆ/WAGA (malejąco).

    Args:
        items (list): Lista słowników przedmiotów ('id', 'value', 'weight').
        capacity (int or float): Maksymalna pojemność plecaka.

    Returns:
        tuple: (total_value, total_weight, selected_items)
    """
    # Oblicz stosunek wartość/waga dla każdego przedmiotu
    # Dodaj obsługę przypadku, gdy waga = 0 (choć w typowym problemie plecakowym wagi są > 0)
    items_with_density = []
    for item in items:
        if item['weight'] > 0:
            density = item['value'] / item['weight']
        elif item['value'] > 0: # Waga 0, ale wartość dodatnia - nieskończona gęstość
             density = float('inf')
        else: # Waga 0 i wartość 0 - gęstość 0
            density = 0
        # Tworzymy nową listę, aby nie modyfikować oryginalnych słowników
        items_with_density.append({**item, 'density': density})


    # Sortuj przedmioty według gęstości malejąco
    sorted_items = sorted(items_with_density, key=lambda item: item['density'], reverse=True)

    knapsack = []
    current_weight = 0
    total_value = 0

    for item in sorted_items:
        # Sprawdź, czy przedmiot zmieści się w pozostałej pojemności
        if current_weight + item['weight'] <= capacity:
            knapsack.append(item) # Dodajemy oryginalny słownik bez 'density' dla spójności
            current_weight += item['weight']
            total_value += item['value']

    # Usuń klucz 'density' z wybranych przedmiotów, jeśli został dodany (choć powyżej już tego nie robimy)
    # Czystrza wersja zwraca listę oryginalnych słowników, a nie tych z dodaną gęstością.
    # Dlatego knapsack.append(item) powyżej dodaje item z listy sorted_items, która *ma* density.
    # Poprawmy to:
    final_knapsack = []
    current_weight = 0
    total_value = 0
    for item in sorted_items:
        # Znajdź oryginalny item po id, aby uniknąć zwracania 'density'
        original_item = next(i for i in items if i['id'] == item['id'])
        if current_weight + original_item['weight'] <= capacity:
            final_knapsack.append(original_item)
            current_weight += original_item['weight']
            total_value += original_item['value']


    return total_value, current_weight, final_knapsack # Zwracamy final_knapsack

# Możemy dodać prosty test na dole pliku, aby sprawdzić, czy funkcje działają
if __name__ == "__main__":
    # Dane z naszej ręcznej analizy
    example_items = [
        {'id': 'A', 'value': 60, 'weight': 5},
        {'id': 'B', 'value': 50, 'weight': 3},
        {'id': 'C', 'value': 70, 'weight': 4},
        {'id': 'D', 'value': 30, 'weight': 2},
    ]
    max_capacity = 10

    print("--- Test Algorytmów Zachłannych ---")
    print(f"Przedmioty: {example_items}")
    print(f"Pojemność plecaka: {max_capacity}\n")

    val_value, val_weight, val_items = greedy_knapsack_by_value(example_items, max_capacity)
    print(f"Zachłanny wg Wartości:")
    print(f"  Wybrane przedmioty: {[item['id'] for item in val_items]}")
    print(f"  Łączna wartość: {val_value}")
    print(f"  Łączna waga: {val_weight}\n")

    wei_value, wei_weight, wei_items = greedy_knapsack_by_weight(example_items, max_capacity)
    print(f"Zachłanny wg Wagi:")
    print(f"  Wybrane przedmioty: {[item['id'] for item in wei_items]}")
    print(f"  Łączna wartość: {wei_value}")
    print(f"  Łączna waga: {wei_weight}\n")

    den_value, den_weight, den_items = greedy_knapsack_by_density(example_items, max_capacity)
    print(f"Zachłanny wg Gęstości (wartość/waga):")
    print(f"  Wybrane przedmioty: {[item['id'] for item in den_items]}")
    print(f"  Łączna wartość: {den_value}")
    print(f"  Łączna waga: {den_weight}\n")