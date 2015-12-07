figure(1)

subplot(1,3,1)
mp = MetaParametersLWR(10);
centers = mp.getCenters(0,1);
plot(centers,0*centers,'o');
axis square

subplot(1,3,2)
mp = MetaParametersLWR([10 4]);
centers = mp.getCenters([0 4],[1 5]);
plot(centers(:,1),centers(:,2),'o');
axis square


subplot(1,3,3)
mp = MetaParametersLWR([10 4 5]);
centers = mp.getCenters([0 4 6],[1 5 8]);
plot3(centers(:,1),centers(:,2),centers(:,3),'o');
axis square


figure(2)

[X1,X2] = meshgrid(-2:.1:2, -2:.1:2);
Y = X1 .* exp(-X1.^2 - X2.^2) + 0.05*X2;

x1 = X1(:);
x2 = X2(:);
x = [x1 x2];
y = Y(:)';

for n_centers=1:3
  figure(n_centers+1)
  meta_parameters = MetaParametersLWR(2*[n_centers n_centers]+1);
  centers = meta_parameters.getCenters(min(x),max(x));

  fa = FunctionApproximatorLWR(meta_parameters);
  fa = fa.train(x,y);
  y_rep = fa.predict(x);

  mesh(X1,X2,Y,'FaceColor','none','EdgeColor',0.9*ones(1,3))
  hold on
  plot3(x1,x2,y_rep,'.r')
  hold off
  axis square
end