
epochs = 10;
no_tries = 4;

fprintf('Make error plot for range of hidden neurons and %d tries.\n', no_tries);

data = zeros(30, no_tries);
for hidden_neurons = 7:10
    for i = 1:no_tries
        fprintf('Test hidden: %d, epochs: %d, try: %d\n', hidden_neurons, epochs, i);
            
        [errors, success_rate] = jieter_test(hidden_neurons, epochs, false);
        data(hidden_neurons, i) = success_rate;
    end
end

errorplot(data);