#include "dmp/Trajectory.h"

#include <iostream>
#include <fstream>
#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

int main(int n_args, char** args)
{
  VectorXd ts = VectorXd::LinSpaced(11,0,0.5  );
  VectorXd y_first(2); y_first << 0.0,1.0;
  VectorXd y_last(2);  y_last  << 0.4,0.5;
  Trajectory traj = Trajectory::generateMinJerkTrajectory(ts, y_first, y_last);

  string filename("/tmp/testTrajectory.txt");
  
  ofstream outfile;
  outfile.open(filename.c_str()); 
  outfile << traj; 
  outfile.close();
  
  Trajectory traj_reread = Trajectory::readFromFile(filename);

  cout << "__________________" << endl;
  cout << traj;
  cout << "__________________" << endl;
  cout << traj_reread;
  
  MatrixXd misc = RowVectorXd::LinSpaced(3,1,3);
  traj.set_misc(misc);
  
  filename = string("/tmp/testTrajectoryMisc.txt");
  
  outfile.open(filename.c_str()); 
  outfile << traj; 
  outfile.close();
  
  Trajectory traj_reread_misc = Trajectory::readFromFile(filename);

  cout << "__________________" << endl;
  cout << traj;
  cout << "__________________" << endl;
  cout << traj_reread_misc;

  return 0;
}







