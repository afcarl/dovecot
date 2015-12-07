#ifndef RUNEVOLUTIONARYOPTIMIZATIONPARALLEL_H
#define RUNEVOLUTIONARYOPTIMIZATIONPARALLEL_H

// Forward declarations
class Task;
class TaskSolverParallel;
class DistributionGaussian;
class Updater;

#include <string>
#include <vector>

void runEvolutionaryOptimizationParallel(Task* task, TaskSolverParallel* task_solver, std::vector<DistributionGaussian*> distributions, Updater* updater, int n_updates, int n_samples_per_update, std::string save_directory=std::string(""),bool overwrite=false);

#endif

/** \defgroup DMP_BBO Black Box Optimization of Dynamical Movement Primitives Module
 */

/** \page page_dmp_bbo Black Box Optimization of Dynamical Movement Primitives

 */
 
 
