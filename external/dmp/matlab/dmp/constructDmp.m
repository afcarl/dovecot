function dmp = constructDmp(tau, x_init, x_attr, dmp_type, function_approximators)

if (nargin<4), dmp_type = 'KULVICIUS_2012_JOINING'; end
if (nargin<5), function_approximators=[]; end

if (strcmp(dmp_type,'IJSPEERT_2002_MOVEMENT'))
  goal_system = [];
  phase_system  = ExponentialSystem(tau,1,0,10);
  gating_system = ExponentialSystem(tau,1,0,10);
elseif (strcmp(dmp_type,'KULVICIUS_2012_JOINING'))
  goal_system = ExponentialSystem(tau,x_init,x_attr,15);
  phase_system  = TimeSystem(tau);
  gating_system = SigmoidSystem(tau,1,-40,0.75*tau);
else
  error('Unknown Dmp type "%s"',dmp_type)
end

alpha_spring_damper = 20;
dmp = Dmp(tau, x_init, x_attr, alpha_spring_damper, goal_system, phase_system, gating_system, function_approximators);

end

