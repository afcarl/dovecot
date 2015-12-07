#include "dmp_bbo/TaskViapoint.h"

#include "dmp/Trajectory.h"

#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>

#include <eigen3/Eigen/Core>

using namespace std;
using namespace Eigen;

int main(int n_args, char* args[])
{
  string directory;
  if (n_args>1)
    directory = string(args[1]);
  
  int n_dims = 1;

  VectorXd viapoint = VectorXd::Constant(n_dims,0.5);
  double viapoint_time = 0.5;
  TaskViapoint task = TaskViapoint(viapoint, viapoint_time);
  
  MatrixXd task_parameters = MatrixXd(1,n_dims);

  int n_time_steps = 51;
  VectorXd ts = VectorXd::LinSpaced(n_time_steps,0,1);
  
    
  int n_demos = 9;
  VectorXd task_parameter_values = VectorXd::LinSpaced(n_demos,-0.4,1.4);
  
  
  Trajectory demonstration;
  for (int i_demo=0; i_demo<n_demos; i_demo++)
  {
    task_parameters.fill(task_parameter_values[i_demo]);
    task.generateDemonstration(task_parameters, ts, demonstration);
  
    cout <<  fixed << setw(1) << setprecision(3);
    if (directory.empty())
    {
      cout << "______________________" << endl;
      cout << task_parameters << endl<< endl;
      cout << demonstration << endl;
    } 
    else
    {
      stringstream stream;
      stream << directory << "/demonstration" << setw(2) << setfill('0') << i_demo << ".txt";
      string filename = stream.str();
 
      cout << "Saving to " << filename << endl;

      std::ofstream outfile;
      outfile.open(filename.c_str()); 
      outfile << demonstration;
      outfile.close();
      
      stringstream stream2;
      stream2 << directory << "/task_parameters" << setw(2) << setfill('0') << i_demo << ".txt";
      filename = stream2.str();
      
      cout << "Saving to " << filename << endl;
      
      outfile.open(filename.c_str()); 
      outfile << task_parameters;
      outfile.close();

      stringstream stream3;
      stream3 << directory << "/viapoint_time" << setw(2) << setfill('0') << i_demo << ".txt";
      filename = stream3.str();
      
      cout << "Saving to " << filename << endl;
      
      outfile.open(filename.c_str()); 
      outfile << viapoint_time;
      outfile.close();
      
    }
  }

  if (!directory.empty())
  {
    cout << endl << "Plot results in Matlab as follows:" << endl << endl;
    cout << "clf; for dd=0:"<<n_demos-1<<", data = load(sprintf('"<<directory<<"demonstration%02d.txt',dd)); tp = load(sprintf('"<<directory<<"task_parameters%02d.txt',dd)); viapoint_time = load(sprintf('"<<directory<<"viapoint_time%02d.txt',dd)); for ss=1:3, subplot(1,3,ss); plot(data(:,1),data(:,ss+1)'); hold on; if (ss==1), plot(viapoint_time,tp,'ro'); end; axis square; axis tight; end; end" << endl;
  }
  
  
}
