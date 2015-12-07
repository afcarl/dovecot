

tau=1.2;
initial_state=3;
max_rate=-5;
inflection_point_time = tau*0.75;
dyn_sys = SigmoidSystem(tau,initial_state,max_rate,inflection_point_time);

dt = 0.01;
ts = -0.5*tau:dt:tau*1.5;

figure(1)
clf
max_ff = 3;
for ff=0:max_ff

  if (ff==1)
    dyn_sys = dyn_sys.setTau(tau*0.75);
  end
  if (ff==2)
    dyn_sys = dyn_sys.setInitialState(initial_state*1.1);
  end
  if (ff==3)
    initial_state = [3 2]';
    dyn_sys = SigmoidSystem(tau,initial_state,max_rate,inflection_point_time);
    figure(2)
    clf
  end

  [xs xds] = dyn_sys.analyticalSolution(ts);

  subplot(1,2,1)
  plot(ts,xs,'Color',[ff/max_ff 1-ff/max_ff 0],'LineWidth',2)
  axis tight
  hold on
  for dd=1:length(dyn_sys.Ks)
    plot([0 0 ts(1)],[0 initial_state(dd)*ones(1,2)],'-g')
    plot([dyn_sys.inflection_point_time*ones(1,2) ts(1)],[0 dyn_sys.Ks(dd)/2 dyn_sys.Ks(dd)/2],'-b')
    plot(xlim,dyn_sys.Ks(dd)*ones(1,2),'--b')
  end
  ylim([ 0 1.1*max(dyn_sys.Ks)])
  plot(tau*ones(1,2),ylim,'-k')

  subplot(1,2,2)
  plot(ts,xds,'Color',[ff/max_ff 1-ff/max_ff 0],'LineWidth',2)
  hold on
  plot(ts,diffnc(xs,dt),'Color',[ff/max_ff 1-ff/max_ff 0])
  plot(dyn_sys.inflection_point_time*ones(1,2),ylim,'-b')
  axis tight
  plot(tau*ones(1,2),ylim,'-k')
  plot(0*ones(1,2),ylim,'-k')


end


