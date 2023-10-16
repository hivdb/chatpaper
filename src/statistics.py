from scipy import stats


def chi_square():
    pass


def calc_contigency_table(listA, listB):

    match_list = list(zip(listA, listB))

    both = [
        1
        for i, j in match_list
        if i and j
    ]

    i_only = [
        1
        for i, j in match_list
        if i and not j
    ]

    j_only = [
        1
        for i, j in match_list
        if not i and j
    ]

    none = [
        1
        for i, j in match_list
        if not i and not j
    ]

    return {
        'both': len(both),
        'i_only': len(i_only),
        'j_only': len(j_only),
        'none': len(none),
        'total': len(match_list)
    }


def calc_spearman(listA, listB):
    sp = stats.spearmanr(listA, listB)

    return {
        'spearman_rho': round(sp.statistic, 3),
        'spearman_p_value': sp.pvalue,
    }
