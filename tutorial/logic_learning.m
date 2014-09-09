function [errors] = logic_learning(expected, threshold)
    logic_table = [[0, 0]; [1, 0]; [0, 1]; [1, 1]];
   
    % initialize weights with ramdom values between -1 ... 1
    weights = -1 +  2 .* rand(1, size(logic_table, 2));
    learning_rate = 0.1;
    epochs = 20;
    errors = zeros(1, epochs);
    
    
    fprintf('Initial weights: %0.2f, %0.2f; threshold: %0.2f, learning rate: %0.2f, #epochs: %d\n\n', weights, threshold, learning_rate, epochs)
    
    for epoch = 1:epochs
        for i = 1:size(logic_table, 1)
            row = logic_table(i, :);
            Y = perceptron(row, weights, threshold);

            error = expected(i) - Y;
            
            errors(1, epoch) = errors(1, epoch) + error ^ 2;
                    
            weights(1, 1) = weights(1, 1) + learning_rate * row(1, 1) * error;
            weights(1, 2) = weights(1, 2) + learning_rate * row(1, 2) * error;
        end
    end
    
    fprintf('Final weights: %0.2f, %0.2f, final test after %d epochs.\n', weights, epochs);
    
    disp('x1, x2:  out');
    
    for i = 1:size(logic_table, 1)
        row = logic_table(i, :);
        Y = perceptron(row, weights, threshold);
        fprintf(' %d,  %d:    %d \n', row, Y);
    end
end
