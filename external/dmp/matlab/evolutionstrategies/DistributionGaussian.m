classdef DistributionGaussian
  
  properties
    n_dims
    mean
    covar
  end

  methods
    function obj = DistributionGaussian(mean,covar)
      if (min(size(mean))~=1)
        error('Mean of Gaussian distribution must be a vector, but it is a matrix of size %d x %d. ',size(mean,1),size(mean,2));
      end
      if (length(mean)~=size(covar,1) || length(mean)~=size(covar,2))
        error('Mean of Gaussian distribution is of size %d x %d. In that case, the covariance matrix must be of size %d x %d, but it is %d x %d',size(mean,1),size(mean,2),length(mean),length(mean),size(covar,1),size(covar,2));
      end
      
      obj.n_dims = length(mean);
      obj.mean = mean(:)'; %#ok<PROP> % Make sure it is a column vector
      obj.covar=covar;
    end
    function samples = generateSamples(obj,n_samples)
      mu = obj.mean;
      covar = obj.covar;
      if (isequal(diag(diag(covar)),covar))
        % For diagonal covar, manual sampling is much faster than using mvnrnd (older
        % versions)
        n_dims = length(mu);
        samples = repmat(mu,n_samples,1) + randn(n_samples,n_dims).*repmat(sqrt(diag(covar))',n_samples,1);
      else
        samples = mvnrnd(mu,covar,n_samples);
      end
    end
    
    function grid_samples = getGridSamples(obj,n_samples_per_dimension) %#ok<INUSD>

      % Copied and adapted from error_ellipes
      % http://www.mathworks.com/matlabcentral/fileexchange/4705
      sigmas = linspace(1,3,n_samples_per_dimension(1));
      points_on_ellipse = n_samples_per_dimension(2);

      p=linspace(0,2*pi,points_on_ellipse+1);
      p(end) = [];

      [eigvec,eigval] = eig(obj.covar); % Compute eigen-stuff
      xy = [cos(p'),sin(p')] * sqrt(eigval) * eigvec'; % Transformation
      x = xy(:,1);
      y = xy(:,2);

      grid_samples = [];
      for sigma=sigmas
        grid_samples = [grid_samples; (obj.mean(1)+sigma*x) (obj.mean(2)+sigma*y)];
      end

    end

  end

end
