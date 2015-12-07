classdef TimeSystem < DynamicalSystem
  % Dynamical system that represents a time signal.
  %   x always starts at 0 and xd is constant (1/tau)
  %   This represents a monotonically increasing system that starts at 0, and
  %   thus mimics time.s
  %   Once the state exceeds 1 (x>1), then xd=0, i.e. x remains constant. 
  %   This may be a "weird" system, but it is very useful as a time signal in
  %   dynamical movement primitives.
    
  methods
    
    % Time system is entirely defined by tau
    function [obj] = TimeSystem(tau)
      order = 1;
      dim = 1; % Time system is always 1-dimensional
      x_init   = zeros(dim,1);
      x_attr = ones(dim,1);
      obj = obj@DynamicalSystem(order,tau,x_init,x_attr);
    end
    
    function xd = differentialEquation(obj,x)
      % if state<1: xd = 1/obj.tau
      % else        xd = 0
      xd = ones(obj.dim,1)/obj.tau; 
      xd(x>1) = 0;
    end
    
    function [xs xds] = analyticalSolution(obj,ts) %#ok<INUSD,INUSL>
      ts = ts(:);
      velocity_stop_index = find(ts>obj.tau,1)-1;
      
      
      xs  = repmat(ts/obj.tau,1,obj.dim);
      xs(velocity_stop_index+1:end) = 1;
      
      xds = zeros(length(ts),obj.dim);
      xds(1:velocity_stop_index) = 1/obj.tau;

    end
  end
  
  methods
    function str = toString(obj)
      str = sprintf('%s[name=%s, tau=%1.2f, dim=%d]',class(obj),obj.name,obj.tau,obj.dim);
    end
    
  end

end