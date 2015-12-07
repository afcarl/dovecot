classdef FunctionApproximatorLWPR < FunctionApproximator
  %FunctionApproximatorLWPR Summary of this class goes here
  %   Detailed explanation goes here

  methods
    
    function obj = FunctionApproximatorLWPR(meta_parameters,model_parameters)
      if (nargin<2), model_parameters = []; end
      obj.name = 'LWPR';
      obj.meta_parameters_ = meta_parameters;
      obj.model_parameters_ = model_parameters;
    end
    
    function [ outputs activations ] = predict(obj,inputs)
      if (isempty(obj.model_parameters_))
        %warning('Cannot make predictions if model has not been trained.') %#ok<WNTAG>
        outputs = [];
        activations = [];
        return;
      end
      outputs = lwpr_predict(obj.model_parameters_.model_,inputs',0.00001);
      outputs = outputs';
      activations = getactivations(obj,inputs);
    end
    
    function activations = getactivations(obj,inputs)
      x = inputs';
      [d,N] = size(x);
      model = obj.model_parameters_.model_;
      for i=1:length(model.sub.rfs),
        RFS = model.sub.rfs(i);

        if N>1
          xn = x.*repmat(model.norm_in.^(-1),1,N);
        else
          xn = x./model.norm_in;
        end
        for n=1:N
          % compute the weight
          % subtract the center
          xc = xn(:,n) - RFS.c;
          activations(n,i) = lwpr_x_kernel(model.kernel,xc'*RFS.D*xc);
        end
      end
      %figure(14)
      %surf(activations)
      %pause
    end
    
    function [obj outputs] = train(obj,inputs,targets)
      
      nIn  = size(inputs,2);
      nOut = size(targets,2);
      
      %Initialization phase
      model = lwpr_init(nIn,nOut,'name',obj.name);

      model = lwpr_set(model,'init_D',obj.meta_parameters_.init_D_);
      model = lwpr_set(model,'w_gen',obj.meta_parameters_.w_gen_);
      model = lwpr_set(model,'w_prune',obj.meta_parameters_.w_prune_);
      
      model = lwpr_set(model,'update_D',obj.meta_parameters_.update_D_);
      model = lwpr_set(model,'init_alpha',obj.meta_parameters_.init_alpha_);
      model = lwpr_set(model,'diag_only',obj.meta_parameters_.diag_only_);
      model = lwpr_set(model,'penalty',obj.meta_parameters_.penalty_);
      
      model = lwpr_set(model,'meta',obj.meta_parameters_.use_meta_);
      model = lwpr_set(model,'meta_rate',obj.meta_parameters_.meta_rate_);
      model = lwpr_set(model,'kernel',obj.meta_parameters_.kernel_name_);

      
      norm_in = range(inputs)';
      norm_out = range(targets)';
      % If norm_in is equal to 0 (perhaps due to non-varying dimensions), set it to 1 here.
      norm_in(norm_in==0) = 1;
      norm_out(norm_out==0) = 1;
      % Transfer to model
      model = lwpr_set(model,'norm_in',norm_in);
      model = lwpr_set(model,'norm_out',norm_out);

      %  Transfer model into mex-internal storage
      ID = lwpr_storage('Store',model);
      
      N = size(inputs,1);
      outputs = zeros(N,model.nOut);
      tic; % start the time counter
      % train the model
      j = 50;
      while (j>=0)
        if (j==0)
          inds = 1:N;
        else
          inds = randperm(N);
        end
        mse = 0;
        for i = 1:N
          [model outputs(i,:)] = lwpr_update(model,inputs(inds(i),:)',targets(inds(i),:)');
          mse = mse + (targets(inds(i),:)-outputs(i,:)).^2;
        end
        nMSE = mse/N/var(targets,1);
        if (mod(j,5)==0)
          fprintf(1,'iter=%d (#Data=%d #rfs=%d nMSE=%5.3f)\n',j,lwpr_num_data(model),lwpr_num_rfs(model),nMSE);
        end
        if (nMSE<0.000 && j>1)
          % Good enough, stop here
          fprintf(1,'iter=%d (#Data=%d #rfs=%d nMSE=%5.3f) (GOOD ENOUGH)\n',j,lwpr_num_data(model),lwpr_num_rfs(model),nMSE);
          % Good enough, do only one more run
          j = 1;
        end
        j = j-1;
                
      end
      elapsed_time = toc; %#ok<NOPRT,NASGU> % stop the time counter
      % extract the weights
      % weights = zeros(obj.nbf,1);
      % for bb = 1:obj.nbf
      %   weights(bb,:) = model.sub.rfs(bb).w;
      % end
      
      obj.model_parameters_ = ModelParametersLWPR(ID,model);
      obj.last_inputs  = inputs;
      obj.last_targets = targets;
      obj.last_outputs = outputs;
    end
    
    function visualizefa(obj,inputs,targets)
      if (obj.model.nIn>3)
        warning('Cannot visualize LWPR when input space > 3D') %#ok<WNTAG>
        return
      end

      nbf = obj.get_n_basis_functions();
      prev_cmap = colormap;
      colormap(ones(nbf,3)); % To set number of colors
      colormap(copper);         % To set colormap
      cmap = colormap;       % To get colormap
      colormap(prev_cmap)    % Set colormap to original colormap

      for ii = 1:nbf
        centers(ii,:) =  obj.model.sub.rfs(ii).c;
        covar = obj.model.sub.rfs(ii).D;
        if (obj.model.nIn>1)
          %if (isequal(diag(diag(covar)),covar))
          %  error_ellipse(diag(1./diag(covar)),centers(ii,:));
          error_ellipse(inv(covar),centers(ii,:),'conf',0.1);
          %  % Equivalent to: draw_ellipse(squeeze(covar(ii,:,:)),centers(ii,:),0.5,'Gaussian')
          %else
          %handle = draw_ellipse(covar,centers(ii,:),0.5,'Gaussian');
          %end
          %set(handle,'Color',cmap(ii,:))
          hold on
        end
      end
      if (obj.model.nIn==1)
        handle_center = plot(centers,0*centers,'ob');
        hold on
      elseif (obj.model.nIn==2)
        handle_center = plot(centers(:,1),centers(:,2),'ob');
      else
        handle_center = plot3(centers(:,1),centers(:,2),centers(:,3),'ob');
      end
      set(handle_center(:),'Color',[0 0 0],'MarkerFaceColor',[0.8 0.3 0.3],'MarkerSize',5)
      hold off
      axis equal % Normalized space, so we can do this
      axis tight
      if (nbf>4 && obj.model.nIn>1)
        min_vals = min(centers)-0.5*range(centers);
        max_vals = max(centers)+0.5*range(centers);
        axis_limits = [ min_vals; max_vals ];
        axis(axis_limits(:));
      end

      % Plot some predictions?
      if (nargin>1)
        if (obj.model.nIn>2)
          warning('Cannot visualize predictions when input space > 2D') %#ok<WNTAG>
          return;
        else
          hold on
          predicted = obj.predict(inputs);
          % Normalize inputs
          inputs = inputs./repmat(obj.model.norm_in',size(inputs,1),1);
          if (obj.model.nIn==1)
            plot(inputs,predicted,'.','Color',0.8*ones(1,3))
            if (nargin>2)
              plot(inputs,targets,'.','Color',0.4*ones(1,3))
              plot(inputs([1 1]),[targets predicted],'-','Color',0.8*ones(1,3))
            end
            axis tight
          else
            plot3(inputs(:,1),inputs(:,2),predicted,'.','Color',0.8*ones(1,3))
            if (nargin>2)
              plot3(inputs(:,1),inputs(:,2),targets,'.','Color',0.4*ones(1,3))
              plot3(inputs(:,[1 1])',inputs(:,[2 2])',[targets predicted]','-','Color',0.8*ones(1,3))
            end
            axis square
          end
          hold off
        end
      end
    end
    
    function obj = clear(obj)
      % disposes the internally stored model pointed to by ID
      lwpr_storage('Free',obj.model_parameters_.model_.ID);
    end
    
    function n_basis_functions = get_n_basis_functions(obj)
      n_basis_functions = lwpr_num_rfs(obj.model_parameters_.model_);
    end

  end


end
