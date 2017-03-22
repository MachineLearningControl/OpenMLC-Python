# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez (raulopez@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015  Thomas Duriez (thomas.duriez@gmail.com), Adrian Durán (adrianmdu@gmail.com),
# Ezequiel Torres (ezequiel.torresfeyuk@gmail.com), Marco Germano (marco.germano@intraway.com),
# Raul Lopez (raulopez@gmail.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
import numpy as np
import matplotlib.pyplot as plt

# Sine amplitud
A = 1.1
# Offset
Offset = 1.65
f0 = 10
w0 = 2 * np.pi * f0
fs = 1e3

n = np.linspace(0, fs, num=fs)
sinewave = Offset + A * np.cos(w0 * n / fs)

dac_max_value = 4095
dac_min_value = 0
dac_amp_pp = dac_max_value - dac_min_value
min_value = 0.55
max_value = 2.75
amp_pp = max_value - min_value


# Normalization
min_value = Offset - A
sinewave = (sinewave - min_value) * dac_amp_pp / amp_pp + dac_min_value
sinewave = [int(x) for x in sinewave]

fig = plt.figure()
plt.plot(n, sinewave, 'k', linestyle=':')
plt.show(block=True)

output = ""
for i in xrange(int(fs)):
    if i == 0:
        output += "{" + "{0}, ".format(sinewave[i])
    if i == (fs - 1):
        output += "{0}".format(sinewave[i]) + "}"
    else:
        output += "{0}, ".format(sinewave[i])

with open("sinewave.txt", "w") as f:
    f.write(output)
