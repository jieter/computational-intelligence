clear validation fout class MAX hidden_layer output
Validation_set = A(5001:7000,:);
Validation_targets = B(5001:7000);


for i = 1:length(Validation_set)
    for j = 1:hidden_neurons
        weight = wij(j,:);
        weighted_sum_ij(j) = sum(A(i,:).*weight);
    end
    hidden_layer(i,:) = 1./(1 + exp(-(weighted_sum_ij - treshold_hl)));
    
        for j = 1:7
        weight = wjk(j,:);
        weighted_sum_jk(j) = sum(hidden_layer(i,:) .* weight);
        end
        
        output(i,:) = 1./(1 + exp(-(weighted_sum_jk - treshold_ol)));

end

class = zeros(1,length(Validation_set));

 MAX = max(output');
    for m = 1:length(Validation_set);
    class(m) = find(output(m,:) == MAX(m));
    end
    validation = class' - B(1:length(class));
    fout = nnz(validation)
    
   