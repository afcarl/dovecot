function [curve_handles sample_handles std_handles ] = plotlearningcurve(costs_per_update,plot_variance,plot_mean_or_first)
if (nargin<2), plot_variance = 'samples'; end
if (nargin<3), plot_mean_or_first = 'mean'; end

% COMPUTE SOME VALUE
std_costs_exploration = [];
all_costs = [];
costs_mean = [];
n_rollouts_per_update = [];
for hh=1:size(costs_per_update,1)
  all_costs = [all_costs; costs_per_update{hh}];
  costs_mean(hh,:) = mean(costs_per_update{hh});
  n_rollouts_per_update(hh) = size(costs_per_update{hh},1);
  std_costs_exploration(hh,:) = sqrt(var(costs_per_update{hh}));
end

if (strcmpi('mean',plot_mean_or_first))
  evaluation_rollouts = cumsum(n_rollouts_per_update(1:end));
  plot_costs = costs_mean;
  legend_labels{1} = 'cost (average over an epoch)';
else
  evaluation_rollouts = cumsum([1 n_rollouts_per_update(1:end-1)]);
  plot_costs = all_costs(evaluation_rollouts,:);
  legend_labels{1} = 'cost (first evaluation in an epoch)';
end


% PLOTTING

% Little hack to find out which xticks Matlab would use if we do not plot
% individual samples.
cla
plot(plot_costs);
x_tick_updates = get(gca,'XTick');
if (x_tick_updates(1)==0)
  x_tick_updates = x_tick_updates(2:end-1);
end
cla

% Now do the actual plotting
std_handles = [];
sample_handles = [];
if (strcmpi('samples',plot_variance))
  % The individual samples
  sample_handles = plot(all_costs(:,1),'.');
  hold on
  legend_labels{2} = 'cost (all samples)';
elseif (strcmpi('std',plot_variance))
  mean_plus_std = plot_costs+std_costs_exploration;
  mean_min_std = plot_costs-std_costs_exploration;
  std_handles = patch(evaluation_rollouts([1:end end:-1:1]),[mean_plus_std(:,1); mean_min_std(end:-1:1,1)],1,'EdgeColor','none');
  legend_labels{2} = 'cost (std over an epoch)';
  hold on
end

% The learning curve
curve_handles = plot(evaluation_rollouts,plot_costs(:,1),'-','LineWidth',2);
hold on
% The different cost components, i.e. learing curves for each sub-cost
if (size(costs_mean,2)>1)
  sub_curve_handles = plot(evaluation_rollouts,plot_costs(:,2:end),'-','LineWidth',1);
  curve_handles = [curve_handles; sub_curve_handles];
end
hold off

set(sample_handles,'Color',0.8*ones(1,3));
set(curve_handles(1),'Color','k');
set(std_handles,'FaceColor',0.8*ones(1,3));

if (length(x_tick_updates)<=length(evaluation_rollouts))
  set(gca,'XTick',evaluation_rollouts(x_tick_updates));
  set(gca,'XTickLabel',x_tick_updates);
end

axis tight
y_limits = ylim;
if ((y_limits(1)/y_limits(2))<0.2)
  % y-axis is very close to zero. So set it to zero.
  ylim([0 y_limits(2)])
end
set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
% zzz legend([curve_handles; sample_handles; std_handles],legend_labels)
xlabel('number of updates')
ylabel('costs')

end