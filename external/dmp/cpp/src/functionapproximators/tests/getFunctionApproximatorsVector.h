#ifndef GETFUNCTIONAPPROXIMATORSVECTOR_H
#define GETFUNCTIONAPPROXIMATORSVECTOR_H

#include <vector>
#include <string>

class MetaParameters;
class FunctionApproximator;

MetaParameters* getMetaParametersByName(std::string name, int input_dim);
FunctionApproximator* getFunctionApproximatorByName(std::string name, int input_dim);

void getFunctionApproximatorsVector(int input_dim, std::vector<FunctionApproximator*>& function_approximators);


#endif        //  #ifndef GETFUNCTIONAPPROXIMATORSVECTOR_H

