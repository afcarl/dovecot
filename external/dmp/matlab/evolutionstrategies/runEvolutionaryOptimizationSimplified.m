function [update_summaries_history cost_vars_history] = runEvolutionaryOptimizationSimplified(task, task_solver, distribution, n_samples_per_update, updater, n_updates)
% Simplified version of 'evolutionaryoptimization.m' to get an initial
% understanding of the code.
%
% The two main external functions this function calls are
%    Sample from a (Gaussian) distribution
%      samples = generate_samples(distribution,n_samples);
%    Update the distribution, given the samples and their costs
%      distribution = update_distributions(distribution,samples,costs,update_parameters);
%
% Two helper functions (not essential, but handy to have) are
%    Do sanity check on the parameters for updating
%      update_parameters = check_update_parameters(update_parameters);
%    Plot the learning history so far
%      plotlearninghistory(learning_history);
%
% The above functions are completely generic, and do not depend on the problem
% to be optimized at all.
%
%
% The task-specific functions are in
%    Do a roll-out, i.e. determine the cost-relevant variables from a sample
%    (example: sample=policy parameters, cost_vars=force sensors at finger tips
%    of a robot)
%      cost_vars = task_solver.perform_rollouts(task,samples);
%
%    Compute the costs for this task, given the cost-relevant variables.
%      costs = task.cost_function(task,cost_vars);
%
% There is a very good reason for splitting the computation of the costs into
% the two functions 'perform_rollouts' and 'cost_function'. For 'standard
% optimization' of a function it is not necessary, but when working with real
% robots it is (to be explained here some day).
%
%-------------------------------------------------------------------------------

if (nargin<6), n_updates = 25; end 

%-------------------------------------------------------------------------------
% Optimization loop
for i_update=1:n_updates % Do 20 updates
  fprintf('Update: %d\n',i_update);

  % 1. Sample from distribution
  samples = distribution.generateSamples(n_samples_per_update);
  
  % 2. Perform rollouts for the samples
  cost_vars = task_solver.performRollouts(samples);
  
  % 3. Evaluate the last batch of rollouts
  costs = task.costFunction(cost_vars);

  % 4. Update parameters
  [ distribution summary ] = updater.updateDistribution(distribution,samples,costs);
  
  % Bookkeeping and plotting
  update_summaries_history(i_update,1) = summary;
  cost_vars_history{i_update} = cost_vars;
  plot_n_most_recent_updates = 10;
  plotlearninghistory(update_summaries_history,updater,cost_vars_history,task,plot_n_most_recent_updates);

end

end