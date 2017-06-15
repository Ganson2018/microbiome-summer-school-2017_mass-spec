//
// Created by Mario Marchand on 17-06-12.
//
#include <vector>

#include "gtest/gtest.h"
#include "../Heap.h"

using namespace std;

TEST(heap, can_instantiate_heap)
{
    vector<vector<double> > peak{{1, 2, 3}, {1, 3, 4}, {2, 3}};
    Heap h(peak);

    EXPECT_EQ(get<0>(h.top()), 0);
    EXPECT_EQ(get<1>(h.top()), 0);
    EXPECT_EQ(get<2>(h.top()), 1);

//    tuple<size_t,size_t,double> p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);
//    cout << "vector extracted: " << get<0>(p) << " " << get<1>(p) << " " << get<2>(p) << endl;
//    p = h.popAndFeed(peak);

}

