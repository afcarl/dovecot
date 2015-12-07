classdef UpdaterPIBB < UpdaterMean

  properties
    covar_diag_only
    covar_learning_rate
    covar_bounds
  end

  methods
    function obj = UpdaterPIBB(eliteness,weighting_method,covar_diag_only,covar_learning_rate,covar_bounds)
      if (nargin<1), eliteness           =      10; end
      if (nargin<2), weighting_method    = 'PI-BB';  end % {'PI-BB','CMA-ES'}
      if (nargin<3), covar_diag_only     =       1;  end % Update diagonal only
      if (nargin<4), covar_learning_rate =       1;  end % No lowpass filter
      if (nargin<5), covar_bounds        =  [0.01];  end %#ok<NBRAK> % Lower relative bound

      obj = obj@UpdaterMean(eliteness, weighting_method);
      
      obj.covar_diag_only     = covar_diag_only    ;
      obj.covar_learning_rate = covar_learning_rate;
      obj.covar_bounds        = covar_bounds       ;
    end

    function covar_new = updateDistributionCovar(obj, mean, covar, samples, weights)
      n_dims  = length(mean);
      n_samples = size(samples,1);

      mu = mean;

      eps = samples - repmat(mu,n_samples,1);
      covar_new = (repmat(weights,1,n_dims).*eps)'*eps;
      if (obj.covar_diag_only)
        % Only use diagonal
        covar_new = diag(diag(covar_new));
      end

      % Avoid numerical issues
      covar_new = real(covar_new);

      % Apply low pass filter
      rate = obj.covar_learning_rate;
      covar_new = (1-rate)*covar + rate*covar_new;

      if (isempty(obj.covar_bounds))
        % No bounding
        covar_new_bounded = covar_new;
      else
        covar_new_bounded = boundcovar(covar_new,obj.covar_bounds);
      end

      covar = covar_new_bounded;
    end
      
    function [distribution_new summary]  = updateDistribution(obj,distribution,samples,costs)
      % Input:
      %   distribution - distribution from which "samples" were sampled
      %                   mean, covar, sigma, evolution paths (last two only for CMA-ES)
      %   samples       - samples from above distribution. Size:  n_dofs x n_samples x n_dims
      %   costs         - costs for each sample: 1 x n_samples
      %
      % Output:
      %   distribution_new - updated distribution
      %   summary           - structure with summary of this update

      distribution_new = distribution;
      [distribution_new.mean weights] = obj.updateDistributionMean(distribution.mean,samples,costs);

      mean = distribution.mean;
      distribution_new.covar = obj.updateDistributionCovar(mean, distribution.covar, samples, weights);
      
      %-------------------------------------------------------------------------------
      % Bookkeeping: put relevant information in a summary
      summary.distribution = distribution;
      summary.samples = samples;
      summary.costs = costs;
      summary.weights = weights;
      summary.distribution_new = distribution_new;
    end

  end
end

