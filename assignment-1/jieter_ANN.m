function [errors, success_rate] = jieter_ANN(no_hidden, epochs, debug)
    % TI2730B computational intelligence
    %
    % This is a function to be able to use local functions.
    % Jan Pieter Waagmeester

    if nargin < 1
        no_hidden = 7;
    end

    if nargin < 2
        epochs = 300;
    end

    if nargin < 3
        debug = true;
    else
        debug = false;
    end

    learning_rate = 0.1;
    mse_threshold = 1e-5;

    activation = @(x)(1.0 ./ (1 + exp(-x)));

    % Initializer function to assign random weights
    w_initializer = @(L, w_init_range)(-w_init_range + (2 * w_init_range) .* rand(L));

    % Assignments training data
    features_raw = dlmread('data/features.txt');
    targets_raw = dlmread('data/targets.txt');

    no_inputs = size(features_raw, 2);
    no_outputs = size(unique(targets_raw), 1);

    all_features = 7854;
    % Partition the provided features
    training_set_size = 4000;
    validation_set_size = 1500;
    test_set_size = all_features - training_set_size - validation_set_size;

    if test_set_size < 100
        error('test_set_size size too small, decrease the training/validation set size');
    end

    function [features, targets] = partition_dataset(a, b)
        set_size = b - a + 1;
        features = features_raw(a:b, :);

        targets = sparse(1:set_size, targets_raw(a:b, :), 1, set_size, no_outputs);
    end

    [trainingset,   trainings_targets]  = partition_dataset(1, training_set_size);
    [validationset, validation_targets] = partition_dataset(training_set_size + 1, ...
                                                            training_set_size + validation_set_size);

    [testset, test_targets]             = partition_dataset(training_set_size + validation_set_size + 1, ...
                                                            training_set_size + validation_set_size + test_set_size);



    % Initialize weights for all neurons
    w_ij = w_initializer([no_inputs, no_hidden], 1);
    w_jk = w_initializer([no_hidden, no_outputs], 1);

    threshold_hidden = w_initializer([1, no_hidden], 2);
    threshold_outputs = w_initializer([1, no_outputs], 2);

    y_hidden = zeros(1, no_hidden);
    y_output = zeros(1, no_outputs);

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


    errors = zeros(1, epochs);
    validations = zeros(1, epochs);
    epoch_errors = zeros(1, training_set_size);

    if debug
        tic;
        fprintf('Running %d epochs over trainingset size %d,\nhidden neurons: %d,\n', ...
                epochs, training_set_size, no_hidden);

        figure

        subplot(2, 1, 1);
        w_ij_plt = imagesc(w_ij);
        title('Hidden layer');

        colormap(jet(10));
        colorbar('location', 'eastoutside');
        xlabel('hidden neuron');
        ylabel('input neuron');

        subplot(2, 1, 2);
        w_jk_plt = imagesc(w_jk);
        title('Output layer');

        colormap(jet(10))
        colorbar('location', 'eastoutside');
        xlabel('output neuron');
        ylabel('hidden neuron');
    end

    % training
    for epoch = 1:epochs
        % iterate over training set.
        for current = 1:training_set_size

            % forward phase
            [y_hidden, y_output] = forward(trainingset(current, :));

            % backward phase

            % calculate output error
            e = trainings_targets(current, :) - y_output;
            epoch_errors(current) = sum(e .^ 2);

            e_gradient_output = y_output .* (1 - y_output) .* e;

            % y * (1 - y) * sum(of each  (e_gradient_output * w_hidden))
            e_gradient_hidden = zeros(1, no_hidden);
            for j = 1:no_hidden
                e_gradient_hidden(j) = y_hidden(j) .* (1 - y_hidden(j)) * ...
                                       sum(e_gradient_output .* w_jk(j, :));
            end

            % calculate deltas
            d_threshold_outputs = learning_rate .* (-1)                     .* e_gradient_output;
            d_threshold_hidden  = learning_rate .* (-1)                     .* e_gradient_hidden;
            d_weight_jk         = learning_rate  * (y_hidden'                * e_gradient_output);
            d_weight_ij         = learning_rate  * (trainingset(current, :)' * e_gradient_hidden);

            % update weights
            w_ij = w_ij + d_weight_ij;
            w_jk = w_jk + d_weight_jk;

            % adjust thresholds
            threshold_outputs = threshold_outputs + d_threshold_outputs;
            threshold_hidden = threshold_hidden + d_threshold_hidden;
        end

        errors(epoch) = mean(epoch_errors);

        % adjust learning rate
        % if epoch > 1
        %     if errors(epoch) < errors(epoch - 1)
        %         learning_rate = learning_rate * 1.2;
        %     else
        %         learning_rate = learning_rate / 1.3;
        %     end
        % end

        % Stop conditions
        if errors(epoch) < mse_threshold
            fprintf('MSE < %f, quitting.\n', mse_threshold);
            break;
        end
         if epoch > 3
            if errors(epoch) > errors(epoch - 1) && errors(epoch - 1) > errors(epoch - 2)
                fprintf('MSE in trainingsset increasing for two epochs, quitting training...');
                break;
            end

            if validations(epoch) > validations(epoch)
                fprintf('MSE in validationset increasing, quitting training...');
            end
        end

        % Validation;
        epoch_validations = zeros(1, validation_set_size);
        for current = 1:validation_set_size
            validationset(current, :);
            [~, y_output] = forward(validationset(current, :));
            e = validation_targets(current, :) - y_output;
            epoch_validations(current) = sum(e .* e);
        end
        validations(epoch) = mean(epoch_validations);

        if debug
            % update weight plot
            set(w_jk_plt, 'CData', w_jk);
            set(w_ij_plt, 'CData', w_ij);
            drawnow;


            if epochs > 2 && mod(epoch, epochs / 10) == 0
                elapsed = toc;

                fprintf('Epoch #%d, elapsed: %0.1fs, training: %0.6f, %0.6f \n', epoch, elapsed, errors(epoch), validations(epoch));

                if epoch == epochs / 10
                    fprintf('  epoch 1-%d took %0.1fs, done in about %0.1fmin\n', ...
                            epoch, elapsed, (elapsed * 9) / 60);
                end
                tic;
            end
        end
    end


    % pass a reference to the forward function
    function Y = forward_single_output(feature)
       [~, Y] = forward(feature);
    end

    function c = classify_category(feature)
        [~, c] = max(forward_single_output(feature));
    end

    classify = @forward_single_output;

    if debug
        tic
    end

    success = 0;
    actuals = zeros(test_set_size, no_outputs);
    for i = 1:test_set_size
        actual = classify_category(testset(i, :));
        actuals(i, actual) = 1;

        [~, expected] = max(test_targets(i, :));

        if actual == expected
           success = success + 1;
        end
    end
    success_rate = success / test_set_size;

    if debug
        fprintf('\nTesting time: %2.2fs.\n', toc);

        figure
        plotconfusion(test_targets', actuals')

        title(sprintf('Confusion matrix (testset) %d epochs, training set: %d, hidden neurons: %d', ...
                      epoch, training_set_size, no_hidden));

        filename = sprintf('output/confusion-matrix-h%d-e%d-t%d', no_hidden, epoch, training_set_size);
        print(strcat(filename, '.eps'), '-depsc');
        print(strcat(filename, '.png'), '-dpng', '-r300');

        fprintf('Number of epochs:    %4d, training elements: %4d \n', epoch, training_set_size);
        fprintf('Number of tests:     %4d, hidden neurons:    %4d \n', test_set_size, no_hidden);
        fprintf('Number of successes: %4d, success rate:      %2.2f\n\n', success, success_rate);
    end

    unknown = dlmread('data/unknown.txt');
    classified = zeros(1, length(unknown));
    for i = 1:length(unknown)
        classified(1, i) = classify_category(unknown(i, :));
    end

    dlmwrite(sprintf('output/5_classes_%0.4f.txt', success_rate), classified');

    % Make a plot
    if debug || true
        figure
        semilogy(1:length(errors), errors, 'b', 1:length(validations), validations, 'r');
        title(sprintf('Learning curve %d epochs, training set: %d, hidden neurons: %d', ...
                      epoch, training_set_size, no_hidden));

        xlabel('epochs');
        ylabel('mean squared error');
        legend('Training', 'Validation')

        filename = sprintf('output/learning_curve-%0.4f.eps', success_rate);
        print(filename, '-depsc');
    end
end
