classdef DynamicalSystem
  %DynamicalSystem Interface for implementing dynamical systems
  %   Other dynamical systems must inherit from this class.

  properties(SetAccess = 'protected')
    
    % The original order of the system
    % All systems are rewritten as 1st order systems
    % This number represents the order of the system before the rewrite
    order_orig
    
    % Dimensionality of the state of the system
    dim
    
    % Dimensionality of the state of the system
    dim_orig
    
    % Time constant
    tau = -1;
    
    % The initial state of the system 
    x_init = [];
    
    % The attractor state, i.e. to which the system will converge 
    x_attr = [];
    
  end
    
  properties(SetAccess = 'public')
    % Name of the system
    name
    
    % Unit
    var_names
    
    % Unit
    var_units
    
    % Whether to use Runge-Kutta or Euler integration
    use_runge_kutta = 1; 
  end
    


  % These two functions really define the dynamical system. They must be 
  % implemented by every subclass.
  methods(Abstract = true, Access='public')    
    
    % The differential equation that defines the dynamical system.
    % 
    % Inputs:
    %    x      - The vector of state variables
    %    x_attr - The attractor state of the system
    %
    % Outputs:
    %    xd     - The rates of change of the state variables
    xd = differentialEquation(obj,x);  
 
    % Return a string representation of this object (Java-inspired)
    str = toString(obj);

    % Return analytical solution of the system at certain times
    %
    % Inputs:
    %
    %   ts     - A vector of times for which to compute the analytical
    %            solutions
    %   
    % Outputs:
    %
    %   x      - The system states for at the time values in 'ts'
    %            Size is T x D, where
    %              T - number of time steps
    %              D - dimensionality of the system
    %
    %   xd      - The rates of change of the state vector variables at the time 
    %             values in 'ts'
    %             Size is T x D, where
    %               T - number of time steps
    %               D - dimensionality of the system
    %
    [xs xds] = analyticalSolution(obj,ts)
    
  end

  methods(Access='public')

    % Initializing constructor
    % Sets the member variables as passed. See documentation of the member 
    % variables for their semantics.
    function obj = DynamicalSystem(order,tau,x_init,x_attr,name,var_names,var_units)
      if (nargin<6), name      = 'dynamical system'; end
      if (nargin<7), var_names = 'x'; end
      if (nargin<8), var_units = ''; end
      
      obj.order_orig = order;

      % For 1st order systems, the dimensionality of the state vector 'x' is 'dim'
      % For 2nd order systems, the system is expanded to x = [y z], where 'y' and
      % 'z' are both of dimensionality 'dim'. Therefore dim(x) is 2*dim
      obj.dim        = length(x_init)*order;
      
      % The dimensionality of the system before a potential rewrite
      obj.dim_orig   = length(x_init);
      
      obj.x_init = x_init;
      obj.x_attr = x_attr;
            
      % Set rest of the members
      obj.tau             = tau;
      obj.name            = name;
      obj.var_names       = var_names;
      obj.var_units       = var_units;
      
    end

    % Start integrating the system (with a new initial state)
    %
    % Inputs:
    %   obj    - The dynamical system
    %   x_init - The initial state of the system (optional: default is
    %                                                            obj.x_init)
    %
    % Outputs:
    %   x      - The initial state of the system
    %            The difference between the input x_init is
    %            that several sanity checks have been performed.
    %   xd     - The initial rates of change of the state of the system
    %   obj    - The dynamical system (output may be ignored if x_init was not passed)
    %
    function [x xd obj] = integrateStartWithInit(obj,x_init)
      if (nargin>1), obj = obj.setInitialState(x_init); end
      [x xd] = integrateStart(obj);
    end    

    % Start integrating the system
    %
    % Inputs:
    %   obj    - The dynamical system
    %
    % Outputs:
    %   x      - The initial state of the system
    %            The difference between the input x_init is
    %            that several sanity checks have been performed.
    %   xd     - The initial rates of change of the state of the system
    %
    function [x xd] = integrateStart(obj)
                  
      % Return value
      % For 2nd order systems, the system is expanded to x = [y z], where z is
      % initially 0. Thus, here we do x = [x_init 0] if necessary.
      x = [ obj.x_init; zeros(obj.dim-obj.dim_orig,1)];
      
      % Return value (rates of change)
      xd = obj.differentialEquation(x);
      
    end    

    % Integrate the system one time step.
    %
    % The default implementation uses Euler or 4th order Runge-Kutta integration
    % (depending on the value of the member variable 'use_runge_kutta').
    %
    % Inputs:
    %   dt     - Duration of the time step
    %   x      - The current state of the system
    %
    % Outputs:
    %   x     - The updated state of the system
    %   xd    - Rates of change of the state variables
    %
    %
    function [x xd]  = integrateStep(obj,dt,x)
      x = x(1:obj.dim);
      if (obj.use_runge_kutta)
        [x xd] = obj.integrateStepRungeKutta(dt,x);
      else
        [x xd] = obj.integrateStepEuler(dt,x);
      end
    end
    
    % Accessor function for attractor_state property.
    % Sets obj.attractor state to the value passed
    function obj = setAttractorState(obj,x_attr)
      obj.x_attr = x_attr;
      assert(isequal(size(obj.x_attr),[obj.dim_orig 1]))
    end

    
    % Accessor function for initial_state property.
    % Sets obj.intial_state to the value passed
    function obj = setInitialState(obj,x_init)      
      obj.x_init = x_init;
      assert(isequal(size(obj.x_init),[obj.dim_orig 1]))
    end
    
    % Set the time constant.
    function obj = setTau(obj,tau)
      obj.tau = tau;
      assert(obj.tau>0)
    end
    % Get the time constant.
    function tau = getTau(obj)
      tau = obj.tau;
    end
    
  end
    
  methods(Access='protected')
    % Integrate the system one time step using the simple Euler method.
    %
    % Inputs:
    %   dt     - Duration of the time step
    %   x      - The current state of the system
    %   x_attr - Attractor state of the system
    %
    % Outputs:
    %   x     - The updated state of the system
    %   xd    - Rates of change of the state variables
    %
    function [x xd] = integrateStepEuler(obj,dt,x)
      % Simple Euler integration
      xd = obj.differentialEquation(x);
      x  = x + dt*xd;
    end

    % Integrate the system one time step using 4th order Runge-Kutta
    %
    % Inputs:
    %   dt     - Duration of the time step
    %   x      - The current state of the system
    %   x_attr - Attractor state of the system
    %
    % Outputs:
    %   x     - The updated state of the system
    %   xd    - Rates of change of the state variables
    %
    function [x xd] = integrateStepRungeKutta(obj,dt,x)
      % 4th order Runge-Kutta for a 1st order system
      % http://en.wikipedia.org/wiki/Runge-Kutta_method#The_Runge.E2.80.93Kutta_method
        
      k1 = dt*obj.differentialEquation(x);
      k2 = dt*obj.differentialEquation(x+k1/2);
      k3 = dt*obj.differentialEquation(x+k2/2);
      k4 = dt*obj.differentialEquation(x+k3);
      
      x = x + (k1 + 2.0*(k2+k3) + k4)/6.0;
      xd = obj.differentialEquation(x);
      
    end

  end
  
  methods (Access='public')
    
    function [y yd ydd] = getOutput(obj,x,xd)
      if (obj.order_orig==1)
        y   = x(:,1:obj.dim);
        yd  = xd(:,1:obj.dim);
        ydd = [];
      else
        dim2 = obj.dim/2;
        y   = x(:,0*dim2+(1:dim2));
        z   = x(:,1*dim2+(1:dim2));
        yd  = xd(:,0*dim2+(1:dim2));
        zd  = xd(:,1*dim2+(1:dim2));
        % Divide by tau to go from z to y space
        % yd = z/obj.tau;
        ydd = zd/obj.tau;
      end
    end
    
    % Plot a series of states 
    % Inputs:
    %   axis_handles    - The axes on which to plot that data. Of length '0',
    %                     where '0' is the order of the system +1
    %
    %   ts              - A vector of times for which to compute the analytical
    %                     solutions
    %
    %   states          - The system states for at the time values in 'ts'
    %                     Size is T x O x D, where
    %                       T - number of time steps
    %                       O - order of the system +1
    %                       D - dimensionality of the system
    %   
    % Outputs:
    %   line_handles    - Handles to the lines of the different plots   
    %
    %function line_handles = plotStates(obj,axis_handles,ts,states)
    %  [x xd xdd] = obj.getOutput(states);
    %  line_handles = obj.plotStatesX(axis_handles,ts,x,xd,xdd);
    %end
    
  end

  methods (Access='public')
    % As above, but states has been split into the x/xd/xdd components
    % xdd may be empty.
    function line_handles = plotStates(obj,axis_handles,ts,x,xd)
      if (isempty(ts))
        % Cannot plot this
        line_handles = [];
        return; 
      end
      
      for i_order=0:obj.order_orig
        if (obj.order_orig==1)
          if (i_order==0)
            cur_states = x;
          else
            cur_states = xd;
          end
        else
          if (i_order==0)
            cur_states = x(:,1:(end/2));
          elseif (i_order==1)
            cur_states = xd(:,1:(end/2));
          else
            cur_states = xd(:,((end/2)+1):end)/obj.tau;
          end
        end
          
        subplot(axis_handles(i_order+1))
        line_handles(i_order+1,:) = plot(ts,cur_states,'-','LineWidth',1);
        hold on
        %dt = ts(2)-ts(1);
        %switch (i_order)
        %  case 0
        %  case 1
        %    plot(ts,diffnc(x,dt),'--r')
        %  case 2
        %    plot(ts,diffnc(diffnc(x,dt),dt),'--r')
        %end
        %xlabel('time (s)')
        switch (i_order)
          case 0
            %y_label = sprintf('$%s (%s)$'        ,obj.var_names,obj.var_units);
            y_label = sprintf('$%s$'        ,obj.var_names);
          case 1
            %y_label = sprintf('$\\dot{%s} (%s/s)$' ,obj.var_names,obj.var_units);
            y_label = sprintf('$\\dot{%s}$' ,obj.var_names);
          case 2
            %y_label = sprintf('$\\ddot{%s} (%s/s^2)$',obj.var_names,obj.var_units);
            y_label = sprintf('$\\ddot{%s}$',obj.var_names);
        end
        %xlabel('time (s)','Interpreter','latex');
        ylabel(y_label,'Interpreter','latex');
        axis tight;
        text(mean(xlim),min(ylim)+0.9*range(ylim),[ '{\sf ' obj.name '~}' y_label],...
          'Interpreter','latex','HorizontalAlignment','center','VerticalAlignment','middle','FontSize',10)
        text(mean(xlim),min(ylim)+0.7*range(ylim),[ '{\sf (' class(obj) ')}'],...
          'Interpreter','latex','HorizontalAlignment','center','VerticalAlignment','middle','FontSize',8)

        y_limits = ylim;
        % Add 10% padding to top and bottom
        ylim([y_limits(1)-0.1*range(y_limits) y_limits(2)+0.1*range(y_limits)])

        % The golden ratio is very accomodating to the eye
        set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
        
      end
      
    end
    
    function dim_orig = getDimOrig(obj)
      dim_orig = obj.dim_orig;
    end
  end
  
end