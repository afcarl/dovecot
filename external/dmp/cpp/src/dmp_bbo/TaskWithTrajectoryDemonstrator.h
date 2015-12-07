#ifndef TASKWITHTRAJECTORYDEMONSTRATOR_H
#define TASKWITHTRAJECTORYDEMONSTRATOR_H

#include "bbo/Task.h"
#include "bbo/DistributionGaussian.h"
#include "dmp/Trajectory.h"

#include <vector>
#include <eigen3/Eigen/Core>

class TaskWithTrajectoryDemonstrator : public Task
{
public:
  virtual void generateDemonstration(const Eigen::MatrixXd& task_parameters, const Eigen::VectorXd& ts, Trajectory& demonstrations) const = 0;
  
  void generateDemonstrations(const std::vector<Eigen::MatrixXd>& task_parameters, const std::vector<Eigen::VectorXd>& ts, std::vector<Trajectory>& demonstrations) const
  {
    unsigned int n_demos = task_parameters.size();
    assert(n_demos==ts.size());
    
    demonstrations = std::vector<Trajectory>(n_demos);
    for (unsigned int i_demo=0; i_demo<n_demos; i_demo++)
    {
      generateDemonstration(task_parameters[i_demo], ts[i_demo], demonstrations[i_demo]); 
    }
    
  }
  
  void generateDemonstrations(DistributionGaussian* task_parameter_distribution, int n_demos, const Eigen::VectorXd& ts, std::vector<Trajectory>& demonstrations) const
  {
    Eigen::MatrixXd task_parameters;
    
    demonstrations = std::vector<Trajectory>(n_demos);
    for (int i_demo=0; i_demo<n_demos; i_demo++)
    {
      task_parameter_distribution->generateSamples(n_demos,task_parameters);
      generateDemonstration(task_parameters, ts, demonstrations[i_demo]); 
    }
    
  }

  /*
  Matlab code:
  void generatedemonstrationsrandom(int n_demonstrations, Matrix&task_instances)
  {
     // Generate random task parameters
     task_parameters = obj.task_parameters_distribution.getsamples(n_demonstrations);
     // Generate task instances
     generatedemonstrations(task_parameters,task_instances);
  }
    
    function task_instances = generatedemonstrationsgrid(obj,n_demonstrations)
      n_dim = obj.task_parameters_distribution.n_dims;

      % Process arguments
      if (length(n_demonstrations)==1)
         % Copy value to make array of length n_dim
        n_demonstrations = n_demonstrations*ones(1,n_dim);
      elseif (length(n_demonstrations)==n_dim)
        % Everything is fine
      else
        error('n_demonstrations should be of length 1 or n_dim') %#ok<WNTAG>
      end

      % Generate task parameters on a grid
      task_parameters = obj.task_parameters_distribution.getgridsamples(n_demonstrations);
      
      % Remove duplicate rows (might be due to redundant dimensions)
      task_parameters = unique(task_parameters,'rows');

      % Generate task instances
      task_instances = obj.generatedemonstrations(task_parameters);
   
    end
  end
  */
};
  
#endif

