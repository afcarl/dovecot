classdef TaskSolverIdentity < TaskSolver
  methods
    function obj = TaskSolverIdentity()
    end
    
    function cost_vars = performRollouts(obj,samples,task_parameters) %#ok<INUSL,INUSD>
      %   samples         = n_samples x n_dim
      %   task_parameters = n_samples x n_task_pars
      %   cost_vars       = n_samples x n_cost_vars
      if (iscell(samples))
        if (length(samples)>1)
          warning('TaskSolverIdentity expect samples to be a matrix, or a cell array of matrices of length 1.') %#ok<WNTAG>
        end
        samples = samples{1};
      end
      cost_vars = samples;
    end
  end
end

