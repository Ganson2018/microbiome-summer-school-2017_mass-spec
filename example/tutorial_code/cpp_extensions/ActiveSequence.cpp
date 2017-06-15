//
// Created by Mario Marchand on 17-06-12.
//

//#define VLM

#include "ActiveSequence.h"

using namespace std;

ActiveSequence::ActiveSequence(size_t p_nbOfSpectra, double p_window_size)
    : window_size(p_window_size), nbOfSpectra(p_nbOfSpectra), mz_avg(0), mz_lb(-50)
{
    spectraPresent.resize(nbOfSpectra);
    for (int i=0; i<nbOfSpectra; ++i)
    {
        spectraPresent[i] = false;
    }
}

bool ActiveSequence::empty() const
{
    return theList.empty();
}

double ActiveSequence::getAverageMz() const
{
    return mz_avg;
}

//precondition: peaks in theList must all be from different spectra
bool ActiveSequence::isValid(const Heap & heap) const
{
#ifdef VLM
    if (theList.size() != nbOfSpectra) return false;
#endif
    if(this->empty()) return false;
    if(!heap.empty())
    {
        if( get<2>(heap.top()) <= mz_avg*(1.0 + window_size) ) return false;
    }
    if(get<2>(theList.back()) > mz_avg*(1.0 + window_size)) return false;
    if(get<2>(theList.front()) < mz_avg*(1.0 - window_size)) return false;
    if( mz_lb >=  mz_avg*(1.0 - window_size) ) return false;
    return true;
}

void ActiveSequence::advanceLowerBound()
{
    if(this->empty()) throw logic_error("ActiveSequence::advanceLowerBound(): ActiveSequence must be non empty");

    size_t old_size = theList.size();
    tuple<size_t,size_t,double> t = theList.front();
    theList.pop_front();

    if (get<0>(t) >= nbOfSpectra) throw logic_error("ActiveSequence::advanceLowerBound(): get<0>(t] >= nbOfSpectra");
    if(spectraPresent[get<0>(t)] == false) throw logic_error("ActiveSequence::advanceLowerBound(): that spectrum should be present");
    spectraPresent[get<0>(t)] = false;

    mz_lb = get<2>(t);

    size_t new_size = theList.size();
    if (new_size==0)
    {
        mz_avg = 0;
    }
    else
    {
        mz_avg = ((double)old_size*mz_avg - mz_lb) / (double)new_size;
    }
}

bool ActiveSequence::insert(Heap &heap, const vector<vector<double> > & peak)
{
    if(heap.empty()) return false; //cannot insert one more since no more peak exists

    if(theList.empty())
    {
        tuple<size_t,size_t,double> t = heap.popAndFeed(peak);
        if (get<0>(t) >= nbOfSpectra) throw logic_error("ActiveSequence::insert(): get<0>(t] >= nbOfSpectra");

        if(spectraPresent[get<0>(t)]) throw logic_error("ActiveSequence::insert(): this spectra should be absent");
        spectraPresent[get<0>(t)] = true;
        theList.push_back(t);
        mz_avg = get<2>(t);
        return true;
    }
    else
    {
        tuple<size_t,size_t,double> t = heap.top();
        if (get<0>(t) >= nbOfSpectra) throw logic_error("ActiveSequence::insert(): get<0>(t] >= nbOfSpectra");

        size_t spectra_indx = get<0>(t);
        double mz = get<2>(t);
        if(spectraPresent[spectra_indx]) return false; //since this new peak is from a spectra already present
        size_t old_size = theList.size();
        double new_mz_avg = (old_size*mz_avg + mz) / (double)(old_size + 1);

        if (mz <= new_mz_avg * (1 + window_size))
        {
            if (get<2>(theList.front()) >= new_mz_avg * (1 - window_size))
            {
                //you can add this peak while the first peak in the sequence remain in the window
                spectraPresent[spectra_indx] = true;
                mz_avg = new_mz_avg;
                theList.push_back(heap.popAndFeed(peak));
                return true;
            }
        }
        return false; //since the peak is not added into the sequence
    }

}

std::ostream & operator<<(std::ostream & flux, const ActiveSequence & as)
{
    flux << "Active sequence with mz_avg = "  << as.mz_avg << " : " << endl;
    for(auto itr = as.theList.begin(); itr!= as.theList.end(); ++itr)
    {
        flux << "(" << get<0>(*itr) << ", " << get<1>(*itr) << ", " << get<2>(*itr) << ")" << endl;
    }
    flux << endl;
    return flux;
}

