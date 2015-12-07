classdef UpdaterCEM < UpdaterPIBB

  methods
    function obj = UpdaterCEM(eliteness,weighting_method,covar_diag_only,covar_learning_rate,covar_bounds)
      if (nargin<1), eliteness           =      10; end
      if (nargin<2), weighting_method    =   'CEM';  end % {'PI-BB','CMA-ES'}
      if (nargin<3), covar_diag_only     =       1;  end % Update diagonal only
      if (nargin<4), covar_learning_rate =       1;  end % No lowpass filter
      if (nargin<5), covar_bounds        =   [0.1];  end %#ok<NBRAK> % Lower relative bound

      obj = obj@UpdaterPIBB(eliteness, weighting_method,covar_diag_only,covar_learning_rate,covar_bounds);
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

      % Here's the tricky bit in CEM! Use update mean.
      %mean = distribution.mean;
      mean = distribution_new.mean;
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

