function testdynamicalsystems(test_names,system_names,dt,tau,initial_state,attractor_state)
addpath ../matlab/dynamicalsystems/
if (nargin<1), test_names =  {'rungekutta','reset','tau','attractor','perturb','euler'}; end
if (nargin<2), system_names = {'Exponential','Sigmoid','Time','SpringDamper'}; end
if (nargin<3), dt = 0.004; end
if (nargin<4), tau = 0.6; end
if (nargin<5), initial_state   = [0.5 1.0]'; end
if (nargin<6), attractor_state = [0.8 0.1]'; end

dim = length(initial_state);

for i_system = 1:length(system_names)

  clear dyn_sys
  alpha = 6;
  switch lower(system_names{i_system})
    case 'exponential'
      dyn_sys = ExponentialSystem(tau,initial_state,attractor_state,alpha);
    case 'sigmoid'
      max_rate = -20;
      inflection_point_time = tau*0.8;
      dyn_sys = SigmoidSystem(tau,initial_state,max_rate,inflection_point_time);
    case 'springdamper'
      dyn_sys = SpringDamperSystem(tau,initial_state,attractor_state,2*alpha);
    case 'time'
      dyn_sys = TimeSystem(tau);
    case 'dmp'
      n_trans = length(initial_state);

      goal_alpha = 10;
      goal_system = ExponentialSystem(dim,tau,attractor_state,initial_state,goal_alpha);

      phase_alpha = 6;
      phase_system = ExponentialSystem(1,tau,1,0,phase_alpha);
      %phase_system = TimeSystem(1,tau,0,tau);

      gating_alpha = 6;
      gating_system = ExponentialSystem(1,tau,1,0,gating_alpha);

      % Initialize one LWR for each dimension
      phase_min_max = sort([phase_system.initial_state phase_system.attractor_state]);
      n_basis_functions = 10;
      centers = linspace(phase_system.initial_state,phase_system.attractor_state,n_basis_functions);
      intersection_ratio = 0.5;
      for dd=1:dim
        function_approximators(dd) = FunctionApproximatorLWR(intersection_ratio,centers);
        function_approximators(dd).weights = 500*randn(n_basis_functions,1); % zzz
      end
      
      alpha = 14;
      dyn_sys = Dmp(dim,tau,initial_state,attractor_state,alpha,goal_system,phase_system,gating_system,function_approximators);
      % dyn_sys = Dmp(dim,tau,initial_state,attractor_state);
    otherwise
      error('Unknown system "%s"',system_names{i_system})
  end

  i_figure = 10*i_system;
  figure(i_figure)

  testdynamicalsystem(test_names,dyn_sys,dt);

end
