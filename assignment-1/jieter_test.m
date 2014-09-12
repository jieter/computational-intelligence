% TI2730B computational intelligence
%
% Jan Pieter Waagmeester

% Settings
no_inputs = 2;
no_hidden = 3;
no_outputs = 2;

epochs = 10; 
learning_rate = 0.1;

activation = @(x)(1 / (1 + exp(-x)));

% Initializer function to assign random weights between -1 ... 1
w_initializer = @(L)(-1 + 2 .* rand(L));

% try with xor.
features = [0, 0; 0, 1; 1, 0; 1, 1];
targets = [0, 1; 1, 0; 1, 0; 0, 1];

% Read data
%features = dlmread('data/features.txt');
%target_raw = dlmread('data/targets.txt');

% Select only a part of the input set while testing.
%test_len = 500;
%features = features(1:test_len,:);
%target_raw = target_raw(1:test_len,:);

% Translate the nx1 size matrix to an nx(range) matrix
% with ones on the position for the expected output.
% Each row correspondents with the expected output vector.
%targets = zeros(size(target_raw, 1), no_outputs);
%for i=1:size(target_raw, 1)
%   targets(i, target_raw(i)) = 1;
%end

% Initialize weights for all neurons
w_inputs = w_initializer([no_hidden, no_inputs]);
w_hidden = w_initializer([no_outputs, no_hidden]);

threshold_hidden = w_initializer([1, no_hidden]);
threshold_outputs = w_initializer([1, no_outputs]);

% training
for epoch = 1:epochs
    
    % iterate over training set.
    for i = 1:size(features, 2)
        
    %%%%% forward phase
    
        y_hidden = zeros(1, no_hidden);
        for hidden = 1:no_hidden
            X = dot(features(i, :), w_inputs(hidden, :));
            y_hidden(hidden) = activation(X - threshold_hidden(hidden));
        end
    
        y_output = zeros(1, no_outputs);
        for output = 1:no_outputs
           X = dot(y_hidden, transpose(w_hidden(output, :)));
           y_output(output) = activation(X - threshold_outputs(output));
        end
        
    %%%%% backward phase
        
        % calculate output error
        e = targets(i, :) - y_output;
        
        e_gradient_output = y_output .* (1 - y_output) .* e;
   
        % y * (1 - y) * sum(of each  (e_gradient_output * w_hidden))
        % TODO
        e_gradient_hidden = zeros(1, no_hidden);
        for hidden = 1:no_hidden
            e_gradient_hidden(1, hidden) = y_hidden(hidden) * (1 - y_hidden(hidden)) * ...
            sum(e_gradient_output * w_hidden(:, hidden));
        end
        
        % calculate delta's
        d_threshold_outputs = learning_rate .* (-1)           .* e_gradient_output;
        d_weight_hidden     = learning_rate .* y_output       .* e_gradient_output;
        %d_weight_input      = learning_rate .* features(i, :) .* e_gradient_hidden;
        
        % adjust weights for the connenection between hidden and output layers.
        for output = 1:no_outputs
            w_hidden(output,:) = w_hidden(output,:) + d_weight_hidden;
        end
        % adjust output thresholds
        threshold_outputs = threshold_outputs + d_threshold_outputs;
        
        % adjust hidden thresholds:
   
        % TODO
        
        % adjust input weights
        % TODO
        
    end

end