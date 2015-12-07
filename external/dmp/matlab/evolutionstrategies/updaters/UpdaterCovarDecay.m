classdef UpdaterCovarDecay < UpdaterMean

  properties
    covar_decay_factor
  end

  methods
    function obj = UpdaterCovarDecay(eliteness,weighting_method,covar_decay_factor)
       default_covar_decay_factor = 0.95;
      if (nargin<1), eliteness           =      10; end
      if (nargin<2), weighting_method    = 'PI-BB';  end % {'PI-BB','CMA-ES'}
      if (nargin<3), covar_decay_factor  =    default_covar_decay_factor ;  end

      obj = obj@UpdaterMean(eliteness, weighting_method);
 
      obj.covar_decay_factor  = covar_decay_factor ;
      
      % Do some checks here
      if (obj.covar_decay_factor<=0 || obj.covar_decay_factor>=1)
        warning('covar decay must be in range <0-1>, but it is %1.2f. Setting to default: %1.2f',obj.covar_decay,default_covar_decay_factor) %#ok<WNTAG>
        obj.covar_decay_factor = default_covar_decay_factor;
      end


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
      
      % Update the mean
      distribution_new = distribution;
      [distribution_new.mean weights] = obj.updateDistributionMean(distribution.mean,samples,costs);

      % Update the covariance matrix
      distribution_new.covar = obj.covar_decay_factor*distribution.covar;
    end
    
  end
end

