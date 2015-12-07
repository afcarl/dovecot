classdef FunctionApproximatorLWR < FunctionApproximator

  methods

    function obj = FunctionApproximatorLWR(meta_parameters,model_parameters)
      if (nargin<2), model_parameters = []; end
      obj.name = 'LWR';
      obj.meta_parameters_ = meta_parameters;
      obj.model_parameters_ = model_parameters;
    end

    function obj  = train(obj,inputs,targets)

      centers = obj.meta_parameters_.getCenters(min(inputs),max(inputs));
      widths  = obj.meta_parameters_.getWidths(centers);
      activations = obj.normalizedKernelActivations(centers, widths, inputs);

      % Make the design matrix
      X = [inputs ones(size(inputs,1),1)];
      y = targets(:);
      for bb=1:size(activations,2)
        W = diag(activations(:,bb));
        % Compute beta
        beta(bb,:) = inv(X'*W*X)*X'*W*y;
      end
      offsets = beta(:,end);
      slopes = beta(:,1:end-1);
      obj.model_parameters_ = ModelParametersLWR(centers,widths,slopes,offsets);
      obj.last_inputs  = inputs;
      obj.last_targets = targets;
      obj.last_outputs = [];
      
      
      plot_me = 0;
      if (plot_me)
        for bb=1:size(activations,2)
          W = diag(activations(:,bb));
          y_hat = X*beta(bb,:)';
          
          colors = get(gcf,'DefaultAxesColorOrder');
          n_colors = size(colors,1);

          %[val indices] = max(activations,[],2);
          dim = size(inputs,2);
          if (dim==1)
            if (bb==1)
              plot(inputs,targets,'-','LineWidth',10,'Color',0.9*ones(1,3))
              hold on
              axis square
              axis tight
            end
            plot(inputs,activations(:,bb),'-','Color',colors(mod(bb,n_colors-1)+1,:))
            %focus = (indices==bb);
            focus = activations(:,bb)>0.001;
            plot(inputs(focus),y_hat(focus),'-','Color',0.8*colors(mod(bb,n_colors-1)+1,:),'LineWidth',3)
            focus = activations(:,bb)>0.00001;
            plot(inputs(focus),y_hat(focus),'--','Color',0.8*colors(mod(bb,n_colors-1)+1,:),'LineWidth',1)
          else
            if (bb==1)
              mesh(X1,X2,Y,'EdgeColor',0.9*ones(1,3),'FaceColor','none')
              hold on
              axis square
            end
            %plot3(x(:,1),x(:,2),activations(:,bb),'.','Color',colors(mod(bb,n_colors-1)+1,:))
            %focus = (indices==bb);
            focus = activations(:,bb)>0.00001;
            plot3(x(focus,1),x(focus,2),y_hat(focus),'.','Color',0.9*colors(mod(bb,n_colors-1)+1,:))
          end

        end
      end
      
      
      
      
    end

    function [ outputs activations ] = predict(obj,inputs)
      if (isempty(obj.model_parameters_))
        %warning('Cannot make predictions if model has not been trained.') %#ok<WNTAG>
        outputs = [];
        regressor = [];
        return;
      end

      slopes  = obj.model_parameters_.slopes_;
      offsets = obj.model_parameters_.offsets_;
      X = [inputs ones(size(inputs,1),1)];
      lines = X*[slopes offsets]';

      centers = obj.model_parameters_.centers_;
      widths  = obj.model_parameters_.widths_;
      activations = obj.normalizedKernelActivations(centers, widths, inputs);
      
      outputs = sum(lines.*activations,2);
      
    end
    function obj = clear(obj)
      obj.slopes = [];
    end

    function activations = kernelActivation(obj, center, width, inputs)  %#ok<INUSL>
      % centers     = 1 x n_dim
      % widths      = 1 x n_dim
      % inputs      = n_samples x n_dim
      % activations = n_samples x 1      
      [n_samples n_dims] = size(inputs);
      activations = ones(n_samples,1);
      for i_dim=1:n_dims
        activations = activations.*exp((-0.5*(inputs(:,i_dim)-center(i_dim)).^2)/(width(i_dim).^2));        
      end
    end

    function normalized_kernel_activations = normalizedKernelActivations(obj,centers, widths, inputs)
      % centers     = n_basis_functions x n_dim
      % widths      = n_basis_functions x n_dim
      % inputs      = n_samples         x n_dim
      % activations = n_samples         x n_basis_functions
      
      [n_basis_functions n_dims] = size(centers);
      n_samples = size(inputs,1);
      
      assert(isequal(size(centers),size(widths)));
      assert(n_dims==size(inputs,2));

      % Get activations of kernels
      activations = zeros(n_samples,n_basis_functions);
      for bb = 1:n_basis_functions
        activations(:,bb) = obj.kernelActivation(centers(bb,:),widths(bb,:),inputs);
      end

      % Compute sum for each row (each value in input_vector)
      sum_activations = repmat(sum(activations,2),1,size(activations,2));

      % Normalize for each row (each value in input_vector)
      normalized_kernel_activations = activations./sum_activations;
      
      %cla
      %for bb = 1:n_basis_functions
      %  plot3(inputs(:,1),inputs(:,2),normalized_kernel_activations(:,bb),'.','Color',[bb/n_basis_functions 1-(bb/n_basis_functions) 0])
      %  hold on
      %  axis square
      %end
      %pause
      
    end

    function visualizefa(obj)
      centers = obj.meta_parameters_.getCenters(min(obj.last_inputs),max(obj.last_inputs));
      widths  = obj.meta_parameters_.getWidths(centers);

      n_in = size(obj.last_inputs,2);
      if (n_in>3)
        warning('Cannot visualize LWR when input space > 3D') %#ok<WNTAG>
        return
      end

      if (n_in==1)
        handle_center = plot(centers,0*centers,'bo');
      elseif (n_in==2)
        handle_center = plot(centers(:,1),centers(:,2),'bo');
      else
        handle_center = plot3(centers(:,1),centers(:,2),centers(:,3),'bo');
      end
      hold on

      nbf = length(centers);
      if (n_in==1)
        xs = linspace(centers(1),centers(end),100);
        kernels = obj.normalizedKernelActivations(centers, widths,xs);
        handle_ellipse = plot(xs,kernels);
      else
        for ii = 1:nbf
          covar = diag(widths(ii,:));
          %handle = draw_ellipse(diag(1./diag(covar)),centers(ii,:),0.5,'Gaussian');
          handle_ellipse(ii,:) = error_ellipse(covar,centers(ii,:),0.1); %#ok<NASGU>
        end
      end
      set(handle_ellipse(:),'Color',0.7*[1 1 1])
      hold off
      axis square
      axis tight

      set(handle_center(:),'Color',[0 0 0],'MarkerFaceColor',[0.8 0.3 0.3],'MarkerSize',5)

    end

  end
end
