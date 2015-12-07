function plotlearninghistory(update_summaries_history,updater,cost_vars_history,task,plot_n_most_recent_updates)
if (nargin<2), updater=[]; end
if (nargin<3), cost_vars_history=[]; end
if (nargin<4), task=[]; end
if (nargin<5), plot_n_most_recent_updates=length(update_summaries_history); end

main_color = [0 0 0];

update_summaries = update_summaries_history;
assert(~isempty(update_summaries))

[ n_updates n_parallel ] = size(update_summaries);
assert(n_parallel>0)

n_parameters = length(update_summaries(1).distribution_new.mean);

% Very difficult to see anything in the plots for many parallel optimizations
% so plot at most 3
plot_n_parallel = min(n_parallel,3);

% If there are more thatn 2 parallel optimizations, the subplots get cluttered. So
% remove annotations
annotate_plots = (n_parallel<3); 

% Generate a circle for plotting
% zzz Should be marker, as in update_distribution_visualization
aaa = linspace(0,2*pi,20);
circle = 3*[sin([aaa(end) aaa])' cos([aaa(end) aaa])'];

from_summary = max(1,n_updates-plot_n_most_recent_updates+1);
colors = [linspace(0.95,main_color(1),plot_n_most_recent_updates)'...
  linspace(0.95,main_color(2),plot_n_most_recent_updates)'...
  linspace(0.95,main_color(3),plot_n_most_recent_updates)'...
  ];

n_summaries = min(n_updates,plot_n_most_recent_updates);

n_rows = 2;
if (~isempty(updater))
  n_rows = n_rows + 1;
end
n_cols = n_parallel;

offset = 1;
if (~isempty(cost_vars_history) && ~isempty(task) )
  n_rows = n_rows + 1;
  offset = 2;
  subplot(n_cols,n_rows,1:n_rows:n_cols*n_rows);
  task.plotRollouts(squeeze(cost_vars_history{end}));
  set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
end

for i_parallel=1:plot_n_parallel %#ok<FXUP>

  if (~isempty(updater))
    subplot(n_cols,n_rows,(i_parallel-1)*n_rows + offset)
    cla
    updater.visualizeUpdate(update_summaries(1,i_parallel),0,0,[1 1 1]);
    for hh=1:n_summaries
      %disp([ hh  length(summaries)-n_summaries+hh ]);
      highlight = (hh==n_summaries);
      plot_samples = (hh==n_summaries);
      i_color  = hh+(plot_n_most_recent_updates-n_summaries);
      color = colors(i_color,:);
      update_summary = update_summaries(end-n_summaries+hh,i_parallel);
      updater.visualizeUpdate(update_summary,highlight,plot_samples,color);
    end
  end
  
  % Get the covariance matrices at each update
  covars_per_update = zeros(n_updates,n_parameters,n_parameters);
  for i_update=1:n_updates
    covars_per_update(i_update,:,:) = update_summaries(i_update,i_parallel).distribution.covar;
  end  

  % Plot exploration curves
  subplot(n_cols,n_rows,(i_parallel-1)*n_rows + n_rows-1)
  plotexplorationcurve(covars_per_update);
  
end


% Get the costs at each update
costs_per_update = cell(n_updates,1);
for i_update=1:n_updates
  costs_per_update{i_update} = update_summaries(i_update,1).costs; % Costs are the same for all, so just take the first
end

% Plot learning curves
subplot(n_cols,n_rows,n_rows:n_rows:n_cols*n_rows)
plot_variance = 'samples';
plot_mean_or_first = 'mean';
plotlearningcurve(costs_per_update,plot_variance,plot_mean_or_first);

drawnow

end
