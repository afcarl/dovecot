function lwr_multidim

n_basis_functions = 12;
width=0.2;

n_colors = n_basis_functions;
colormap(ones(n_colors,3));
colors = colormap(jet);
colors_hsv = rgb2hsv(colors);
colors_hsv(:,2) = 0.7;
colors_faded = hsv2rgb(colors_hsv); %#ok<NASGU>
colors_hsv(:,3) = 0.8;
colors = hsv2rgb(colors_hsv); %#ok<NASGU>


for dim=1:1


  if (dim==1)
    x = linspace(0,2*pi,100)';
    y = 1.5*sin(x);

  else
    [X1,X2] = meshgrid(-2:.1:2, -2:.1:2);
    Y = X1 .* exp(-X1.^2 - X2.^2) + 0.05*X2;

    x1 = X1(:);
    x2 = X2(:);
    x = [x1 x2];
    y = Y(:)';
  end


  n = length(y);


  % http://en.wikipedia.org/wiki/Design_matrix#Simple_Regression
  % http://www.mathworks.com/help/curvefit/least-squares-fitting.html

  % Make the weights matrix
  if (dim==1)
    w_b = zeros(n_basis_functions,n);
    centers = linspace(x(1),x(end),n_basis_functions);
    for bb=1:n_basis_functions
      w_b(bb,:) = exp(-(x - centers(bb)).^2./(2*width^2));
    end
  else
    w_b = zeros(n_basis_functions*n_basis_functions,n);
    centers1 = linspace(x(1,1),x(end,1),n_basis_functions);
    centers2 = linspace(x(1,2),x(end,2),n_basis_functions);
    bb=1;
    for bb1=1:n_basis_functions
      for bb2=1:n_basis_functions
        w_b(bb,:) = exp(-(x(:,1) - centers1(bb1)).^2./(2*width^2)).*exp(-(x(:,2) - centers2(bb2)).^2./(2*width^2));
        bb = bb + 1;
      end
    end
    n_basis_functions = size(w_b);
  end
  
  wb_rep = repmat(sum(w_b),size(w_b,1),1);
  w_b = w_b./wb_rep;

  % Make the design matrix
  X = [x ones(size(x,1),1)];

  for bb=1:n_basis_functions

    W = diag(w_b(bb,:));
    % Compute b
    if (dim==1)
      beta(bb,:) = inv(X'*W*X)*X'*W*y;
    else
      beta(bb,:) = inv(X'*W*X)*X'*W*y';
    end

    y_hat = X*beta(bb,:)';
    

    if (bb==n_basis_functions)
      lines = X*beta';
      outputs = sum(lines.*w_b',2);
    end

    [val indices] = max(w_b);
    subplot(1,2,dim)
    if (dim==1)
      if (bb==1)
        data_handle = plot(x(1:3:end),y(1:3:end),'o','LineWidth',1,'MarkerFaceColor',0*ones(1,3),'MarkerEdge','none');
        plot(x,y,'-','LineWidth',10,'Color',0.9*ones(1,3));
        hold on
      end
      plot(x,w_b(bb,:),'-','Color',colors(bb,:))
      focus = (indices==bb);
      focus_first = find(focus,1);
      focus(focus_first) = 0;
      %if (focus_first>1)
      %  focus(focus_first-1) = 1;
      %end      
      focus = w_b(bb,:)>-0.00001;
      plot(x(focus),y_hat(focus),'--','Color',colors(bb,:),'LineWidth',1)
      focus = w_b(bb,:)>0.7;
      plot(x(focus),y_hat(focus),'-','Color',colors(bb,:),'LineWidth',6)
      if (bb==n_basis_functions)
        uistack(data_handle,'top')
        plot(x,outputs,'-k','LineWidth',1)
      end
    else
      if (bb==1)
        mesh(X1,X2,Y,'EdgeColor',0.9*ones(1,3),'FaceColor','none')
        hold on
        axis square
      end
      %plot3(x(:,1),x(:,2),w_b(bb,:),'.','Color',colors(mod(bb,n_colors-1)+1,:))
      focus = (indices==bb);
      %focus = w_b(bb,:)>0.00001;
      plot3(x(focus,1),x(focus,2),y_hat(focus),'.','Color',0.9*colors(mod(bb,n_colors-1)+1,:))
    end
  end
  
  
  hold off
  axis square
  axis tight
  if (dim==1)
    ylim([-2 2])
    xlabel('x')
    ylabel('y = 1.5*sin(x)')
    set(gca,'PlotBoxAspectRatio',[1.618 1 1] )
  end



end