//
// Created by Mario Marchand on 17-06-11.
//

#include "Heap.h"

using namespace std;

Heap::Heap(const vector<vector<double> > & peak)
{
    for(size_t i=0 ; i<peak.size(); ++i)
    {
        if(peak[i].size()==0) throw logic_error("Heap::Heap(): a spectrum contains no peaks");
        theVector.push_back( tuple<size_t,size_t,double>(i, 0, peak[i][0]) );
    }
    make_heap(theVector.begin(), theVector.end(), comp);

//    cout << "theVector:  " << endl;
//    for(size_t i=0 ; i<peak.size(); ++i)
//    {
//        cout << get<0>(theVector[i]) << " " << get<1>(theVector[i]) << " " << get<2>(theVector[i]) << endl;
//    }

}

bool Heap::empty() const
{
    return theVector.empty();
}
size_t Heap::size() const
{
    return theVector.size();
}


const std::tuple<size_t, size_t, double> & Heap::top() const
{
    if(theVector.empty()) throw logic_error("Heap::top(): the heap must be non empty");
    return theVector[0];
}

std::tuple<size_t, size_t, double> Heap::popAndFeed(const vector<vector<double> > & peak)
{
    if(theVector.empty()) throw logic_error("Heap::popAndFeed(): theVector must be non empty");

    tuple<size_t,size_t,double> returned_peak = theVector[0];
    size_t spectra_indx = get<0>(returned_peak);
    size_t peak_indx = get<1>(returned_peak) + 1; //must point to the next available peak from same spectra

    pop_heap(theVector.begin(), theVector.end(), comp); //swap 1st and last element and reconstruct heap without last element

    if( peak_indx < peak[spectra_indx].size() )
    {
        theVector[theVector.size() - 1] = tuple<size_t, size_t, double>(spectra_indx, peak_indx,
                                                                        peak[spectra_indx][peak_indx]);
        push_heap(theVector.begin(), theVector.end(), comp);

//        cout << "theVector:  " << endl;
//        for(size_t i=0 ; i<theVector.size(); ++i)
//        {
//            cout << get<0>(theVector[i]) << " " << get<1>(theVector[i]) << " " << get<2>(theVector[i]) << endl;
//        }

    }
    else
    {
        theVector.pop_back();
//        cout << "new size: " << theVector.size() << endl;
//        cout << "theVector:  " << endl;
//        for(size_t i=0 ; i<theVector.size(); ++i)
//        {
//            cout << get<0>(theVector[i]) << " " << get<1>(theVector[i]) << " " << get<2>(theVector[i]) << endl;
//        }

    }

    return returned_peak;
}

