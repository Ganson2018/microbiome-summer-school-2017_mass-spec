//
// Created by Mario Marchand on 17-06-12.
//

#ifndef MASSSPECTRAALIGN_ACTIVESEQUENCE_H
#define MASSSPECTRAALIGN_ACTIVESEQUENCE_H

#include <list>
#include <vector>

#include "Heap.h"

class ActiveSequence
{
public:
    ActiveSequence(size_t nbOfSpectra, double p_window_size);
    bool isValid(const Heap &) const;
    bool empty() const;
    void advanceLowerBound();
    bool insert(Heap & heap, const std::vector<std::vector<double> > & peak);
    double getAverageMz() const;
    friend std::ostream & operator<<(std::ostream & flux, const ActiveSequence & as);

private:
    std::list<std::tuple<size_t,size_t,double> > theList;
    std::vector<bool> spectraPresent;
    double window_size;
    size_t nbOfSpectra;
    double mz_avg;
    double mz_lb;


};


#endif //MASSSPECTRAALIGN_ACTIVESEQUENCE_H
