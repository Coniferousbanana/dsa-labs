#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: TODO (обосновать в отчёте).

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    # TODO: реализовать; считать сравнения и обмены
    exchange_count = 0
    cmp_count = 0
    a = list(a)
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(n-i-1):
            cmp_count += 1
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                exchange_count += 1
                swapped = True
        if not swapped:
            break
    return a, cmp_count, exchange_count

                


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность: TODO (лучший/худший случаи)."""
    # TODO: реализовать; считать сравнения и перемещения (сдвиги)
    a = list(a)
    cmp_count = 0
    shift_count = 0
    n = len(a)
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0:
            cmp_count += 1
            if a[j] > key:
                a[j+1] = a[j]
                shift_count += 1
            else:
                break
            j -= 1
        a[j+1] = key
    return a, cmp_count, shift_count
                



def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: TODO (почему не зависит от входа?)."""
    # TODO: реализовать; считать сравнения и обмены
    a = list(a)
    exchange_count = 0
    cmp_count = 0
    n = len(a)
    for i in range(n):
        min_index = i
        for j in range(i+1, n):
            cmp_count += 1
            if a[j] < a[min_index]:
                min_index = j
        if min_index != i:
            a[i], a[min_index] = a[min_index], a[i]
            exchange_count += 1
        
    return a, cmp_count, exchange_count


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем TODO, в худшем случае TODO (обосновать
    в отчёте, объяснить роль рандомизации). rng передаётся снаружи, чтобы
    запуск был воспроизводим по seed варианта.
    """
    if rng is None:
        rng = random.Random()
    # TODO: реализовать (рекурсивно или циклом со стеком);
    # TODO: опорный элемент — a[rng.randrange(lo, hi)], не первый и не последний.
    n = len(a)
    if n < 2:
        return list(a)
    pivot = a[rng.randrange(len(a))]
    less = []
    equal = []
    greater = []
    for i in a:
        if i < pivot:
            less.append(i)
        if i == pivot:
            equal.append(i)
        if i > pivot:
            greater.append(i)
    return quick_sort(less, rng) + equal + quick_sort(greater, rng)



# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------

class Pair:
    def __init__(self, key, label):
        self.key = key
        self.label = label

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key

    def __eq__(self, other):
        return self.key == other.key

def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    # TODO: подготовить пары, прогнать все четыре сортировки, напечатать итог
    data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    pairs = [Pair(k, l) for k, l in data]

    reference = [(p.key, p.label) for p in sorted(pairs)]
    print("эталон:", reference)

    for name, fn in ALGORITHMS.items():
        result = fn(list(pairs))
        view = [(p.key, p.label) for p in result]
        # TODO: сравнить view с reference
        if view == reference:
            print(f"сортировка {name} стабильна на полученных данных")
        else:
            print(f"сортировка {name} не стабильна на полученных данных")
        # TODO: напечатать name, view и вывод: стабильна / нет

# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5

def print_slopes(results) -> None:
    """Наклон прямой в log-log координатах: t ~ n^k, печатаем k."""
    print("\nНаклоны в log-log (t ~ n^k):")
    for name, by_cls in results.items():
        for cls, points in by_cls.items():
            ns = np.array([p[0] for p in points], dtype=float)
            ts = np.array([p[1] for p in points], dtype=float)
            k = np.polyfit(np.log(ns), np.log(ts), 1)[0]
            print(f"  {name:<15} вход={cls:<13} k={k:.2f}")


def plot_results(results, path: str = "lab03_benchmarks.png") -> None:
    """Log-log графики времени от n: по одному окну на алгоритм, линии = классы входов."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, (name, by_cls) in zip(axes.flat, results.items()):
        for cls, points in by_cls.items():
            ns = [p[0] for p in points]
            ts = [p[1] for p in points]
            ax.loglog(ns, ts, marker="o", label=cls)

        # Опорные линии, привязанные к первой точке случайного входа
        ref = by_cls["случайный"]
        n0, t0 = ref[0]
        ns = np.array([p[0] for p in ref], dtype=float)
        ax.loglog(ns, t0 * (ns / n0) ** 2, "--", color="gray", label="∝ n²")
        ax.loglog(ns, t0 * (ns * np.log(ns)) / (n0 * np.log(n0)),
                  ":", color="gray", label="∝ n log n")

        ax.set_title(name)
        ax.set_xlabel("n")
        ax.set_ylabel("время, с")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"\nграфик сохранён: {path}")
    plt.show()


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    results = {}
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        results[name] = {}
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
                results[name].setdefault(cls, []).append((n, t))

    print_slopes(results)
    plot_results(results)
    # TODO: сопоставить наклоны с O(n^2) и O(n log n), объяснить расхождения
    #       (в т. ч. лучший случай вставок и поведение пузырька на упорядоченном входе);
    # TODO: включить в отчёт таблицы счётчиков сравнений/обменов.

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
