#!/bin/bash
#
# Author: scottakirkwood@gmail.com (scottkirkwood))
unzip -o $1 content.xml
tidy -xml -indent content.xml > content-clean.xml 2> /dev/null
rm content.xml
mv content-clean.xml content.xml
