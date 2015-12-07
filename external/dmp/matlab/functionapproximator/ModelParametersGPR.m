classdef ModelParametersGPR < Parameterizable
  properties
    meanfunc_
    covfunc_
    likfunc_
    hyper_parameters_
    inputs_train_
    targets_train_
  end

  methods
    function obj = ModelParametersGPR(meanfunc, covfunc, likfunc, hyper_parameters, inputs_train, targets_train)
      obj.meanfunc_ = meanfunc;
      obj.covfunc_ = covfunc;
      obj.likfunc_ = likfunc;
      obj.hyper_parameters_ = hyper_parameters;
      obj.inputs_train_ = inputs_train;
      obj.targets_train_ = targets_train;
      
    end

    function selectable_labels = getSelectableModelParameters(obj)
      selectable_labels = {};
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function size = getModelParameterValuesSize(obj)
      size = 0;
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function obj = setSelectedModelParameters(obj,selected_values_labels)
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function values = getModelParameterValues(obj)
      values = [];
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function obj = setModelParameterValues(obj,values)
      error('Not implemented yet...') %#ok<WNTAG>
    end
    function model_parameters_clone = clone(obj)
      model_parameters_clone = 0;
      error('Not implemented yet...') %#ok<WNTAG>
    end
  end
end
