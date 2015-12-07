function demodmp

addpath ../matlab/dmp/
addpath ../matlab/dynamicalsystems/
addpath ../matlab/functionapproximator/

%-------------------------------------------------------------------------------
% SETTINGS RELATED TO TIME

% Time constant
tau = 0.6;

% Time signal, e.g. 0.01, 0.02, 0.03 ... 2*tau
dt = 0.004;
ts = 0:dt:1.25*tau;

%-------------------------------------------------------------------------------
% CONSTRUCT THE DEFAULT DMP
initial_state   = [0.5 1.0 1.2 ];
attractor_state = [0.0 0.8 1.5 ];
dim = length(initial_state);
dmps{1} = Dmp(dim,tau,initial_state,attractor_state);

%-------------------------------------------------------------------------------
% CONSTRUCT SOME DYNAMICAL SYSTEMS NECESSARY FOR A DMP

goal_alpha = 10;
goal_system = ExponentialSystem(dim,tau,attractor_state,initial_state,goal_alpha);

phase_alpha = 6;
%phase_system = ExponentialSystem(1,tau,1,0,phase_alpha);
phase_system = TimeSystem(1,tau,0,tau);

gating_alpha = 6;
gating_system = ExponentialSystem(1,tau,1,0,gating_alpha);

%-------------------------------------------------------------------------------
% CONSTRUCT SOME FUNCTION APPROXIMATORS FOR THE DMP

% Initialize one LWR for each dimension
phase_min_max = sort([phase_system.initial_state phase_system.attractor_state]);
n_basis_functions = 10;
centers = linspace(phase_system.initial_state,phase_system.attractor_state,n_basis_functions);
intersection_ratio = 0.5;
for dd=1:dim
  function_approximators(dd) = FunctionApproximatorLWR(intersection_ratio,centers);
  function_approximators(dd).weights = 100*randn(n_basis_functions,1); % zzz
end

%-------------------------------------------------------------------------------
% CONSTRUCT THE DMP
alpha = 14;
dmps{2} = Dmp(dim,tau,initial_state,attractor_state,alpha,goal_system,phase_system,gating_system,function_approximators);


%-------------------------------------------------------------------------------
% INTEGRATE AND PLOT ALL DMPS

for i_demo=1:length(dmps)

  % Get dynamical system for this demo and print it
  dmp = dmps{i_demo};
  disp(dmp.toString());

  %-----------------------------------------------------------------------------
  % INTEGRATE STEP BY STEP
  
  % Now initialize (reset) and integrate system
  % This is where we will store the states over time
  [dmp state_vector ] = dmp.reset();% Reset the dynamical system
  state_dmp = dmp.fromStateVector(state_vector);

  states(1) = state_dmp; % Put first state in matrix
  % Allocate last element also to avoid growing array
  states(length(ts)) = states(1);

  for tt=2:length(ts)
    state_dmp = dmp.integrateStepDmpState(dt,state_dmp); % Integration
    states(tt) = state_dmp;
  end

  %-----------------------------------------------------------------------------
  % PLOTTING (USING Dmp::plotStates)
  figure(i_demo)
  set(gcf,'Name',sprintf('%s (%d)',class(dmp),i_demo))
  clf
  dmp.plotDmpStates(states);

end
end
