function demodynamicalsystems

addpath ../matlab/dynamicalsystems/


%-------------------------------------------------------------------------------
% SETTINGS RELATED TO TIME

% Time constant
tau             = 0.6;

% Time signal, e.g. 0.01, 0.02, 0.03 ... 2*tau
dt = 0.004;
ts = 0:dt:2*tau;

%-------------------------------------------------------------------------------
% CONSTRUCT SOME DYNAMICAL SYSTEMS (IN A CELL ARRAY)

% Contruct a 1D exponential system
initial_state   = 1;
attractor_state = 0;
alpha           = 6;
dim             = length(initial_state);
dyn_systems{1}  = ExponentialSystem(dim,tau,initial_state,attractor_state,alpha);

% Contruct a 2D exponential system
initial_state   = [1 0.5];
attractor_state = [0 1.2];
alpha           = 6;
dim             = length(initial_state);
dyn_systems{2}  = ExponentialSystem(dim,tau,initial_state,attractor_state,alpha);

% Contruct a 4D spring-damper system
initial_state   = [1 0.5 0.5 0.7];
attractor_state = [0 1.2 0.0 0.6];
alpha           = 6;
dim             = length(initial_state);
dyn_systems{3}  = SpringDamperSystem(dim,tau,initial_state,attractor_state,alpha);

% Again but with a higher alpha
alpha           = 2*alpha;
dyn_systems{4}  = SpringDamperSystem(dim,tau,initial_state,attractor_state,alpha);


%-------------------------------------------------------------------------------
% INTEGRATE AND PLOT ALL DYNAMICAL SYSTEMS IN THE CELL ARRAY
for i_demo=1:length(dyn_systems)
  
  % Get dynamical system for this demo and print it
  dyn_sys = dyn_systems{i_demo};
  disp(dyn_sys.toString());
  
  
  %-----------------------------------------------------------------------------
  % INTEGRATE STEP BY STEP
  
  % Now initialize (reset) and integrate system
  % This is where we will store the states over time
  states_step = zeros(length(ts),dyn_sys.dim*(dyn_sys.order+1));
  [dyn_sys state] = dyn_sys.reset();  % Reset the dynamical system
  states_step(1,:) = state;           % Put first state in matrix
  for tt=2:length(ts) % Integration
    states_step(tt,:) = dyn_sys.integrateStep(dt,states_step(tt-1,:)')';
  end

  
  %-----------------------------------------------------------------------------
  % SOLVE ANALYTICALLY 
  states_analytical = dyn_sys.analyticalSolution(ts);

  
  %-----------------------------------------------------------------------------
  % PLOTTING (USING DynamicalSystem::plotStates)
  figure(i_demo)
  clf
  set(gcf,'Name',sprintf('%s %dD',class(dyn_sys),dyn_sys.dim))
  for sp=1:(dyn_sys.order+1)
    axis_handles(sp) = subplot(1,3,sp);
  end

  line_handles_step = dyn_sys.plotStates(axis_handles,ts,states_step);
  set(line_handles_step,'LineWidth',4)
  set(line_handles_step,'Color',[0.8 0.8 1])

  line_handles_analytical = dyn_sys.plotStates(axis_handles,ts,states_analytical);
  set(line_handles_analytical,'LineStyle','--')
  set(line_handles_analytical,'LineWidth',2)
  set(line_handles_analytical,'Color',[0.3 0.3 0.6])
  
  legend([line_handles_step(1) line_handles_analytical(2)],{'step-by-step integration', 'analytical solution'});
  
end

end