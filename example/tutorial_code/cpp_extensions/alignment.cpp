#include <fstream>
#include <iostream>
#include <sstream>

#include <vector>
#include <string>

#include "Heap.h"
#include "ActiveSequence.h"

//#define VERBOSE

using namespace std;

vector<string> string_to_vector(const string &s, char delim)
{
    stringstream ss(s);
    string item;
    vector<string> elems;
    while (getline(ss, item, delim))
    {
        elems.push_back(item);
    }
    return elems;
}


vector<double> removeOverlaps(const vector<double> &tentativeAlignmentPoint, double window_size)
{
    vector<double> alignmentPoint;

    size_t n = tentativeAlignmentPoint.size();
    vector<bool> isOverlapping(n, false);

    if (n == 0) return alignmentPoint;

    for (size_t i = 0; i < (n - 1); ++i)
    {
        if ((1.0 + window_size) * tentativeAlignmentPoint.at(i) >=
            (1.0 - window_size) * tentativeAlignmentPoint.at(i + 1))
        {
            isOverlapping[i] = true;
            isOverlapping[i + 1] = true;
        }
    }
    for (size_t i = 0; i < n; ++i)
    {
        if (!isOverlapping.at(i))
        {
            alignmentPoint.push_back(tentativeAlignmentPoint[i]);
        }

    }
    return alignmentPoint;
}

vector<double> alignmentPointDetection(const vector<vector<double> > &peak, double window_size)
{
    vector<double> tentativeAlignmentPoint; //aligment points that may overlap; initially empty

    size_t nbOfSpectra = peak.size();

    Heap heap(peak); //each spectra has its first peak in the min heap h
    ActiveSequence as(nbOfSpectra, window_size); //initially empty (contains zero peaks)

#ifdef VERBOSE
    cout << "nbOfSpectra = " << nbOfSpectra << " window size = " << window_size << endl;
#endif
    bool found = false;

    while (!heap.empty())
    {
        if (as.isValid(heap)) found = true;

        if (as.insert(heap, peak) == false) //was not able to insert next peak in as
        {
            if (found)
            {
                tentativeAlignmentPoint.push_back(as.getAverageMz());
                found = false;
#ifdef VERBOSE
                cout << "Alignment point found! with average mz = " << as.getAverageMz() << endl;
                cout << as;
#endif
            }
            as.advanceLowerBound();
        } else //the insertion in as has succeeded
        {
#ifdef VERBOSE
            cout << as;
#endif
            if (heap.empty()) //if there are no more peak to insert you are done
            {
                while (!as.empty())
                {
                    if (as.isValid(heap))
                    {
                        tentativeAlignmentPoint.push_back(as.getAverageMz());
#ifdef VERBOSE
                        cout << "Alignment point found while heap empty! with average mz = " << as.getAverageMz() << endl;
                        cout << as;
#endif
                        break;
                    }
                    as.advanceLowerBound();
                }
            }
        }
    }
#ifdef VERBOSE
    cout << "Tentative alignment points: " ;
    for (const auto & v : tentativeAlignmentPoint)
    {
        cout << v << " ";
    }
    cout << endl;
#endif

    vector<double> alignmentPoint = removeOverlaps(tentativeAlignmentPoint, window_size);

    return alignmentPoint;
}

/**
int main()
{
    const unsigned int bufferSize = 2000000;
    char buffer[bufferSize];

//    vector<vector<double> > peak{{1, 2.1, 3, 7}, {1, 3, 4, 6.9}, {2, 3, 7.1}}; //toy example for testing

    vector<vector<double> > peak; //contains the mz values for all peaks in the set of spectra

    string output_file_name("alignmentPoints.txt");
    ofstream output_file(output_file_name);

    string input_file_name;
    cout << "Enter name of file containing the spectra: ";
    cin >> input_file_name;
    double window_size;
    cout << "Enter window size in relative units: ";
    cin >> window_size;
    cout << "In progress ..." << endl;

    ifstream input_file(input_file_name);
    if (!input_file.is_open())
        logic_error("main(): Cannot open file containing spectra");
    if (!input_file.good())
        logic_error("main(): File containing spectra must be open");

    size_t cpt = 0;
    while (input_file.good())
    {
        input_file.getline(buffer, bufferSize);
        string input_line(buffer);
        if (input_line.size() > 0) //skip blank lines
        {
            vector<string> v = string_to_vector(input_line, ',');
            vector<double> aSpectra;
            for (string mz_string : v)
            {
                aSpectra.push_back(atof(mz_string.c_str()));
            }
            peak.push_back(aSpectra);
            cout << peak[cpt].size() << endl;
            cpt++;
        }
    }

    vector<double> alignmentPoint = alignmentPointDetection(peak, window_size);
#ifdef VERBOSE
    cout << "alignment points: " ;
#endif
    for (const auto &v : alignmentPoint)
#    {
        output_file << v << " ";
    }
    output_file << endl;
    cout << "Writing to file " << output_file_name << endl;

    return 0;
}
**/
