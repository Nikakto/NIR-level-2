import random

NUM = 59


def field_operation(field, fun):

    table = {}
    for term in field:
        table[term] = fun(term, field)

    return table


def field_operation_full(field, fun):

    table = {}
    for term in field:
        table[term] = {}

        for other_term in field:
            table[term][other_term] = fun(term, other_term, field)

    return table


def field_inv(a, field=None):
    # a * field_inv(a) = 1

    for factor in field:
        if field_mul(a, factor, field) == 1:
            return factor

    return None


def field_mul(a, b, field):
    # a * b = c
    return (a * b) % len(field)


def field_opp(a, field=None):
    # a + field_opp(a) = 0
    if a == 0:
        return 0
    else:
        return len(field) - a


def field_sum(a, b, field):
    # a * b = c
    return (a + b) % len(field)


def print_all(table, operation='+'):
    for term in table.keys():
        for other_term in table.keys():
            print(f'{term:3d} {operation} {other_term:3d} = {table[term][other_term]:3d}; ', end='')
        print()


def print_results(field, opp, inv):

    print(' '*4, end='')
    for val in field:
        print(f'{val:4d}', end='')
    print()

    print(f'{"-x":4s}', end='')
    for val in opp.values():
        print(f'{val:4d}', end='')
    print()

    print(f'{"1/x":4s}', end='')
    for val in inv.values():
        if val is None:
            print(f'   -', end='')
        else:
            print(f'{val:4d}', end='')
    print()


def random_ax_b(field):

    x = -1

    while x < 0 or int(x) != x or x not in field:
        a, b, c = random.choice(field), random.choice(field), random.choice(field)
        for _x in field:
            if field_sum(field_mul(a, _x, field), b, field) == c:
                x = _x

    print(f'{a}*x + {b} = {c}')
    print(f'x = {x};')


def random_ax2_bx_c(field):

    roots = []
    while len(roots) < 2:

        roots = []
        a, b, c, d = random.choice(field), random.choice(field), random.choice(field), random.choice(field)
        for _x in field:

            _x2 = field_mul(_x, _x, field)
            p1 = field_mul(a, _x2, field)
            p2 = field_mul(b, _x, field)
            p1_p2 = field_sum(p1, p2, field)

            if field_sum(p1_p2, c, field) == d:
                roots.append(_x)

    print(f'{a}*x^2 + {b}*x + {c} = {d}')
    for i, root in enumerate(roots):
        print(f'x{i} = {root};')


def random_ax3_bx2_cx_d(field):

    roots = []
    while len(roots) < 3:

        roots = []
        a, b, c, d, e = random.choice(field), random.choice(field), random.choice(field), random.choice(field), random.choice(field)
        for _x in field:

            _x2 = field_mul(_x, _x, field)
            _x3 = field_mul(_x2, _x, field)

            p1 = field_mul(a, _x3, field)
            p2 = field_mul(b, _x2, field)
            p3 = field_mul(c, _x, field)

            p1_p2 = field_sum(p1, p2, field)
            p1_p2_p3 = field_sum(p1_p2, p3, field)

            if field_sum(p1_p2_p3, d, field) == e:
                roots.append(_x)

    print(f'{a}*x^3 + {b}*x^2 + {c}*x + {d} = {e}')
    for i, root in enumerate(roots):
        print(f'x{i} = {root};')


def random_sys_2(field):

    a2, b2, c2 = random.choice(field), random.choice(field), random.choice(field)

    roots = []
    while not roots:
        roots = []
        x = -1

        a1, b1, c1 = random.choice(field), random.choice(field), random.choice(field)
        for _x in field:
            if field_sum(field_mul(a1, _x, field), b1, field) == c1:
                x = _x

        if x < 0:
            continue

        a2, b2, c2 = random.choice(field), random.choice(field), random.choice(field)
        if field_sum(field_mul(a2, x, field), b2, field) == c2:
            roots.append(x)

    print(f'{a1}*x + {b1} = {c1}')
    print(f'{a2}*x + {b2} = {c2}')
    for i, root in enumerate(roots):
        print(f'x{i} = {root};')


def random_sys_3(field):

    a2, b2, c2 = random.choice(field), random.choice(field), random.choice(field)

    roots = []
    while not roots:
        roots = []

        a1, b1, c1, d1 = random.choice(field), random.choice(field), random.choice(field), random.choice(field)
        for _x in field:

            _x2 = field_mul(_x, _x, field)
            p1 = field_mul(a1, _x2, field)
            p2 = field_mul(b1, _x, field)
            p1_p2 = field_sum(p1, p2, field)

            if field_sum(p1_p2, c1, field) == d1:
                roots.append(_x)

        _roots = []
        for _x in roots:
            a2, b2, c2, d2 = random.choice(field), random.choice(field), random.choice(field), random.choice(field)
            _x2 = field_mul(_x, _x, field)
            p1 = field_mul(a2, _x2, field)
            p2 = field_mul(b2, _x, field)
            p1_p2 = field_sum(p1, p2, field)

            if field_sum(p1_p2, c2, field) == d2:
                _roots.append(_x)
        roots = _roots

        _roots = []
        for _x in roots:
            a3, b3, c3, d3 = random.choice(field), random.choice(field), random.choice(field), random.choice(field)
            _x2 = field_mul(_x, _x, field)
            p1 = field_mul(a3, _x2, field)
            p2 = field_mul(b3, _x, field)
            p1_p2 = field_sum(p1, p2, field)

            if field_sum(p1_p2, c3, field) == d3:
                _roots.append(_x)
        roots = _roots

    print(f'{a1}*x^2 + {b1}*x + {c1} = {d1}')
    print(f'{a2}*x^2 + {b2}*x + {c2} = {d2}')
    print(f'{a3}*x^2 + {b3}*x + {c3} = {d3}')
    for i, root in enumerate(roots):
        print(f'x{i} = {root};')


if __name__ == '__main__':

    field = [i for i in range(59)]

    sums = field_operation_full(field, field_sum)
    muls = field_operation_full(field, field_mul)

    opp = field_operation(field, field_opp)
    inv = field_operation(field, field_inv)

    print('\n\n=== All sums in field ===')
    print_all(sums)

    print('\n\n=== All muls in field ===')
    print_all(muls)

    print('\n\n=== opposites and inversions ===')
    print_results(field, opp, inv)

    print('\n')
    random_ax_b(field)

    print('\n')
    random_ax2_bx_c(field)

    print('\n')
    random_ax3_bx2_cx_d(field)

    print('\n')
    random_sys_2(field)

    print('\n')
    random_sys_3(field)

    print('Done')