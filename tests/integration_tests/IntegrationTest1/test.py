individuals_file = 'individuals.txt'
a = 0
with open(individuals_file) as f:
    for line in f:
        # Chomp line
        line = line.rstrip()

        # Create the individual as a dictionary
        indiv = {}
        properties = line.split('@')
        for prop in properties:
            key_value = prop.split('=')
            indiv[str(key_value[0])] = key_value[1]
        a = a + 1
        print a
        print indiv

