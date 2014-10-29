function [c] = main(products)
    settings = load('network-weights-0.92821.mat');

    threshold_hidden = settings.threshold_hidden;
    threshold_outputs = settings.threshold_output;
    w_ij = settings.w_ij;
    w_jk = settings.w_jk;
    activation = @(x)(1.0 ./ (1 + exp(-x)));

    no_hidden = 20;
    no_inputs = 10;
    no_outputs = 7;

    % this is the forward phase in a function to be albe to use it later.
    function [y_hidden, y_output] = forward(feature)
        for j = 1:no_hidden
            y_hidden(j) = sum(feature .* transpose(w_ij(:, j)));
        end
        y_hidden = activation(y_hidden - threshold_hidden);

        for k = 1:no_outputs
           y_output(k) = sum(y_hidden .* transpose(w_jk(:, k)));
        end
        y_output = activation(y_output - threshold_outputs);
    end

    % pass a reference to the forward function
    function Y = forward_single_output(feature)
       [~, Y] = forward(feature);
    end

    function c = classify_category(feature)
        [~, c] = max(forward_single_output(feature));
    end



    for i = 1:length(products)
        c(i) = classify_category(products(i, :));
    end


end
