function dmp_bbo_multidim

% Make the task
viapoint = [2 3.5]';
viapoint_time = 0.3;
task = TaskViapoint(viapoint,viapoint_time);

% Some DMP parameters
tau = 1;
x_init = [1 2]';
x_attr = [3 4]';

% Initialize one LWR for each dimension
n_basis_functions = 4;
centers = linspace(0,tau,n_basis_functions);
widths  = 2*centers(2)-centers(1)*ones(size(centers));
slopes = zeros(n_basis_functions,1);
dim = length(x_init);
for dd=1:dim
  meta_parameters = MetaParametersLWR(n_basis_functions);
  model_parameters = ModelParametersLWR(centers,widths,slopes);
  function_approximators(dd) = FunctionApproximatorLWR(meta_parameters,model_parameters);
end

dmp_type = 'KULVICIUS_2012_JOINING';
dmp = constructDmp(tau, x_init, x_attr, dmp_type, function_approximators);


% Make the task solver
n_time_steps = 61;
%parameters_to_optimize = {'centers','widths','slopes'};
parameters_to_optimize = {'slopes'};
task_solver = TaskViapointSolverDmp(dmp,n_time_steps,parameters_to_optimize);

values = task_solver.dmp_.getModelParametersVectors();
for dd=1:dim
  % Make the initial distribution
  mean_init  = values{dd};
  n_parameters = length(mean_init);

  % Build the covar matrix depending on the model parameters that will be
  % optimized
  covar_init = [];
  if (~isempty(strmatch('centers',parameters_to_optimize)))
    covar_init = [covar_init; 0.0001*ones(n_parameters,1)];
  end
  if (~isempty(strmatch('widths',parameters_to_optimize)))
    covar_init = [covar_init; 0.0001*ones(n_parameters,1)];
  end
  if (~isempty(strmatch('slopes',parameters_to_optimize)))
    covar_init = [covar_init; 100*ones(n_parameters,1)];
  end
  covar_init = diag(covar_init);

  distributions(dd) = DistributionGaussian(mean_init,covar_init);
end

% Make the parameter updater
eliteness = 10;
weighting_method = 'CMA-ES';
covar_diag_only = 1;
covar_learning_rate = 1;
covar_bounds = 0.1;
updater = UpdaterPIBB(eliteness,weighting_method,covar_diag_only,covar_learning_rate,covar_bounds);

% Run the optimization
n_samples_per_update = 15;
n_updates = 30;
evolutionaryoptimizationmultidim(task, task_solver, distributions, n_samples_per_update, updater, n_updates)

end