classdef SigmoidSystem < DynamicalSystem
  %SigmoidSystem Dynamical system (1st order) for Sigmoid decay/growth
  %   See: http://en.wikipedia.org/wiki/Sigmoid_decay
  properties(SetAccess='private')
    max_rate
    inflection_point_time
    Ks
  end
  
  methods
    
    function [obj] = SigmoidSystem(tau,x_init,max_rate,inflection_point_time)
      if (nargin<2), x_init=1; end;
      if (nargin<3), max_rate=-10; end;
      if (nargin<4), inflection_point=0; end;

      x_attr = zeros(size(x_init));
      
      order = 1; % This is a first order system
      obj = obj@DynamicalSystem(order,tau,x_init,x_attr);

      obj.max_rate                = max_rate;
      obj.inflection_point_time   = inflection_point_time;
      obj.Ks = obj.computeKs(obj.x_init, obj.max_rate, obj.inflection_point_time);
    end

   
    function xd = differentialEquation(obj,x) %#ok<INUSD>
      x = x(1:obj.dim);
      xd = obj.max_rate*x.*(1-x./obj.Ks);
    end
    
    function [xs xds] = analyticalSolution(obj,ts) %#ok<INUSD>
      
      % Notation: 
      %   http://en.wikipedia.org/wiki/Logistic_function#In_ecology:_modeling_population_growth
      %   http://mathworld.wolfram.com/LogisticEquation.html
      % Confusing bit: N(t)==x(t) in this code, whereas x(t) = N(t)/K above.
      %
      %   N(t) = K / ( 1 + (K/N_0 - 1)*exp(-r*t))   here, N == x
      %        = K / ( 1 + b*exp(-r*t))             with (K/N_0 - 1)
      %
      % Derivative of  N(t) = K/(1+b*exp(-r*t)) = K*(1+b*exp(-r*t))^-1
      %   N'(t) =  -K*(1 + b*exp(-r*t))^-2 * -r*b*exp(-r*t)  
      %         =  K*r*b*(1 + b*exp(-r*t))^-2 * exp(-r*t)  
      
      xs  = zeros(length(ts),obj.dim);
      xds = zeros(length(ts),obj.dim);

      % Auxillary variables to improve legibility
      r = obj.max_rate;
      exp_rt = exp(-r*ts);
      
      for dd=1:obj.dim
        % Auxillary variables to improve legibility
        K = obj.Ks(dd);
        b = (K/obj.x_init(dd))-1;
        
        xs(:,dd)  = K./(1+b*exp_rt);
        xds(:,dd) = K*r*b*(1 + b*exp_rt).^-2 .* exp_rt;
      end
            
    end

        % Accessor function for initial_state property.
    % Sets obj.intial_state to the value passed
    function obj = setInitialState(obj,x_init) 
      obj.x_init = x_init;
      assert(isequal(size(obj.x_init),[obj.dim_orig 1]))
      obj.Ks = obj.computeKs(obj.x_init, obj.max_rate, obj.inflection_point_time);
    end
    
   % Set the time constant.
    function obj = setTau(obj,tau)
      prev_tau = obj.tau;
      obj.tau = tau;
      assert(obj.tau>0)
      
      obj.inflection_point_time = obj.tau*obj.inflection_point_time/prev_tau;
      obj.Ks = obj.computeKs(obj.x_init, obj.max_rate, obj.inflection_point_time);
    end

    function Ks = computeKs(obj,N_0s, r, inflection_point_time) %#ok<INUSL>
      % Known
      %   N(t) = K / ( 1 + (K/N_0 - 1)*exp(-r*t))
      %   N(t_inf) = K / 2
      % Plug into each other and solve for K
      %   K / ( 1 + (K/N_0 - 1)*exp(-r*t_infl)) = K/2
      %              (K/N_0 - 1)*exp(-r*t_infl) = 1
      %                             (K/N_0 - 1) = 1/exp(-r*t_infl)
      %                                       K = N_0*(1+(1/exp(-r*t_infl)))
      Ks = zeros(size(N_0s));
      for dd=1:obj.dim_orig
        Ks(dd) = N_0s(dd)*(1+(1/exp(-r*inflection_point_time)));
      end
    end
    
    function str = toString(obj)
      str = sprintf('%s[name=%s, tau=%1.2f, dim=%d, ',class(obj),obj.name,obj.tau,obj.dim);
      str = [str sprintf('max_rate=%1.1f, inflection_point=%1.1f]',obj.max_rate,obj.inflection_point_time)];
    end

  end

end