classdef TaskViapointSolverDmp < TaskSolver

  properties
    dmp_
    n_dims_
    n_time_steps_    
  end

  methods
    function obj = TaskViapointSolverDmp(first_arg,n_time_steps,optimize_types)
      if (nargin<2), n_time_steps=101; end;
      if (nargin<3), optimize_types{1} = 'slopes'; end;

      if (isnumeric(first_arg))
        obj.dmp_ = [];
        obj.n_dims_ = first_arg;
      else
        obj.dmp_ = first_arg;
        obj.n_dims_ = obj.dmp_.getDimOrig();
        obj.dmp_ = obj.dmp_.setSelectedModelParameters(optimize_types);
      end
      
      obj.n_time_steps_ = n_time_steps;
    end
    
    function cost_vars = performRollouts(obj,samples,task_parameters) %#ok<INUSD,INUSL>
      % Samples can be either
      % - a matrix (of size n_samples x n_model_parameters)
      % - a cell array (of length n_dims_dmp) of matrices (of size n_samples x
      %                                                      n_model_parameters)
      % Here, we convert the former in the latter
      if (~iscell(samples))
        samples_matrices = samples;
        clear samples
        samples{1} = samples_matrices;
      end

      n_dims_dmp = length(samples);
      assert(obj.dmp_.getDimOrig()==n_dims_dmp)
      n_samples = size(samples{1},1);
      
      

      obj.dmp_.getTau();
      ts = linspace(0,1*obj.dmp_.getTau(),obj.n_time_steps_)';
      
      n_cost_vars = 3*n_dims_dmp+1; % [ys yds ydds]^n_dims_dmp + ts
      cost_vars = zeros(n_samples,obj.n_time_steps_*n_cost_vars); 

      for k=1:n_samples

        model_params = {};
        for dd=1:n_dims_dmp
          model_params{dd} = samples{dd}(k,:);
        end
        obj.dmp_ = obj.dmp_.setModelParametersVectors(model_params);

        [xs xds] = obj.dmp_.analyticalSolution(ts);
        %obj.dmp_.plotStates(ts,xs,xds);
        [ys yds ydds] = obj.dmp_.getOutput(xs,xds);
        
        traj = [ys yds ydds ts];
        cost_vars(k,:) = reshape(traj',1,[]);
      end
    end

    %   function observation = observation_function_viapoint_solver_dmp(task,N,min_values,max_values,figure_handle) %#ok<DEFNU>
    %     n_dim = length(task.viapoint);
    %     if (n_dim~=2)
    %       error('Sorry. observation_function_viapoint only works for n_dim==2 (but it is %d)',n_dim)
    %     end
    %     if (nargin<2), N = 20; end
    %     if (nargin<3), min_values = zeros(1,n_dim); end
    %     if (nargin<4), max_values = ones(1,n_dim); end
    %     if (nargin<5), figure_handle = 0; end
    %
    %     % Scale viapoint in normalized space [0-1]
    %     scaled_viapoint = (task.viapoint-min_values)./(max_values-min_values);
    %     % Generate X/Y grid in normalized space
    %     [X Y] = meshgrid(linspace(0,1,N),linspace(0,1,N));
    %     % Get value in multi-variate normal distribution
    %     Z = mvnpdf([ X(:) Y(:)],scaled_viapoint,0.005*eye(n_dim));
    %     % Make an NxN image of this.
    %     image = reshape(Z,N,N);
    %
    %     max_image = max(max(image));
    %     image(image<0.01*max_image) = 0;
    %     image = image + 2*randn(size(image));
    %
    %     if (figure_handle)
    %       figure(figure_handle)
    %       mesh(image)
    %       axis square
    %       axis tight
    %       colormap(gray)
    %     end+
    %
    %     observation = image(:);
    %
    %
    %   end
%     function cost_vars = performRolloutsExternal(obj,thetas)
% 
%       n_samples = size(thetas,2);
%       for k=1:n_samples
%         theta = squeeze(thetas(:,k,:));
%         trajectories(k) = dmpintegrate(task_solver.y0,task_solver.g,theta,task_solver.time,task_solver.dt,task_solver.time_exec);
%       end
%       directory = ['./data_' task.name];
%       write_trajectories_to_ascii(directory,trajectories);
% 
%       done_filename = sprintf('%s/done.txt',directory);
%       if (exist(done_filename,'file'))
%         delete(done_filename)
%       end
% 
%       % Run external program here
%       command = ['./tasks/viapoint/task_viapoint_external_cpp/task_viapoint_external_cpp ' pwd '/' directory];
%       fprintf('External program running... ');
%       system(command);
% 
%       % Wait for the file. A crude but simple way for communication.
%       while (~exist(done_filename,'file'))
%         pause(0.1)
%         fprintf('.');
%       end
%       fprintf('done.\n');
% 
%       cost_vars = read_costvars_from_ascii(directory);
% 
%     end


  end

end