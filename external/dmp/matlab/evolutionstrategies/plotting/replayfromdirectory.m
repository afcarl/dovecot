function summaries = replayfromdirectory(directory,plot_n_most_recent_summaries)
if (nargin<2), plot_n_most_recent_summaries=10; end

updater_mean = UpdaterMean; % zzz 


task = [];
if (exist([directory 'task.txt'],'file'))  
  str = fileread([directory 'task.txt']);
  task = Task.fromString(str);
end

summaries = UpdateSummary.readHistoryFromDirectory(directory);

cost_vars_history = {};

n_updates = size(summaries,1);
for i_update=1:n_updates
  filename = sprintf('%s/update%05d/cost_vars.txt',directory,i_update);
  if (exist(filename,'file'))
    cost_vars_history{i_update} = load(filename);
  end
  plotlearninghistory(summaries(1:i_update,:),updater_mean,cost_vars_history,task,plot_n_most_recent_summaries);
  pause(0.1);
end