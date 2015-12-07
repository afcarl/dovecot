function [update_summaries_history cost_vars_history] = runEvolutionaryOptimization(task, task_solver, distributions, n_samples_per_update, updater, n_updates)
if (nargin<6), n_updates = 25; end 

%-------------------------------------------------------------------------------
% Optimization loop
for i_update=1:n_updates
  fprintf('Update: %d\n',i_update);

  % 1. Sample from distributions
  for pp=1:length(distributions)
    samples{pp} = distributions(pp).generateSamples(n_samples_per_update);
  end

  % 2. Perform rollouts for the samples
  cost_vars = task_solver.performRollouts(samples);

  % 3. Evaluate the last batch of rollouts
  costs = task.costFunction(cost_vars);

  % 4. Update parameters
  for pp=1:length(distributions)
    [ distributions(pp) summaries(pp) ] = updater.updateDistribution(distributions(pp),samples{pp},costs);
  end

  % Bookkeeping and plotting
  update_summaries_history(i_update,:) = summaries;
  cost_vars_history{i_update} = cost_vars;
  plot_n_most_recent_updates = 10;
  plotlearninghistory(update_summaries_history,updater,cost_vars_history,task,plot_n_most_recent_updates);

end

end