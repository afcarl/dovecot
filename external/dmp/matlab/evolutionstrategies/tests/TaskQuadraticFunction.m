classdef TaskQuadraticFunction < Task

  properties(SetAccess='private')
    minimum_
    plot_rollouts_axis_
  end
  methods
    function obj = TaskQuadraticFunction(minimum)
      obj.minimum_ = minimum;
    end
  end
  
  methods(Static)
    function obj = fromStringSubclass(str)
      token = regexp(str,'minimum=(.+)]','tokens');
      minimum_str = char(token{1});
      minimum = sscanf(minimum_str,'%f');
      
      obj = TaskQuadraticFunction(minimum);
    end
  end
    
  methods
    function costs = costFunction(obj,cost_vars,task_parameters) %#ok<INUSD>
      cost_vars = squeeze(cost_vars);
      
      % Cost is quadratic distance to minimum
      n_samples = size(cost_vars,1);
      minimum_rep = repmat(obj.minimum_,n_samples,1);
      costs = sum((cost_vars-minimum_rep).^2,2);
    end

    function line_handles = plotRollouts(obj,cost_vars,task,axes_handle)
      %   cost_vars       = n_samples x n_cost_vars
      plot(obj.minimum_(1),obj.minimum_(2),'o','MarkerFaceColor',[0.6 1 0.6],'MarkerEdgeColor','k','MarkerSize',10);
      hold on
      line_handles = plot(cost_vars(:,1),cost_vars(:,2),'.','Color',[0.6 0.6 0.6]);
      hold off
      
      if (isempty(obj.plot_rollouts_axis_))
        axis tight
        cur_axis = axis;
        padding = 0.5;
        obj.plot_rollouts_axis_(1) = cur_axis(1) - padding*range(cur_axis(1:2));
        obj.plot_rollouts_axis_(2) = cur_axis(2) + padding*range(cur_axis(1:2));
        obj.plot_rollouts_axis_(3) = cur_axis(3) - padding*range(cur_axis(3:4));
        obj.plot_rollouts_axis_(4) = cur_axis(4) + padding*range(cur_axis(3:4));
      else
        obj.plot_rollouts_axis_(1) = min(obj.plot_rollouts_axis_(1),min(cost_vars(:,1)));
        obj.plot_rollouts_axis_(2) = max(obj.plot_rollouts_axis_(2),max(cost_vars(:,1)));
        obj.plot_rollouts_axis_(3) = min(obj.plot_rollouts_axis_(3),min(cost_vars(:,2)));
        obj.plot_rollouts_axis_(4) = max(obj.plot_rollouts_axis_(4),max(cost_vars(:,2)));
      end
      
      axis(obj.plot_rollouts_axis_)
      
    end
    
  end
end
