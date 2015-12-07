classdef FunctionApproximatorGPR < FunctionApproximator
  %FunctionApproximatorGPR Summary of this class goes here
  %   Detailed explanation goes here

  methods

    function obj = FunctionApproximatorGPR(meta_parameters,model_parameters)
      if (nargin<2), model_parameters = []; end
      obj.name = 'LWR';
      obj.meta_parameters_ = meta_parameters;
      obj.model_parameters_ = model_parameters;
    end
    
    function [obj outputs] = train(obj,inputs,targets)
      
      obj.last_inputs = inputs;
      obj.last_targets = targets;
      
      hyper_parameters = obj.meta_parameters_.hyper_parameters_;
      meanfunc = obj.meta_parameters_.meanfunc_;
      covfunc = obj.meta_parameters_.covfunc_;
      likfunc = obj.meta_parameters_.likfunc_;
      
      D = size(inputs,2);
      if (~isempty(meanfunc))
        hyper_parameters.mean = ones(D+1,1);
      end

      % Train hyperparameters
      n = size(inputs,1);
      norm_in = range(inputs);
      norm_in(norm_in==0) = 1;
      inputs_train_norm = inputs-repmat(mean(inputs),n,1);
      inputs_train_norm  = inputs_train_norm./repmat(norm_in,n,1);
      
      
      hyper_parameters = minimize(hyper_parameters, @gp, -100, @infExact, meanfunc, covfunc, likfunc, inputs_train_norm, targets);
      
      obj.model_parameters_ = ModelParametersGPR(meanfunc, covfunc, likfunc, hyper_parameters, inputs, targets);
      
      [ outputs ] = obj.predict(inputs);
      
      obj.last_outputs = outputs;
      
    end
    
    function [ outputs activations ] = predict(obj,inputs)
      inputs_train = obj.model_parameters_.inputs_train_;
      
      % Inputs used to generate output
      n = size(inputs_train,1);
      norm_in = range(inputs_train);
      norm_in(norm_in==0) = 1;
      inputs_train_norm  = inputs_train-repmat(mean(inputs_train),n,1);
      inputs_train_norm  = inputs_train_norm./repmat(norm_in,n,1);

      meanfunc = obj.model_parameters_.meanfunc_;
      covfunc = obj.model_parameters_.covfunc_;
      likfunc = obj.model_parameters_.likfunc_;
      hyper_parameters = obj.model_parameters_.hyper_parameters_;
      

      % Current inputs
      n = size(inputs,1);
      inputs_norm = inputs-repmat(mean(inputs_train),n,1);
      inputs_norm  = inputs_norm./repmat(range(inputs_train),n,1);


      % Doing predictions with Gaussian Process
      [outputs outputs_s2] = gp(hyper_parameters, @infExact, meanfunc, covfunc, likfunc, inputs_train_norm, obj.model_parameters_.targets_train_, inputs_norm);

      activations = [];

    end
    
    function visualizefa(obj,inputs,targets) %#ok<INUSD>
    end
    
    function obj = clear(obj)
    end

  end


end
