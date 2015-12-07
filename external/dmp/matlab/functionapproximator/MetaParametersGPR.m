classdef MetaParametersGPR

  properties(SetAccess='private')
    meanfunc_
    covfunc_
    likfunc_
    hyper_parameters_
 end

  methods
    function obj = MetaParametersGPR(covar)
      if (nargin<1), covar = 1; end
      
      %obj.meanfunc = [];
      obj.meanfunc_ = {@meanSum, {@meanLinear, @meanConst}};
      obj.hyper_parameters_.mean = [1; 1; 1];

      obj.covfunc_ = {@covMaterniso, covar};
      ell = 1/4;
      sf = 1;
      obj.hyper_parameters_.cov = log([ell; sf]);
      %covfunc = @covSEiso;
      %obj.hyper_parameters.cov = [0; 0];

      obj.likfunc_ = @likGauss;
      sn = 0.1;
      obj.hyper_parameters_.lik = log(sn);
      %obj.hyper_parameters.lik = log(0.1);      
    end

    function meta_parameters_clone = clone(obj)
    end
  end
end