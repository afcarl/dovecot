classdef Parameterizable
  
  methods(Abstract=true)
    selectable_labels = getSelectableModelParameters(obj);
    size = getModelParameterValuesSize(obj);
    obj = setSelectedModelParameters(obj,selected_values_labels);
    values = getModelParameterValues(obj)
    obj = setModelParameterValues(obj,values)
  end
end


