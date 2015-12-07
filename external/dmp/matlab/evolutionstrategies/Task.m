classdef Task < handle

  methods(Abstract = true)
    costs = costFunction(obj,cost_vars,task_parameters)
    line_handles = plotRollouts(obj,cost_vars,axes_handle);
  end
  methods(Static)
    function task = fromString(str)
      token = regexp(str,'(.+)[','tokens');
      class_name = char(token{1});
      command = sprintf('%s.fromStringSubclass(str)',class_name);
      task = eval(command);
    end
  end
  methods(Static, Abstract = true)
    task = fromStringSubclass(str);
  end
end
