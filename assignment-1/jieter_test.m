function [classify] = jieter_test()
    % TI2730B computational intelligence
    %
    % This is a function to be able to use local functions.
    % Jan Pieter Waagmeester

    % Settings
    debug = true;
    
    % Select only a part of the input set while testing.
    test_set_size = 3000;
    
    epochs = 400;
    learning_rate = 0.1;
    mse_threshold = 1e-5;
    
    activation = @(x)(1.0 / (1 + exp(-x)));

    % Initializer function to assign random weights between -1 ... 1
    w_initializer = @(L)(-.2 + .4 .* rand(L));

    % Training set
    if false
        % XOR for testing purposes.
        features = [0, 0; 0, 1; 1, 0; 1, 1];
        targets = [0; 1; 1; 0];

        no_hidden = 2;
    else
        % Assignment's training data
        features_raw = dlmread('data/features.txt');
        targets_raw = dlmread('data/targets.txt');

        % Translate the nx1 size matrix to an nx(range) matrix
        % with ones on the position for the expected output.
        % Each row correspondents with the expected output vector.
        targets = zeros(size(targets_raw, 1), size(unique(targets_raw), 2));
        for i=1:size(targets_raw, 1)
            targets(i, targets_raw(i)) = 1;
        end

        features = features_raw(1:test_set_size,:);
        targets = targets(1:test_set_size,:);

        no_hidden = 7;
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
    if debug
        tic;
        fprintf('Running %d epochs over trainingset size %d\n\n', epochs, size(features, 1));
    end

    % training
    for epoch = 1:epochs
        if debug && mod(epoch, epochs/10) == 0
            fprintf('Epoch #%d, elapsed: %0.1fs, last msqe: %f\n', epoch, toc, errors(epoch - 1));
            tic;
        end

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
        
        errors(epoch) = sum(e .* e) / size(features, 1);

        if errors(epoch) < mse_threshold
            fprintf('MSE < %f, quitting.', mse_threshold);
            break;
        end
    end

    figure
    semilogy(1:length(errors), errors);
    title(sprintf('Learning curve %d epochs, training set: %d, hidden neurons:', epochs, size(features, 1), no_hidden));

    xlabel('epochs');
    ylabel('mean squared error');
    ylim([0, max(errors)]);

    print('learning_curve-versie1.eps', '-depsc');
    
    % pass a reference to the forward function
    function Y = forward_single_output(feature)
       [~, Y] = forward(feature);
    end

    classify = @forward_single_output;
    if debug
       fprintf('\nLets validate:\n');

       success = 0;
       start = 5000;
       count = 2854;
       for test = 5000:(start + count)
           [~, actual] = max(classify(features_raw(test, :)));
           expected = targets_raw(test);
           if expected == actual
               success = success + 1;
           end
       end
       
       fprintf('Number of epochs:     %d,   training elements:   %d \n', epoch, test_set_size);
       fprintf('Number of tests:     %d,   hidden neurons:         %d \n', count, no_hidden);
       fprintf('Number of successes: %d,   success rate:     %0.2f\f', success, success / 2854);
       
    end
end