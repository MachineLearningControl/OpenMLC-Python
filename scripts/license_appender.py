# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
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

import os
import shutil
import sys
from random import randint

if len(sys.argv[1]) != 2:
    print "Root directory must be specified"

license = """# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
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

"""

this_file_name = "license_appender.py"
aux_file_name = "aux_{0}.py".format(randint(0, 1e10))
copy = False
for root, directories, filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        if (not ".pyc" in filename
            and filename != "__init__.py"
            and ".py" in filename
            and not this_file_name in filename):
            with open(aux_file_name, "w") as aux:
                with open(os.path.join(root, filename), "r") as f:
                    content = f.read()
                    content_splitted = [line + '\n' for line in content.split('\n')]
                    # Check if there is a shebang in the beggining of the file
                    if content_splitted[0].startswith('#!'):
                        content = ''.join(content_splitted[1:])
                        aux.write(content_splitted[0])
                    # Check  if the license is already in the file
                    if not license in content:
                        aux.write(license)
                        aux.write(content)
                        copy = True
            if copy:
                shutil.copyfile(aux_file_name, os.path.join(root, filename))
            os.remove(aux_file_name)
