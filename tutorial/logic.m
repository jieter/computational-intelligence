function [] = logic(weights, threshold)
    logic_table = [[0, 0]; [1, 0]; [0, 1]; [1, 1]];
    
    disp(sprintf('Logic table for perceptron with weights %0.2f, %0.2f; threshold: %0.2f', weights, threshold))
    for i=1:size(logic_table, 1)
        row = logic_table(i, :);
        Y = perceptron(row, weights, threshold);
        
        disp(sprintf('%d, %d: %d', row, Y));
    end
end
