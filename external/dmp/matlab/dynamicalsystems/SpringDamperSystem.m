classdef SpringDamperSystem < DynamicalSystem
  %SpringDamperSystem Dynamical system (2nd order) 
  %   See: http://en.wikipedia.org/wiki/Damped_spring-mass_system
  
  properties(SetAccess='private')
    damping_coefficient
    spring_constant
    mass    
  end
  
  methods
    
    function [obj] = SpringDamperSystem(tau,x_init,x_attr,damping_coefficient,spring_constant,mass)
      if (nargin<4), damping_coefficient=6; end;
      if (nargin<6), mass=1; end;
      if (nargin<5), spring_constant=damping_coefficient.^2/(4*mass); end; % Critically damped
      
      order = 2; % This is a second order system
      obj = obj@DynamicalSystem(order,tau,x_init,x_attr);
      
      obj.damping_coefficient = damping_coefficient;
      obj.spring_constant = spring_constant;
      obj.mass = mass;
      
    end

    function xd = differentialEquation(obj,x)
      
      % Spring-damper system was originally 2nd order, i.e. with [x xd xdd]
      % After rewriting it as a 1st order system it becomes [y z yd zd], with yd = z; 
      
      % Get 'y' and 'z' parts of the state in 'x'
      dim2 = obj.dim/2;
      y  = x(0*dim2 + (1:dim2)); 
      z  = x(1*dim2 + (1:dim2));

      % Compute yd and zd
      % See  http://en.wikipedia.org/wiki/Damped_spring-mass_system#Example:_mass.E2.80.93spring.E2.80.93damper
      % and equation 2.1 of http://www-clmc.usc.edu/publications/I/ijspeert-NC2013.pdf
      yd = z/obj.tau;
      zd = (-obj.spring_constant*(y-obj.x_attr) - obj.damping_coefficient*z)/(obj.mass*obj.tau);
      
      % Put the 'yd' and 'zd' parts of the rates of change in 'xd'
      xd = [yd; zd];
      
    end
    
    function [x xd] = analyticalSolution(obj,ts)
      % See http://en.wikipedia.org/wiki/Damped_spring-mass_system#Critical_damping_.28.CE.B6_.3D_1.29
     
      % Closed form solution to 2nd order canonical system
      % This system behaves like a critically damped spring-damper system
      % http://en.wikipedia.org/wiki/Damped_spring-mass_system
      omega_0 = sqrt(obj.spring_constant/obj.mass)/obj.tau;     % natural frequency
      zeta = obj.damping_coefficient/(2*sqrt(obj.mass*obj.spring_constant));  % damping ratio
      if (zeta~=1)
        warning('Spring-damper system is not critically damped (zeta=%f)',zeta) %#ok<WNTAG>
      end

      % Example
      %  _______________
      %    obj.dim = 4
      %  _______
      %  dim2= 2
      % [y_1 y_2 z_1 z_2 yd_1 yd_2 zd_1 zd_2]
      
      dim2 = obj.dim/2;
      y = zeros(length(ts),dim2);
      z = zeros(length(ts),dim2);
      yd = zeros(length(ts),dim2);
      zd = zeros(length(ts),dim2);
      
      % The loop is slower, but more legible than fudging around with repmat.
      for i_dim=1:dim2
      
        % This is one y variable
        y0  = obj.x_init(i_dim)-obj.x_attr(i_dim);
        
        if (length(obj.x_init)>=obj.dim)
          % Initial velocities also given (z)
          yd0 = obj.x_init(dim2 + i_dim);          
        else
          % Initial velocities not given: set to zero
          yd0 = zeros(size(y0));          
        end
        
        A = y0;
        B = yd0 + omega_0*y0;
        
        % Two extra terms for convenience
        ABts = A+B*ts;
        exp_term = exp(-omega_0*ts);
       
        % Closed form solutions
        % See http://en.wikipedia.org/wiki/Damped_spring-mass_system
        y(:,i_dim) = ABts.*exp_term + obj.x_attr(i_dim);
        
        % Derivative of the above (use product rule: (f*g)' = f'*g + f*g' 
        % and then simplify
        yd(:,i_dim) = (B - omega_0*ABts).*exp_term;
        
        % Derivative of the above (use product rule: (f*g)' = f'*g + f*g' 
        % and then simplify
        ydd(:,i_dim) = ( -omega_0*( 2*B - omega_0*ABts )).*exp_term;
        
        % This is how to compute the 'z' terms from the 'y' terms
        z(:,i_dim)  = yd(:,i_dim)*obj.tau;
        zd(:,i_dim) = ydd(:,i_dim)*obj.tau;
        
      end
      
      % Put subcomponents into vector of state variables and their rates of
      % change
      x  = [y z];
      xd = [yd zd];
      
    end
  end
  
  methods
    function str = toString(obj)
      str = sprintf('%s[name=%s, tau=%1.2f, dim=%d, x_attr=(',class(obj),obj.name,obj.tau,obj.dim);
      str = [str sprintf('%1.4f ',obj.x_attr)];
      str = [str sprintf('),damping_coefficient=%1.1f, spring_constant=%1.1f, mass=%1.1f]',...
        obj.damping_coefficient,obj.spring_constant,obj.mass)];
    end
    
  end

end