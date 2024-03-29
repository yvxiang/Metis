/* Metis
 * Yandong Mao, Robert Morris, Frans Kaashoek
 * Copyright (c) 2012 Massachusetts Institute of Technology
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, subject to the conditions listed
 * in the Metis LICENSE file. These conditions include: you must preserve this
 * copyright notice, and you cannot mention the copyright holders in
 * advertising related to the Software without their permission.  The Software
 * is provided WITHOUT ANY WARRANTY, EXPRESS OR IMPLIED. This notice is a
 * summary of the Metis LICENSE file; the license in that file is legally
 * binding.
 */
#ifndef MERGESORT_HH_
#define MERGESORT_HH_

#include "bench.hh"
#include "mr-types.hh"

/** @brief: Merge @a[@afirst + @astep * i] (0 <= i < @nmya), and output to @sized_output */
template <typename C, typename F>
void mergesort_impl(C *a, size_t nmya, size_t afirst, size_t astep, F &pcmp, C &sized_output) {
    typedef typename C::iterator iterator_type;
    xarray<iterator_type> ai;
    for (size_t i = 0; i < nmya; i++) {
        if (a[afirst + i * astep].size() == 0)
            continue;
        iterator_type cur_it = a[afirst + i * astep].begin();
        ai.push_back(cur_it);
    }

    size_t sorted_pairs = 0;
    while (sorted_pairs < sized_output.size()) {
        size_t min_index = 0, cur_index;
        for (; ai[min_index] == ai[min_index].parent_end(); min_index++)
            ;
        for (cur_index = min_index; cur_index < ai.size(); cur_index++)
            if (pcmp(ai[min_index].current(), ai[cur_index].current()) > 0)
                min_index = cur_index;

        sized_output[sorted_pairs++] = *ai[min_index];
        ai[min_index]++;
        //if(ai[min_index].current() == *(ai[min_index].parent_end()))
        if (ai[min_index] == ai[min_index].parent_end())
            ai.remove(min_index);

    }

    assert(!ai.size());
}

template <typename C, typename F>
C *mergesort(xarray<C> &a, size_t astep, size_t afirst, F &pcmp) {
    size_t nmya = a.size() / astep + (afirst < (a.size() % astep));;
    //number of pairs to sort
    size_t np = 0;
    for (size_t i = 0; i < nmya; i++)
        np += a[afirst + i * astep].size();
    C *out = new C(np);
    if (np == 0)
        return out;

    mergesort_impl(a.array(), nmya, afirst, astep, pcmp, *out);
    dprintf("mergesort: afirst %zd astep %zd (collections %zd : nr-kvs %zu)\n",
 	    afirst, astep, a.size(), np);
    return out;
}

#endif
