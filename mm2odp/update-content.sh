#!/bin/bash
#
# Author: scottakirkwood@gmail.com (scottkirkwood))
zip -dv $1 content.xml
zip -uv $1 content.xml
