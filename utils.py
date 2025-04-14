# utils.py

import csv
import time
import os # Potrzebne do tworzenia ścieżek niezależnych od systemu

# --- Funkcje do wczytywania danych ---

def load_items_from_csv(filepath):
    """
    Wczytuje przedmioty z pliku CSV.
    Oczekuje nagłówków: id, value, weight.
    Konwertuje 'value' na float, 'weight' na int.

    Args:
        filepath (str): Ścieżka do pliku CSV.

    Returns:
        list: Lista słowników reprezentujących przedmioty, lub None w przypadku błędu.
    """
    items = []
    if not os.path.exists(filepath):
        print(f"Błąd: Plik nie istnieje: {filepath}")
        return None

    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Sprawdź, czy nagłówki są poprawne
            required_headers = {'id', 'value', 'weight'}
            if not required_headers.issubset(reader.fieldnames):
                missing = required_headers - set(reader.fieldnames)
                raise ValueError(f"Plik CSV musi zawierać kolumny: {required_headers}. Brakujące: {missing}")

            line_num = 1 # Do śledzenia numeru wiersza dla błędów
            for row in reader:
                line_num += 1
                try:
                    # Pobierz i oczyść dane (usuń białe znaki)
                    item_id = row['id'].strip()
                    value_str = row['value'].strip()
                    weight_str = row['weight'].strip()

                    if not item_id:
                        raise ValueError("ID przedmiotu nie może być puste.")

                    # Konwersja wartości i wagi na odpowiednie typy
                    item_value = float(value_str)
                    item_weight = int(weight_str) # Ważne dla DP!

                    # Walidacja (wartości i wagi nieujemne)
                    if item_value < 0 or item_weight < 0:
                        raise ValueError("Wartość i waga nie mogą być ujemne.")

                    items.append({
                        'id': item_id,
                        'value': item_value,
                        'weight': item_weight
                    })
                except ValueError as e:
                    print(f"Ostrzeżenie [Linia {line_num}]: Pomijanie wiersza '{row}' z powodu błędu konwersji/walidacji: {e}")
                except KeyError as e:
                     print(f"Ostrzeżenie [Linia {line_num}]: Brakujący klucz {e} w wierszu: {row}")


    except FileNotFoundError:
        # Ten błąd jest już obsłużony przez os.path.exists, ale zostawiamy dla pewności
        print(f"Błąd: Nie znaleziono pliku {filepath}")
        return None
    except ValueError as e: # Błąd dotyczący nagłówków
         print(f"Błąd formatu pliku CSV: {e}")
         return None
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas wczytywania pliku CSV '{filepath}': {e}")
        return None

    if not items:
         print("Ostrzeżenie: Nie wczytano żadnych poprawnych przedmiotów z pliku.")
         # Można zwrócić pustą listę lub None, zależnie od preferencji
         return [] # Zwróćmy pustą listę

    return items

# --- Funkcje dostarczające zestawy danych ---

def get_example_items_small():
    """Zwraca mały, predefiniowany zestaw przedmiotów."""
    return [
        {'id': 'A', 'value': 60.0, 'weight': 5},
        {'id': 'B', 'value': 50.0, 'weight': 3},
        {'id': 'C', 'value': 70.0, 'weight': 4},
        {'id': 'D', 'value': 30.0, 'weight': 2},
    ]

def get_example_items_large():
    """Zwraca większy, predefiniowany zestaw przedmiotów."""
    return [
        {'id': 'zegarek', 'value': 100.0, 'weight': 1},
        {'id': 'laptop', 'value': 1500.0, 'weight': 3},
        {'id': 'ksiazka', 'value': 300.0, 'weight': 2},
        {'id': 'aparat', 'value': 800.0, 'weight': 2},
        {'id': 'telefon', 'value': 1000.0, 'weight': 1},
        {'id': 'sluchawki', 'value': 150.0, 'weight': 1},
        {'id': 'powerbank', 'value': 200.0, 'weight': 1},
        {'id': 'namiot', 'value': 500.0, 'weight': 5},
        {'id': 'spiwor', 'value': 400.0, 'weight': 3},
        {'id': 'konsola', 'value': 1200.0, 'weight': 4},
    ]

# --- Funkcja do mierzenia czasu ---

