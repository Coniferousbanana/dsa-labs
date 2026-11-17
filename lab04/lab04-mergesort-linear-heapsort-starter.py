#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. Сортировки
# ---------------------------------------------------------------------------

def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков."""
    res = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        # Условие <= гарантирует стабильность: при равенстве берём из left
        if key(left[i]) <= key(right[j]):
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом для ключей [0, key_max]."""
    if not a:
        return []
    
    count = [0] * (key_max + 1)
    for x in a:
        count[x] += 1
        
    for i in range(1, len(count)):
        count[i] += count[i - 1]
        
    res = [0] * len(a)
    for x in reversed(a):
        count[x] -= 1
        res[count[x]] = x
        
    return res


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые."""
    if not a:
        return []
    
    max_val = max(a)
    exp = 1
    
    while max_val // exp > 0:
        # Устойчивая сортировка по текущему разряду (цифры 0-9)
        count = [0] * 10
        for x in a:
            digit = (x // exp) % 10
            count[digit] += 1
            
        for i in range(1, 10):
            count[i] += count[i - 1]
            
        res = [0] * len(a)
        # Проход с конца для устойчивости
        for x in reversed(a):
            digit = (x // exp) % 10
            count[digit] -= 1
            res[count[digit]] = x
            
        a = res
        exp *= 10
        
    return a


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
            
        if largest == i:
            break
            
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте."""
    n = len(a)
    
    # 1. Построение max-кучи (просейка снизу вверх, O(n))
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
        
    # 2. Фаза извлечения максимумов
    for i in range(n - 1, 0, -1):
        # Меняем корень (максимум) с последним элементом кучи
        a[0], a[i] = a[i], a[0]
        # Просеиваем новый корень в уменьшенной куче размера i
        sift_down(a, 0, i)


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
# 2. Верификация
# ---------------------------------------------------------------------------

class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""

def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)

def heap_sorted(a: list[int]) -> list[int]:
    buf = list(a)
    heap_sort(buf)
    return buf

SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}

def check_sort(fn) -> None:
    boundary = [
        [], [7], [0], [5, 5, 5], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1],
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}")
        expect(res == sorted(a), f"расходится с sorted() на {a}")

def check_merge_stability() -> None:
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен")

def self_check() -> None:
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100
WIDE_KEY_MAX = 10**9

def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    almost = list(range(n))
    for _ in range(max(1, n // 100)):
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }

def bench(fn, data: list[int]) -> float:
    fn(list(data))
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                print(f"    {algo_name:>18}: t = {bench(fn, data):.6f} c")


def plot_results(results: dict) -> None:
    """Автоматическое построение log-log графика по результатам бенчмарка."""
    try:
        import matplotlib
        matplotlib.use("Agg") # Чтобы работало даже без графического интерфейса
    except ImportError:
        print("\nmatplotlib не установлен. Графики не будут построены.")
        return

    plt.figure(figsize=(10, 6))
    
    # Берем данные для самого показательного распределения: random_wide
    dist = "random_wide"
    sizes = [1000, 3000, 10000, 30000, 100000]
    
    algorithms_to_plot = ["merge_sort", "radix_sort_lsd", "heap_sort", "quick_sort", "sorted() (эталон)"]
    markers = ['o', 's', '^', 'v', 'D']
    
    for i, algo in enumerate(algorithms_to_plot):
        if algo in results[dist]:
            times = results[dist][algo]
            plt.loglog(sizes, times, marker=markers[i], label=algo.replace('_', ' ').title())

    # Добавляем опорную линию O(n log n) для наглядности
    # Берем первую точку merge_sort как базовую для масштабирования
    base_t = results[dist]["merge_sort"][0]
    base_n = sizes[0]
    ref_nlogn = [base_t * (n * np.log(n)) / (base_n * np.log(base_n)) for n in sizes]
    plt.loglog(sizes, ref_nlogn, '--', color='gray', label='∝ n log n (теория)')

    plt.xlabel('Размер массива n (log scale)')
    plt.ylabel('Время выполнения, с (log scale)')
    plt.title(f'Сравнение алгоритмов сортировки (распределение: {dist}, seed=43)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend()
    
    plt.savefig('lab04_sorts_comparison.png', dpi=150, bbox_inches='tight')
    print("\n✅ График успешно сохранен как 'lab04_sorts_comparison.png'")


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    
    # Словарь для сбора данных, чтобы потом построить график
    results_for_plot = {
        "random_wide": {"merge_sort": [], "radix_sort_lsd": [], "heap_sort": [], "quick_sort": [], "sorted() (эталон)": []}
    }

    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                
                t = bench(fn, data)
                print(f"    {algo_name:>18}: t = {t:.6f} c")
                
                # Собираем данные для графика (только для random_wide и нужных алгоритмов)
                if dist_name == "random_wide" and algo_name in results_for_plot[dist_name]:
                    results_for_plot[dist_name][algo_name].append(t)

    # Вызываем построение графика в самом конце
    plot_results(results_for_plot)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)

if __name__ == "__main__":
    main()