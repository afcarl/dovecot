classdef Updater < handle

  methods (Abstract=true)
    [distribution_new summary]  = updateDistribution(obj,distribution,samples,costs)
    subplot_handles = visualizeUpdate(obj,update_summary,highlight,plot_samples,main_color)
  end
end