def measure_time(func, *args, **kwargs):
    """
    Mierzy czas wykonania podanej funkcji z podanymi argumentami.

    Args:
        func (callable): Funkcja, której czas wykonania ma być zmierzony.
        *args: Argumenty pozycyjne do przekazania do funkcji.
        **kwargs: Argumenty nazwane do przekazania do funkcji.

    Returns:
        tuple: Krotka zawierająca:
            - result: Wynik zwrócony przez funkcję `func`.
            - execution_time (float): Czas wykonania funkcji w sekundach.
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    return result, execution_time

# --- Blok testowy dla utils ---
if __name__ == "__main__":
    print("--- Testowanie funkcji z utils.py ---")

    # Test wczytywania małego zestawu
    print("\nTest get_example_items_small():")
    small_items = get_example_items_small()
    print(small_items)

    # Test wczytywania dużego zestawu
    print("\nTest get_example_items_large():")
    large_items = get_example_items_large()
    print(large_items)

    # Test wczytywania z pliku CSV (załóżmy, że data/example_items.csv istnieje)
    print("\nTest load_items_from_csv('data/example_items.csv'):")
    # Budujemy ścieżkę względną od pliku utils.py
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Użyj ścieżki absolutnej dla pewności
    # POPRAWIONA ŚCIEŻKA: Łączymy katalog skryptu bezpośrednio z 'data'
    csv_path_small = os.path.join(script_dir, 'data', 'example_items.csv')
    print(f"Oczekiwana ścieżka do małego CSV: {csv_path_small}") # Dodano dla debugowania
    loaded_small_items = load_items_from_csv(csv_path_small)
    if loaded_small_items:
        print(f"Wczytano {len(loaded_small_items)} przedmiotów.")
        print(loaded_small_items)
    else:
        print("Nie udało się wczytać przedmiotów z data/example_items.csv")
        # Sprawdźmy, czy plik istnieje ręcznie
        if not os.path.exists(csv_path_small):
             print(f"Potwierdzenie: Plik {csv_path_small} NIE ISTNIEJE.")
        else:
             print(f"Potwierdzenie: Plik {csv_path_small} ISTNIEJE (problem może być w uprawnieniach lub zawartości).")


    # Test wczytywania z pliku CSV (załóżmy, że data/items_large.csv istnieje)
    print("\nTest load_items_from_csv('data/items_large.csv'):")
     # POPRAWIONA ŚCIEŻKA: Łączymy katalog skryptu bezpośrednio z 'data'
    csv_path_large = os.path.join(script_dir, 'data', 'items_large.csv')
    print(f"Oczekiwana ścieżka do dużego CSV: {csv_path_large}") # Dodano dla debugowania
    loaded_large_items = load_items_from_csv(csv_path_large)
    if loaded_large_items:
        print(f"Wczytano {len(loaded_large_items)} przedmiotów.")
        print(loaded_large_items)
    else:
        print("Nie udało się wczytać przedmiotów z data/items_large.csv")
        if not os.path.exists(csv_path_large):
             print(f"Potwierdzenie: Plik {csv_path_large} NIE ISTNIEJE.")
        else:
            print(f"Potwierdzenie: Plik {csv_path_large} ISTNIEJE (problem może być w uprawnieniach lub zawartości).")

    # Test wczytywania z nieistniejącego pliku
    print("\nTest load_items_from_csv('data/non_existent_file.csv'):")
    # Dla tego testu użyjemy ścieżki względnej od katalogu projektu
    non_existent_path = os.path.join('data', 'non_existent_file.csv')
    print(f"Oczekiwana ścieżka do nieistniejącego CSV: {non_existent_path}") # Dodano dla debugowania
    non_existent = load_items_from_csv(non_existent_path) # Podajemy ścieżkę względną
    if non_existent is None:
        print("Poprawnie obsłużono błąd nieistniejącego pliku (zwrócono None).")
    elif isinstance(non_existent, list) and not non_existent:
         print("Poprawnie obsłużono błąd nieistniejącego pliku (zwrócono pustą listę).")
    else:
         print("Coś poszło nie tak z obsługą nieistniejącego pliku.")


    # Test mierzenia czasu (prosty przykład)
    print("\nTest measure_time():")
    def slow_function(n):
        time.sleep(0.1) # Symulacja pracy
        return n * n

    result, exec_time = measure_time(slow_function, 5)
    print(f"Wynik funkcji: {result}")
    print(f"Czas wykonania: {exec_time:.4f} s")