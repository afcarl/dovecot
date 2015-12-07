classdef TaskSolver < handle

  methods(Abstract = true)
    cost_vars = performRollouts(obj,samples,task_parameters);
  end
end

