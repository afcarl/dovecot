#include "utilities/EigenJSON.hpp"

#include <iostream>
#include <iomanip>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;


int main()
{
  vector<MatrixXd> matrices(3);
  matrices[0] = 10*MatrixXd::Random(4,3); 
  matrices[1] = 10*VectorXd::Random(5); 
  matrices[2] = 10*RowVectorXd::Random(5); 
  
  for (int ii=0; ii<3; ii++)
  {
    MatrixXd m =  matrices[ii];
    string m_string = serializeJSON(m);
    MatrixXd m_deser;
    deserializeMatrixJSON(m_string,m_deser);
    
    MatrixXi m_deser_i;
    deserializeMatrixJSON(m_string,m_deser_i);
    
    cout << "______________________" << endl;
    cout << "Initial matrix: " << endl << m << endl;
    cout << "Serialized as string: " << endl << m_string << endl;
    cout << "Deserialized matrix" << endl << m_deser << endl;
    cout << "Deserialized matrix (int)" << endl << m_deser_i << endl;
      
  }

}
