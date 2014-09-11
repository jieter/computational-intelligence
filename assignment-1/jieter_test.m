% TI2730B computational intelligence
%
% Jan Pieter Waagmeester

% Settings
no_inputs = 10;
no_hidden = 10;
no_outputs = 7;

epochs = 10; 
learning_rate = 0.1;

activation = @(x)(1 / (1 + exp(-x)));

% Initializer function to assign random weights
w_initializer = @(L)(-1 + 2 .* rand(L));

% Read data
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

% Initialize weights for all neurons
w_inputs = w_initializer([no_hidden, no_inputs]);
w_hidden = w_initializer([no_outputs, no_hidden]);

threshold_hidden = w_initializer(no_hidden);
threshold_outputs = w_initializer(no_outputs);

% training
for epoch = 1:epochs
    
    % iterate over training set.
    for i = 1:size(features, 2)
        
        % forward phase
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
        
        % calculate error
        e = targets(i, :) - y_output;
        
        % backward phase
    end

end