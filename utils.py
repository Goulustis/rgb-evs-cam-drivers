def read_bias(file_path):
    bias_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            value, key = line.split('%')
            bias_dict[key.strip()] = int(value.strip())
    return bias_dict

def set_all_biases(i_ll_bias, biases:dict):
    for k, v in biases.items():
        i_ll_bias.set(k, v)


def write_bias(bias_dict, file_path):
    """
    Writes a dictionary to a file in a specific format.
    
    :param bias_dict: Dictionary containing bias configuration.
    :param file_path: Path to the file where the data will be written.
    """
    with open(file_path, 'w') as file:
        for key, value in bias_dict.items():
            file.write(f"{value:3}   % {key}\n")