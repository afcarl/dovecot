classdef ExponentialSystem < DynamicalSystem
  %ExponentialSystem Dynamical system (1st order) for exponential decay
  %   See: http://en.wikipedia.org/wiki/Exponential_decay
  properties(Access='private')
    % Decay constant, see: http://en.wikipedia.org/wiki/Exponential_decay
    alpha
  end
  
  methods
    
    function [obj] = ExponentialSystem(tau,x_init,x_attr,alpha)
      if (nargin<4), alpha=6; end;
      
      order = 1; % This is a first order system
      obj = obj@DynamicalSystem(order,tau,x_init,x_attr);

      obj.alpha           = alpha;
      
    end

    function xd = differentialEquation(obj,x)
      % xd = -alpha*(x-x_g)/tau
      xd = -obj.alpha*(x(1:obj.dim)-obj.x_attr(1:obj.dim))/obj.tau;
    end

    function [xs xds] = analyticalSolution(obj,ts)
      % Formula
      % x  =              exp(-alpha*t/tau)
      % xd = (-alpha/tau)*exp(-alpha*t/tau)
      % (these are scaled and transposed according to initial and attr state).

      xs  = zeros(length(ts),obj.dim);
      xds = zeros(length(ts),obj.dim);
      % The loop is slower, but more legible than fudging around with repmat.
      for i_dim=1:obj.dim
        val_range = obj.x_init(i_dim)-obj.x_attr(i_dim);
        xs(:,i_dim)  =                  exp(-obj.alpha*ts/obj.tau)*val_range + obj.x_attr(i_dim);
        xds(:,i_dim) = -(obj.alpha/obj.tau)*exp(-obj.alpha*ts/obj.tau)*val_range;
      end
    end
  end
  
  methods
    function str = toString(obj)
      str = sprintf('%s[name=%s, tau=%1.2f, dim=%d, x_init=(',class(obj),obj.name,obj.tau,obj.dim);
      str = [str sprintf('%1.4f ',obj.x_init)];
      str = [str sprintf('), x_attr=(')];
      str = [str sprintf('%1.4f ',obj.x_attr)];
      str = [str sprintf('), alpha=%1.1f]',obj.alpha)];
    end

  end

end