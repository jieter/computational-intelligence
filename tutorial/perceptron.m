function [ Y ] = perceptron( inputs, weights, threshold)
    if size(inputs, 2) ~= size(weights, 2)
       error('Inputs and weights do not match in size'); 
    end
    
    Y = dot(inputs, weights);
    Y = step(Y - threshold);
end