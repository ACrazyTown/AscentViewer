#!/bin/bash

# AscentViewer, a Python image viewer.
# Copyright (C) 2020-2021 DespawnedDiamond, A Crazy Town and other contributors
#
# This file is part of AscentViewer.
#
# AscentViewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AscentViewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AscentViewer.  If not, see <https://www.gnu.org/licenses/>.

# =====================================================
# Thank you for using and/or checking out AscentViewer!
# =====================================================

# thanks to
# https://linuxize.com/post/bash-comments/
# and https://stackoverflow.com/questions/3349105/how-can-i-set-the-current-working-directory-to-the-directory-of-the-script-in-ba
# and https://stackoverflow.com/questions/592620/how-can-i-check-if-a-program-exists-from-a-bash-script
# and https://stackoverflow.com/questions/8967902/why-do-you-need-to-put-bin-bash-at-the-beginning-of-a-script-file

cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found, please make sure python3 is in PATH"
else
    python3 ./AscentViewer
fi
