classdef UpdateSummary

  properties
    distribution
    samples
    costs
    weights
    distribution_new
  end

  methods
    function obj = UpdateSummary(distribution, samples, costs, weights, distribution_new)
      if (nargin==5)
        obj.distribution = distribution;
        obj.samples = samples;
        obj.costs = costs;
        obj.weights = weights;
        obj.distribution_new = distribution_new;
      end
    end

    function success = saveToDirectory(obj,parentdirectory,directory)

      % Make directory if it doesn't already exist
      if (~exist(directory,'dir'))
        [s,mess,messid] = mkdir(parentdirectory,directory);
      end

      filename = sprintf('%s/%s/distribution_mean.txt',parentdirectory,directory);
      data = obj.distribution.getMean();
      save(filename,'data','-ascii');

      filename = sprintf('%s/%s/distribution_covar.txt',parentdirectory,directory);
      data = obj.distribution.getCovar();
      save(filename,'data','-ascii');

      filename = sprintf('%s/%s/samples.txt',parentdirectory,directory);
      data = obj.samples;
      save(filename,'data','-ascii');

      filename = sprintf('%s/%s/costs.txt',parentdirectory,directory);
      data = obj.costs;
      save(filename,'data','-ascii');

      filename = sprintf('%s/%s/weights.txt',parentdirectory,directory);
      data = obj.weights;
      save(filename,'data','-ascii');

      filename = sprintf('%s/%s/distribution_new_mean.txt',parentdirectory,directory);
      data = obj.distribution_new.getMean();
      save(filename,'data','-ascii');

      filename = sprintf('%s/%s/distribution_new_covar.txt',parentdirectory,directory);
      data = obj.distribution_new.getCovar();
      save(filename,'data','-ascii');

      success = true;

    end
  end

  methods(Static)
    function update_summaries = readFromDirectory(directory)
      if (~exist(directory,'dir'))
        warning('Cannot read from directory "%s".',directory) %#ok<WNTAG>
        update_summaries = [];
        return;
      end

      n_parallel = 1;
      has_parallel = false;
      suffix = '';
      
      while(exist(sprintf('%s/costs%02d.txt',directory,n_parallel+1),'file'))
        has_parallel = true;
        n_parallel = n_parallel + 1;
      end
                  
      % Allocate memory
      update_summaries(1,n_parallel) = UpdateSummary;

      for i_parallel=1:n_parallel
        
        if (has_parallel)
          suffix = sprintf('%02d',i_parallel);
        end

        samples = load(sprintf('%s/samples%s.txt',directory,suffix));
        costs = load(sprintf('%s/costs%s.txt',directory,suffix));
        weights = load(sprintf('%s/weights%s.txt',directory,suffix));


        distribution_mean  = load(sprintf('%s/distribution_mean%s.txt',directory,suffix));
        distribution_covar = load(sprintf('%s/distribution_covar%s.txt',directory,suffix));
        distribution = DistributionGaussian(distribution_mean, distribution_covar);

        distribution_new_mean= load(sprintf('%s/distribution_new_mean%s.txt',directory,suffix));
        distribution_new_covar = load(sprintf('%s/distribution_new_covar%s.txt',directory,suffix));
        distribution_new = DistributionGaussian(distribution_new_mean, distribution_new_covar);

        update_summaries(i_parallel) = UpdateSummary(distribution, samples, costs, weights, distribution_new);
        
      end


    end

    function update_summaries_history = readHistoryFromDirectory(directory)

      i_update = 1;
      directory_update = sprintf('%s/update%05d/',directory,i_update);

      % Don't know how many there will be, so start with 0
      update_summaries_history = UpdateSummary.empty(0,0);

      fprintf('Reading update summaries from directory "%s".',directory);
      while (exist(directory_update,'dir'))
        fprintf('.');
        update_summaries_history(i_update,:) = UpdateSummary.readFromDirectory(directory_update);

        i_update = i_update + 1;
        directory_update = sprintf('%s/update%05d/',directory,i_update);
      end
      fprintf('\n');

    end
  end

end