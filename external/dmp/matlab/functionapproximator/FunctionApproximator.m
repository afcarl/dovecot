classdef FunctionApproximator < Parameterizable

  properties(Access='protected')
    name
    meta_parameters_
    model_parameters_
    last_inputs
    last_outputs
    last_targets
  end
  methods(Abstract = true)
    
    obj = train(obj,inputs,targets)
    
    [outputs activations] = predict(obj,inputs)    
    
    visualizefa(obj,inputs,targets)
  end
  methods
    function selectable_labels = getSelectableModelParameters(obj)
      selectable_labels = obj.model_parameters_.getSelectableModelParameters();
    end
    function size = getModelParameterValuesSize(obj)
      size = obj.model_parameters_.getModelParameterValuesSize();
    end
    function obj = setSelectedModelParameters(obj,selected_values_labels)
      obj.model_parameters_ = obj.model_parameters_.setSelectedModelParameters(selected_values_labels);
    end
    function values = getModelParameterValues(obj)
      values = obj.model_parameters_.getModelParameterValues();
    end
    function obj = setModelParameterValues(obj,values)
      obj.model_parameters_ = obj.model_parameters_.setModelParameterValues(values);
    end
    
    %obj = clear(obj)
  end
  methods
    function str = toString(obj)
      str = sprintf('%s[name=%s, ',class(obj),obj.name);
      if (isempty(obj.meta_parameters_))
        str = [str 'meta_parameters=[], '];
      else
        str = [str sprintf('meta_parameters=%s, ',obj.meta_parameters_.toString())];
      end
      if (isempty(obj.model_parameters_))
        str = [str 'model_parameters=[]'];
      else
        str = [str sprintf('model_parameters=%s',obj.model_parameters_.toString())];
      end
      str = [str ']'];
    end
    
    function visualizegridpredictions(obj,axis_handle,plot_what,grid_samples_per_dim)
      % plot_what:
      %   plot_grid_predictions
      %   plot_basis_functions
      %   plot_data
      if (nargin<2), axis_handle = gca; end
      if (nargin<3), plot_what = [1 0 1]; end
      if (nargin<4), grid_samples_per_dim = 20; end
      cla(axis_handle)

      plot_grid_predictions = plot_what(1);
      plot_basis_functions  = plot_what(2);
      plot_data             = plot_what(3);

      inputs = obj.last_inputs;
      targets = obj.last_targets;
      if (isempty(obj.last_outputs))
        outputs = obj.predict(inputs);
      else
        outputs = obj.last_outputs;
      end

      if (size(inputs,1)<2)
        min_vals = inputs-ones(size(inputs));
        max_vals =  inputs+ones(size(inputs));
        range_vals = 2*ones(size(inputs));
      else
        min_vals = min(inputs);
        max_vals = max(inputs);
        range_vals = range(inputs);
      end
      generalize_scale = 0.0;
      inputs_grid_1 = linspace(min_vals(1)-generalize_scale*range_vals(1),max_vals(1)+generalize_scale*range_vals(1),grid_samples_per_dim);
      color = [0.7 0.7 0.7];
      if (size(inputs,2)==1)
        inputs_grid = inputs_grid_1';
        hold on
        if (plot_grid_predictions || plot_basis_functions)
          [ predicted activations ] = obj.predict(inputs_grid);
          if (plot_grid_predictions)
            plot(inputs_grid,predicted,'Color',[color]) %#ok<NBRAK>
          end
          if (plot_basis_functions)
            if (~isempty(activations))
              % Some function approximators do not have basis function
              % activatitions. Do not plot them.
              for aa=1:size(activations,2)
                plot(inputs_grid,activations(:,aa),'Color',[color]) %#ok<NBRAK>
              end
              if (plot_data)
                % Scale data so that it does not interfere with the basis function
                outputs = max(max(activations)) + 0.2*(outputs-min(targets))/range(targets);
                targets = max(max(activations)) + 0.2*(targets-min(targets))/range(targets);
              end
            end
          end
          if (plot_data)
            plot(inputs,targets,'.g')
            plot(inputs,outputs,'.r')
          end
        end
        hold off

      elseif (size(inputs,2)==2)
        inputs_grid_2 = linspace(min_vals(2)-generalize_scale*range_vals(2),max_vals(2)+generalize_scale*range_vals(2),grid_samples_per_dim);
        [ inputs_grid_1_rep  inputs_grid_2_rep ] = meshgrid(inputs_grid_1,inputs_grid_2);
        inputs_grid = [ inputs_grid_1_rep(:) inputs_grid_2_rep(:) ];

        hold on
        if (plot_grid_predictions || plot_basis_functions)
          [ predicted activations ] = obj.predict(inputs_grid);
          if (plot_grid_predictions)
            z = reshape(predicted,grid_samples_per_dim,[]);
            mesh(inputs_grid_1,inputs_grid_2,z)
            colormap(color)
            alpha(1)
          end
          if (plot_basis_functions)
            activations = max(activations,[],2);
            if (~isempty(activations))
              % Some function approximators do not have basis function
              % activatitions. Do not plot them.
              z = reshape(activations,grid_samples_per_dim,[]);
              surf(inputs_grid_1,inputs_grid_2,z,'FaceColor',0.9*[1 1 1],'EdgeColor','none')
              camlight left; lighting phong
              if (plot_data)
                % Scale data so that it does not interfere with the basis function
                outputs = max(activations) + 0.2*(outputs-min(targets))/range(targets);
                targets = max(activations) + 0.2*(targets-min(targets))/range(targets);
              end
            end
          end
          if (plot_data)
            plot3(inputs(:,1),inputs(:,2),targets,'.g')
            plot3(inputs(:,1),inputs(:,2),outputs,'.r')
          end
        end
        hold off
        axis equal
        axis square
        view(-30,30)

      elseif (size(inputs,2)==3)
        inputs_grid_2 = linspace(min_vals(2)-generalize_scale*range_vals(2),max_vals(2)+generalize_scale*range_vals(2),grid_samples_per_dim);
        [ inputs_grid_1_rep  inputs_grid_2_rep ] = meshgrid(inputs_grid_1,inputs_grid_2);
        unique_inputs_3  = unique(inputs(:,3));
        for ii=1:length(unique_inputs_3)
          inputs_grid = [ inputs_grid_1_rep(:) inputs_grid_2_rep(:) unique_inputs_3(ii)*ones(grid_samples_per_dim.^2,1)];
          predicted = obj.predict(inputs_grid);

          subplot(1,length(unique_inputs_3),ii)
          select_inputs = (inputs(:,3)==unique_inputs_3(ii));
          mesh(inputs_grid_1,inputs_grid_2,reshape(predicted,grid_samples_per_dim,[]))
          if (~isempty(targets))
            hold on
            plot3(inputs(select_inputs,1),inputs(select_inputs,2),targets(select_inputs),'.')
            hold off
          end
          title(sprintf('input(3)==%1.3f',unique_inputs_3(ii)))
          axis square
        end
      else
        warning('Cannot plot for more than 3 input dimensions') %#ok<WNTAG>
      end

      axis square
      axis tight
    end
  end

end
