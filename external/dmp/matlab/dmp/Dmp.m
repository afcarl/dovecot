classdef Dmp < DynamicalSystem & Parameterizable

  properties(Access='public')

    % Linear closed loop controller
    goal_system_             % Delayed goal function
    % Indices of the system in the state vector
    GOAL

    spring_system_    % Spring damper system
    % Indices of the system in the state vector
    SPRING
    % Indices of the Y and Z components of the spring system
    SPRING_Y
    SPRING_Z

    % Non-linear open loop controller
    phase_system_            % Phase system
    % Indices of the system in the state vector
    PHASE

    gating_system_           % To gate the output of the function approximator
    % Indices of the system in the state vector
    GATING

    function_approximators  % Function approximators

  end

  methods

    function [obj] = Dmp(tau,initial_state,attractor_state,...
        alpha_spring_damper,goal_system,phase_system,gating_system,function_approximators)

      order = 1;
      obj = obj@DynamicalSystem(order,tau,initial_state,attractor_state,'dmp');

      % obj.dim_orig = length(initial_state); % Already set in constructor above
      % This is the space required for 
      %   spring_damper : 2*dim   (because 2nd order)
      %   goal_state    : 1*dim
      %   phase_state   :     1
      %   gating_state  :     1
      obj.dim = (3*length(initial_state) + 2);

      obj.name = 'dmp';
      obj.var_names = 'y';
      obj.var_units = '';

      obj.spring_system_ = SpringDamperSystem(tau,initial_state,attractor_state,alpha_spring_damper);
      obj.spring_system_.name      = 'spring-damper';
      obj.spring_system_.var_names = 'f';
      obj.spring_system_.var_units = '';

      if (~isempty(goal_system))
        goal_system.name      = 'delayed goal';
        goal_system.var_names = 'g';
        goal_system.var_units = '';
      end
      obj.goal_system_ = goal_system;

      phase_system.name      = 'phase';
      phase_system.var_names = 's';
      phase_system.var_units = '';
      obj.phase_system_ = phase_system;

      obj.function_approximators = function_approximators;

      gating_system.name      = 'gating';
      gating_system.var_names = 's';
      gating_system.var_units = '';
      obj.gating_system_ = gating_system;

      obj.use_runge_kutta = 1;

      % Indices in the state vector of the output of the DMP
      obj.SPRING_Y   = (1+0*obj.dim_orig):(1*obj.dim_orig);
      obj.SPRING_Z   = (1+1*obj.dim_orig):(2*obj.dim_orig);
      obj.SPRING     = [obj.SPRING_Y obj.SPRING_Z];
      % Indices in the state vector of the subsystems of the DMP
      goal_order = 1;
      if (~isempty(obj.goal_system_))
        goal_order = obj.goal_system_.order_orig;
      end
      obj.GOAL       = obj.SPRING_Z(end)  + ( 1 : goal_order*obj.dim_orig   );
      obj.PHASE      = obj.GOAL(end)    + ( 1 : obj.phase_system_.order_orig   );
      obj.GATING     = obj.PHASE(end)   + ( 1 : obj.gating_system_.order_orig   );

    end

    function [y yd ydd] = getOutput(obj,x,xd)
      dim2 = obj.dim_orig/2;
      y   = x(:,obj.SPRING_Y);
      z   = x(:,obj.SPRING_Z);
      yd  = xd(:,obj.SPRING_Y);
      zd  = xd(:,obj.SPRING_Z);
      % Divide by tau to go from z to y space
      % yd = z/obj.tau;
      ydd = zd/obj.tau;
    end
  end
  methods(Access='public')
    function [x xd] = integrateStart(obj)
      x = zeros(length(obj.x_init),1);
      xd = zeros(length(obj.x_init),1);

      % Reset goal system if it exists
      if (isempty(obj.goal_system_))
        % No goal system, simply set goal state to attractor state
        x(obj.GOAL) = obj.x_attr;
        xd(obj.GOAL) = 0;
      else
        % Goal system exists. Start integrating.
        x(obj.GOAL) = obj.goal_system_.integrateStart();
      end
      % Set the attractor state of the spring system
      obj.spring_system_ = obj.spring_system_.setAttractorState(x(obj.GOAL));

      % Start all furter subsystems
      x(obj.SPRING)  = obj.spring_system_.integrateStart();
      x(obj.PHASE)   = obj.phase_system_.integrateStart();
      x(obj.GATING)  = obj.gating_system_.integrateStart();

      % Add rates of change
      xd = obj.differentialEquation(x);

    end
  end
  methods(Access='private')
    function fa_output = computeFunctionApproximatorOutput(obj,phase_state)
      fa_output = zeros(obj.dim_orig,1);
      if (~isempty(obj.function_approximators))
        for dd=1:obj.dim_orig
          output = obj.function_approximators(dd).predict(phase_state);
          if (~isempty(output))
            fa_output(dd) = output;
          end
        end
      end
    end
  end
  methods(Access='public')
    function xd = differentialEquation(obj,x) %#ok<INUSD>
      y_attr = obj.x_attr;

      xd = zeros(size(x));

      if (isempty(obj.goal_system_))
        obj.spring_system_ = obj.spring_system_.setAttractorState(y_attr);
      else
        obj.goal_system_ = obj.goal_system_.setAttractorState(y_attr);
        xd(obj.GOAL) = obj.goal_system_.differentialEquation(x(obj.GOAL)); % zzz debug this
        obj.spring_system_ = obj.spring_system_.setAttractorState(x(obj.GOAL));
      end

      xd(obj.SPRING) = obj.spring_system_.differentialEquation(x(obj.SPRING));


      xd(obj.PHASE)  = obj.phase_system_.differentialEquation(x(obj.PHASE));
      xd(obj.GATING) = obj.gating_system_.differentialEquation(x(obj.GATING));

      % Compute the output of the function approximator for each dimension
      phase_state = x(obj.PHASE);
      fa_output = obj.computeFunctionApproximatorOutput(phase_state);
      
      g  = y_attr; % zzz Initial goal state?
      y0 = obj.x_init;
      forcing_term = x(obj.GATING).*fa_output; % .*(g-x0); zzz Todo


      % Add forcing term to the ZD component of the spring state
      xd(obj.SPRING_Z) = xd(obj.SPRING_Z) + forcing_term/obj.tau;

    end

    function [xs xds] = analyticalSolution(obj,ts) %#ok<INUSD>
      ts = ts(:);

      n_time_steps = length(ts);

      if (var(diff(ts))>10^-30)
        warning('The times provided in "ts" are not equidistant. May lead to unexpected results...') %#ok<WNTAG>
      end
      dt = mean(diff(ts));

      %time_secs   = ts;
      %time_steps  = 0:(n_time_steps-1);

      % INTEGRATE SYSTEMS ANALYTICALLY AS MUCH AS POSSIBLE

      % Integrate phase
      [xs_phase xds_phase] = obj.phase_system_.analyticalSolution(ts);

      % Compute gating term
      [xs_gating xds_gating] = obj.gating_system_.analyticalSolution(ts);

      % Compute the output of the function approximator
      fa_outputs = zeros(n_time_steps,obj.dim_orig);
      if (~isempty(obj.function_approximators))
        for dd=1:obj.dim_orig
          output = obj.function_approximators(dd).predict(xs_phase);
          if (~isempty(output))
            fa_outputs(:,dd) = output;
          end
        end
      end

      % Compute forcing term for each dim_origension zzz
      %x0_rep = repmat(obj.initial_state(1:obj.dim_orig)',n_time_steps,1);
      %g_rep = goal_states(:,1:obj.dim_orig); % zzz Initial goal state?
      forcing_terms = repmat(xs_gating,1,obj.dim_orig).*fa_outputs; % .*(g_rep-x0_rep);


      % Get current delayed goal
      if (isempty(obj.goal_system_))
        % If there is no dynamical system for the delayed goal, the goal is
        % simply the attractor state
        xds_goal = zeros(n_time_steps,obj.dim_orig);
        xs_goal  = repmat(obj.x_attr',n_time_steps,1);
      
      else
        % Integrate goal system and get current goal state
        [xs_goal xds_goal] = obj.goal_system_.analyticalSolution(ts);
      end
      
      xs = zeros(n_time_steps,length(obj.x_init));
      xds = zeros(n_time_steps,length(obj.x_init));

      xs(:,obj.GOAL) = xs_goal;     xds(:,obj.GOAL) = xds_goal;
      xs(:,obj.PHASE) = xs_phase;   xds(:,obj.PHASE) = xds_phase;
      xs(:,obj.GATING) = xs_gating; xds(:,obj.GATING) = xds_gating;

      % THE REST CANNOT BE DONE ANALYTICALLY

      % Reset the dynamical system, and get the first state
      local_spring_system = SpringDamperSystem(obj.tau,obj.x_init,obj.x_attr,obj.spring_system_.damping_coefficient);

      % Set first attractor state
      local_spring_system = local_spring_system.setAttractorState(xs_goal(1,:)');
      % Start integrating spring damper system
      [ xs(1,obj.SPRING) xds(1,obj.SPRING)] = local_spring_system.integrateStart();
      % Add forcing term to the acceleration of the spring state
      xds(1,obj.SPRING_Z) = xds(1,obj.SPRING_Z) + forcing_terms(1,:)/obj.tau;

      for tt=2:n_time_steps
        % Euler integration
        xs(tt,obj.SPRING)  = xs(tt-1,obj.SPRING) + dt*xds(tt-1,obj.SPRING);

        % Set attractor state
        local_spring_system = local_spring_system.setAttractorState(xs_goal(tt,:)');
        % Integrate spring damper system
        xds(tt,obj.SPRING) = local_spring_system.differentialEquation(xs(tt,obj.SPRING)')';
        % Add forcing term to the acceleration of the spring state
        xds(tt,obj.SPRING_Z) = xds(tt,obj.SPRING_Z) + forcing_terms(tt,:)/obj.tau;
        % Compute y component from z
        xds(tt,obj.SPRING_Y) = xs(tt,obj.SPRING_Z)/obj.tau;

      end

    end
  end

  methods(Access='public')

    function [axis_handles line_handles] = plotStates(obj,ts,xs,xds,plot_blocks)

      if (nargin<5)
        plot_blocks{1} = 1:obj.dim_orig;
      end
      n_states = size(xs,1);

      T = length(ts);

      n_rows = 2;
      n_cols = 5;

      system_names =   {'phase','gating','goal','spring'};
      system_indices = {obj.PHASE , obj.GATING, obj.GOAL , obj.SPRING};
      subplot_offset = [      1          6           3         8  ];
      axis_handles = [];

      cur_figure = gcf;
      line_handles = [];
      for pp=1:length(plot_blocks)
        figure(cur_figure)
        cur_figure = cur_figure +1;

        for ss=1:length(system_names)

          % Get the current states
          cur_xs  = xs(:,system_indices{ss});
          cur_xds = xds(:,system_indices{ss});

          cur_system_name = system_names{ss};
          cur_system = eval(['obj.' cur_system_name '_system_']);

          % zzz Redo this
          %if (size(cur_states,3)==obj.dim_orig)
          %  cur_states = cur_states(:,:,plot_blocks{pp});
          %end

          % Prepare axis handles
          if (isempty(cur_system))
            order_orig = 0;
          else
            order_orig = cur_system.order_orig;
          end
          cur_axis_handles = zeros(1,order_orig+1);
          for oo=1:length(cur_axis_handles)
            cur_axis_handles(oo) = subplot(n_rows,n_cols,subplot_offset(ss)+oo-1);
          end

          if (isempty(cur_system))
            % This is not really a dynamical system
            cur_line_handles = plot(ts,cur_xs);
            line_handles = [ line_handles; cur_line_handles(:) ];
            axis tight
            text(mean(xlim),min(ylim)+0.9*range(ylim),sprintf('{\\sf %s~}',cur_system_name),...
              'Interpreter','latex','HorizontalAlignment','center','VerticalAlignment','middle','FontSize',10)
            y_limits = ylim;
            % Add 10% padding to top and bottom
            ylim([y_limits(1)-0.1*range(y_limits) y_limits(2)+0.1*range(y_limits)])
          else
            cur_line_handles = cur_system.plotStates(cur_axis_handles,ts,cur_xs,cur_xds);
            line_handles = [ line_handles; cur_line_handles(:) ];
          end

          set(cur_axis_handles,'XTick',[])

          axis_handles = [axis_handles cur_axis_handles];
        end


        % The golden ratio is very accomodating to the eye
        set(axis_handles,'PlotBoxAspectRatio',[1.618 1 1] )

        drawnow
      end

    end

    function str = toString(obj)
      str = sprintf('%s[name=%s, tau=%1.2f, dim=%d, dim_orig=%d',class(obj),obj.name,obj.tau,obj.dim,obj.dim_orig);
      str = [str ', x_init=('   sprintf('%1.4f ',obj.x_init) ')'];
      str = [str ', x_attr=(' sprintf('%1.4f ',obj.x_attr) ')'];
      if (~isempty(obj.goal_system_))
        str = [str ', goal_system=' obj.goal_system_.toString()];
      end
      str = [str ', spring_system=' obj.spring_system_.toString()];
      str = [str ', phase_system='  obj.phase_system_.toString()];
      str = [str ', gating_system=' obj.gating_system_.toString()];
      for dd=1:obj.dim_orig
        str = [str ', function_approximator[' num2str(dd-1) ']=' obj.function_approximators(dd).toString()];
      end
      str = [str ']'];
    end
    
    function selectable_labels = getSelectableModelParameters(obj)
      selectable_labels = {};
      for dd=1:obj.getDimOrig()
        cur_selectable_labels = obj.function_approximators(dd).getSelectableModelParameters();
        for ll=1:cur_selectable_labels
          % Only add if it is not already in the list
          if (isempty(strmatch(cur_selectable_labels{ll},selectable_labels)))
            selectable_labels{end+1} = cur_selectable_labels{ll};
          end
        end
      end
    end
    
    function obj = setSelectedModelParameters(obj,selected_values_labels)
      for dd=1:obj.getDimOrig()
        obj.function_approximators(dd) = obj.function_approximators(dd).setSelectedModelParameters(selected_values_labels);
      end
    end
    
    function size = getModelParameterValuesSize(obj)
      total_size = 0;
      for dd=1:obj.getDimOrig()
        total_size = total_size + obj.function_approximators(dd).getModelParameterValuesSize();
      end
      size = total_size;
    end
    
    function values = getModelParameterValues(obj)
      values = zeros(1,obj.getModelParameterValuesSize());
      offset = 0;
      for dd=1:obj.getDimOrig()
        cur_values = obj.function_approximators(dd).getModelParameterValues();
        values(offset + (1:length(cur_values))) = cur_values; 
        offset = offset + length(cur_values);
      end
    end
    
    function obj = setModelParameterValues(obj,values)
      assert(length(values)==obj.getModelParameterValuesSize());
      offset = 0;
      for dd=1:obj.getDimOrig()
        n_parameters_required = obj.function_approximators(dd).getModelParameterValuesSize();
        cur_values = values(offset+(1:n_parameters_required));
        obj.function_approximators(dd) = obj.function_approximators(dd).setModelParameterValues(cur_values);
        offset = offset +  n_parameters_required;
      end
    end
    
    function values = getModelParametersVectors(obj)
      for dd=1:obj.getDimOrig()
        values{dd} = obj.function_approximators(dd).getModelParameterValues();
      end
    end

    function obj = setModelParametersVectors(obj,values)
      for dd=1:obj.getDimOrig()
         obj.function_approximators(dd) = obj.function_approximators(dd).setModelParameterValues(values{dd});
      end
    end

    function [obj] = train(obj,ts,ys,yds,ydds,figure_handle)
      % zzz Perhaps make it so that dimensionality can change in train...
      % Requires some subsystems to change dimensionality as well

      dt = mean(diff(ts));
      if (nargin<4), yds  = diffnc(dt,ys); end
      if (nargin<5), ydds = diffnc(dt,yds); end
      if (nargin<6), figure_handle = 0; end

      [ n_time_steps dim_data ] = size(ys);
      assert(obj.dim_orig==dim_data)

      tau = ts(end);

      initial_state   = ys(1,:)';
      attractor_state = ys(end,:)';

      obj = obj.setInitialState(initial_state);
      obj = obj.setAttractorState(attractor_state);

      % Integrate analytically to get goal, gating and phase states
      xs_ana = obj.analyticalSolution(ts);
      xs_goal   = xs_ana(:,obj.GOAL);
      xs_gating = xs_ana(:,obj.GATING);
      xs_phase  = xs_ana(:,obj.PHASE);

      % Get parameters from the spring-dampers system to compute inverse
      damping_coefficient = obj.spring_system_.damping_coefficient;
      spring_constant     = obj.spring_system_.spring_constant;
      mass                = obj.spring_system_.mass;
      if (mass~=1)
        warning('Usually, spring-damper system of the DMP should have mass==1, but it is %f',mass) %#ok<WNTAG>
      end

      % Compute inverse
      f_target = obj.tau*obj.tau*ydds + (spring_constant*(ys-xs_goal) + damping_coefficient*obj.tau*yds)/mass;
      % Factor out gating
      fa_output = f_target./repmat(xs_gating,1,obj.dim_orig);

      % Train the function approximator for each dimension
      for dd=1:obj.dim_orig
        obj.function_approximators(dd) = obj.function_approximators(dd).train(xs_phase,fa_output(:,dd));
      end

      if (figure_handle>0)
        figure(figure_handle)
        clf

        subplot_numbers =[       3          6         1     8   9,  10];
        data_to_plot   = { xs_goal, xs_gating, xs_phase,   ys,yds,ydds};

        line_handles_demo = [];
        for pp=1:length(data_to_plot)
          subplot(2,5,subplot_numbers(pp))
          cur_line_handles = plot(ts,data_to_plot{pp});
          hold on
          line_handles_demo = [line_handles_demo; cur_line_handles];
        end

        [xs_ana_repro xds_ana_repro]= obj.analyticalSolution(ts);
        [axis_handles line_handles_recon] = obj.plotStates(ts,xs_ana_repro,xds_ana_repro);

        set(line_handles_demo,'LineWidth',3)
        set(line_handles_demo,'Color',[1 0.7 0.7])
        set(line_handles_demo(1:(obj.dim_orig+2)),'Color',[0.7 1 0.7])

        set(line_handles_recon,'LineStyle','--')
        set(line_handles_recon,'LineWidth',2)
        set(line_handles_recon,'Color',[0.3 0.3 0.6])

        dim_orig = obj.dim_orig;
        figure(figure_handle+1)
        clf
        for dd=1:dim_orig
          axis_handles(1) = subplot(3,dim_orig,dd+0*dim_orig);
          plot(ts,fa_output(:,dd),'-k');
          hold on
          plot(ts,f_target(:,dd),'-r');
          axis tight

          axis_handles(2) = subplot(3,dim_orig,dd+1*dim_orig);
          obj.function_approximators(dd).visualizegridpredictions(axis_handles(2),[1 0 1]); % (obj,axis_handle,plot_what,grid_samples_per_dim)

          axis_handles(3) = subplot(3,dim_orig,dd+2*dim_orig);
          obj.function_approximators(dd).visualizegridpredictions(axis_handles(3),[0 1 0],100); % (obj,axis_handle,plot_what,grid_samples_per_dim)

          % The golden ratio is very accomodating to the eye
          set(axis_handles,'PlotBoxAspectRatio',[1.618 1 1] )
        end
        drawnow
      end

    end

    % Accessor function for initial_state property.
    % Sets obj.intial_state to the value passed
    function obj = setInitialState(obj,x_init)
      obj.x_init = x_init;
      assert(isequal(size(obj.x_init),[obj.dim_orig 1]))

      % Set value in all relevant subsystems also
      obj.spring_system_ = obj.spring_system_.setInitialState(obj.x_init);
      if (~isempty(obj.goal_system_))
        obj.goal_system_ = obj.goal_system_.setInitialState(obj.x_init);
      end

    end

    % Accessor function for attractor_state property.
    % Sets obj.intial_state to the value passed
    function obj = setAttractorState(obj,x_attr)
      obj.x_attr = x_attr;
      assert(isequal(size(obj.x_attr),[obj.dim_orig 1]))

      % Set value in all relevant subsystems also
      if (~isempty(obj.goal_system_))
        obj.goal_system_ = obj.goal_system_.setAttractorState(obj.x_attr);
      end

      % Do NOT do the following. The attractor state of the spring system is
      % determined by the goal system
      % obj._spring_system_ = obj._spring_system_.setAttractorState(obj.x_attr);
    end

    % Set the time constant.
    function obj = setTau(obj,tau)
      obj.tau = tau;
      assert(obj.tau>0)

      % Set value in all relevant subsystems also
      obj.spring_system_ = obj.spring_system_.setTau(obj.tau);
      if (~isempty(obj.goal_system_))
        obj.goal_system_ = obj.goal_system_.setTau(obj.tau);
      end
      obj.phase_system_ = obj.phase_system_.setTau(obj.tau);
      obj.gating_system_ = obj.gating_system_.setTau(obj.tau);
    end


  end


end