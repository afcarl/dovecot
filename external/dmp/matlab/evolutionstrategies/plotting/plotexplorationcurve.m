function curve_handles = plotexplorationcurve(covars_per_update)

% Plot exploration magnitude curve (largest eigenvalue of covar)
for hh=1:size(covars_per_update,1)
  covar = squeeze(covars_per_update(hh,:,:));
  exploration_curve(hh,:) = real(max(eig(covar)));
end
curve_handles = plot(exploration_curve,'-k','LineWidth',2);

axis tight
y_limits = ylim;
if ((y_limits(1)/y_limits(2))<0.2)
  % y-axis is very close to zero. So set it to zero.
  ylim([0 1.05*y_limits(2)])
end
set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
%legend('exploration magnitude')
xlabel('number of updates')
ylabel('exploration magnitude')

end
