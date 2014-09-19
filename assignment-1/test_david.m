clear validation fout class MAX hidden_layer output

test_set = test_set;


for i = 1:length(test_set)
    for j = 1:hidden_neurons
        weight = wij(j,:);
        weighted_sum_ij(j) = sum(test_set(i,:).*weight);
    end
    hidden_layer(i,:) = 1./(1 + exp(-(weighted_sum_ij - treshold_hl(:,:))));
    
        for j = 1:7
        weight = wjk(j,:);
        weighted_sum_jk(j) = sum(hidden_layer(i,:) .* weight);
        end
        
        output(i,:) = 1./(1 + exp(-(weighted_sum_jk - treshold_ol(:,:))));
end


class = zeros(1,length(test_set));

class = vec2ind(output');
    validation = class' - test_B;
    test_prestatie = 1 - nnz(validation)/length(test_B);
    
    
   