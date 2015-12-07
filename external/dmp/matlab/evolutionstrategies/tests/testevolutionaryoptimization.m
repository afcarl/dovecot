function [update_summaries_history cost_vars_history] = testevolutionaryoptimization(use_simplified_version)
if (nargin==0), use_simplified_version=false; end

% Dimensionality of the task
n_dims = 2;

% Get the task
target = 1:n_dims;
task = TaskQuadraticFunction(target);

% Get the solver for the task
task_solver = TaskSolverIdentity();

% Initial parameter distribution
mu = 5*ones(1,n_dims);
covar = 4*eye(n_dims);
distribution = DistributionGaussian(mu,covar);

updater = UpdaterPIBB;

n_samples_per_update = 10;
n_updates = 20;
if (use_simplified_version)
  [update_summaries_history cost_vars_history] = runEvolutionaryOptimizationSimplified(task, task_solver, distribution, n_samples_per_update, updater, n_updates);
else
  [update_summaries_history cost_vars_history] = runEvolutionaryOptimization(task, task_solver, distribution, n_samples_per_update, updater, n_updates);
end
end