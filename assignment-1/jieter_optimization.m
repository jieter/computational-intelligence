
epochs = 100;
no_tries = 10;
min_hidden_neurons = 7;
step = 3;
max_hidden_neurons = 30;

% margin for y axis
margin = 0.002;


fprintf('Make error plot for range of hidden neurons and %d tries, %d epochs.\n', no_tries, epochs);

data = zeros(no_tries, max_hidden_neurons);
for hidden_neurons = min_hidden_neurons:step:max_hidden_neurons
    fprintf('Test with %d hidden neurons: ', hidden_neurons);
    for i = 1:no_tries

        [errors, success_rate] = jieter_test(hidden_neurons, epochs, false);
        data(i, hidden_neurons) = success_rate;
        fprintf('.');
    end
    fprintf('\n');
end

% Make boxplot
hold on;

plot(7:30, mean(data(:, 7:30)), ':b')

boxplot(data);

xlim([min_hidden_neurons - 0.9, max_hidden_neurons + 0.9]);
ylim([min(data(find(data))) * (1 - margin), max(max(data)) * (1 + margin)]);

title('Success rate with different number of hidden neurons, trained for 50 epochs.');
xlabel('Number of hidden neurons');
ylabel('Success rate');
legend('mean');

% Save to file
filename = sprintf('plots/boxplot-tries%d-e%d-h%d-%d', no_tries, epochs, min_hidden_neurons, max_hidden_neurons);
print(strcat(filename, '.eps'), '-depsc');
print(strcat(filename, '.png'), '-dpng', '-r300');
hold off;
