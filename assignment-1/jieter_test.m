% TI2730B computational intelligence
%
% Jan Pieter Waagmeester

% Settings
epochs = 10; 
learning_rate = 0.1;

activation = @(x)(1 / (1 + exp(-x)));

% Initializer function to assign random weights between -1 ... 1
w_initializer = @(L)(-1 + 2 .* rand(L));

% Training set
if 1
    % XOR for testing purposes.
    features = [0, 0; 0, 1; 1, 0; 1, 1];
    targets = [0, 1; 1, 0; 1, 0; 0, 1];
else
    % Assignment's training data
    features = dlmread('data/features.txt');
    target_raw = dlmread('data/targets.txt');

    % Select only a part of the input set while testing.
    test_len = 500;
    features = features(1:test_len,:);
    target_raw = target_raw(1:test_len,:);

    % Translate the nx1 size matrix to an nx(range) matrix
    % with ones on the position for the expected output.
    % Each row correspondents with the expected output vector.
    targets = zeros(size(target_raw, 1), no_outputs);
    for i=1:size(target_raw, 1)
        targets(i, target_raw(i)) = 1;
    end
end

no_inputs = size(features, 2);
no_hidden = 3;
no_outputs = size(targets, 2);


% Initialize weights for all neurons
w_ij = w_initializer([no_inputs, no_hidden]);
w_jk = w_initializer([no_hidden, no_outputs]);

threshold_hidden = w_initializer([1, no_hidden]);
threshold_outputs = w_initializer([1, no_outputs]);

% training
for epoch = 1:epochs
    
    % iterate over training set.
    for current = 1:size(features, 2)
        
    %%%%% forward phase
    
        y_hidden = zeros(1, no_hidden);
        for j = 1:no_hidden
            X = dot(features(current, :), w_ij(:, j));
            y_hidden(j) = activation(X - threshold_hidden(j));
        end
    
        y_output = zeros(1, no_outputs);
        for k = 1:no_outputs
           X = dot(y_hidden, transpose(w_jk(:, k)));
           y_output(k) = activation(X - threshold_outputs(k));
        end
        
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
        d_threshold_outputs = learning_rate .* (-1)                 .* e_gradient_output;
        d_weight_jk         = learning_rate .* y_output             .* e_gradient_output;
        d_weight_ij         = learning_rate .* features(current, :) .* e_gradient_hidden;


        % adjust weights for the connenection between hidden and output layers.
%         for k = 1:no_outputs
%             w_jk(:, k) = w_jk(:, k) + d_weight_jk;
%         end
%         % adjust output thresholds
%         threshold_outputs = threshold_outputs + d_threshold_outputs;
%         
%         % adjust hidden thresholds:
%    
%         % TODO
%         
%         % adjust input weights
%         % TODO
        
    end

end