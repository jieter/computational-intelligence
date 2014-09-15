function [classify] = train_ANN()
    % TI2730B computational intelligence
    %
    % Jan Pieter Waagmeester

    % Settings
    epochs = 100;
    learning_rate = 0.1;

    activation = @(x)(1 / (1 + exp(-x)));

    % Initializer function to assign random weights between -1 ... 1
    w_initializer = @(L)(-.2 + .4 .* rand(L));

    % Training set
    if 0
        % XOR for testing purposes.
        features = [0, 0; 0, 1; 1, 0; 1, 1];
        targets = [0; 1; 1; 0];

        no_hidden = 2;
    else
        % Assignment's training data
        features = dlmread('data/features.txt');
        targets_raw = dlmread('data/targets.txt');

        % Select only a part of the input set while testing.
        test_len = 500;
        features = features(1:test_len,:);
        targets_raw = targets_raw(1:test_len,:);

        % Translate the nx1 size matrix to an nx(range) matrix
        % with ones on the position for the expected output.
        % Each row correspondents with the expected output vector.
        targets = zeros(size(targets_raw, 1), size(unique(targets_raw), 2));
        for i=1:size(targets_raw, 1)
            targets(i, targets_raw(i)) = 1;
        end

        no_hidden = 10;
    end

    no_inputs = size(features, 2);
    no_outputs = size(targets, 2);

    % Initialize weights for all neurons
    w_ij = w_initializer([no_inputs, no_hidden]);
    w_jk = w_initializer([no_hidden, no_outputs]);

    threshold_hidden = w_initializer([1, no_hidden]);
    threshold_outputs = w_initializer([1, no_outputs]);
    
    function [y_hidden, y_output] = forward(feature)
        y_hidden = zeros(1, no_hidden);
        for j = 1:no_hidden
            X = dot(feature, w_ij(:, j));
            y_hidden(j) = activation(X - threshold_hidden(j));
        end

        y_output = zeros(1, no_outputs);
        for k = 1:no_outputs
           X = dot(y_hidden, transpose(w_jk(:, k)));
           y_output(k) = activation(X - threshold_outputs(k));
        end
    end

    errors = zeros(1, epochs); 
    % training
    for epoch = 1:epochs

        % iterate over training set.
        for current = 1:size(features, 1)

        %%%%% forward phase
            [y_hidden, y_output] = forward(features(current, :));

        %%%%% backward phase

            % calculate output error
            e = targets(current, :) - y_output;

            e_gradient_output = y_output .* (1 - y_output) .* e;

            % y * (1 - y) * sum(of each  (e_gradient_output * w_hidden))
            e_gradient_hidden = zeros(1, no_hidden);
            for j = 1:no_hidden
                e_gradient_hidden(j) = y_hidden(j) * (1 - y_hidden(j)) * ...
                                       sum(e_gradient_output .* w_jk(j, :));
            end

            % calculate delta's
            d_threshold_outputs = learning_rate .* (-1)     .* e_gradient_output;
            d_threshold_hidden  = learning_rate .* (-1)     .* e_gradient_hidden; 
            d_weight_jk         = learning_rate .* y_output .* e_gradient_output;

            % calculate inpute delta's.
            d_weight_ij = zeros(no_inputs, no_hidden);
            % TODO: rewrite to be more matlabish.
            for i = 1:no_inputs
                for j = 1:no_hidden
                    d_weight_ij(i, j) = learning_rate .* features(current, i) .* e_gradient_hidden(j);
                end
            end

            % adjust input weights
            w_ij = w_ij + d_weight_ij;

            % adjust hidden weights
            for k = 1:no_outputs
                w_jk(:, k) = w_jk(:, k) + d_weight_jk(k);
            end

            % adjust thresholds
            threshold_outputs = threshold_outputs + d_threshold_outputs;
            threshold_hidden = threshold_hidden + d_threshold_hidden;
        end

        errors(epoch) = sum(e .* e);
    end

    plot(errors, 'b-');
    xlim([1, epoch + 1]);
    xlabel('epochs');

    ylim([0, max(errors + 0.1)]);
    ylabel('sum-squared error');

    % pass a reference to the forward function
    function Y = forward_single_output(feature)
       [~, Y] = forward(feature);
    end
    classify = @forward_single_output;
end