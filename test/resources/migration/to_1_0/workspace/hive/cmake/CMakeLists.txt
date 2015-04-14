
PROJECT( hive )
cmake_minimum_required(VERSION 2.8)

SET(CMAKE_RUNTIME_OUTPUT_DIRECTORY ../bin)
SET(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ../bin)
INCLUDE_DIRECTORIES(../blocks)
INCLUDE_DIRECTORIES(../deps)

# This file has all the variables used in bii_targets.cmake to define the targets
INCLUDE(bii_vars.cmake)


# This file defines the actual targets EXEs, LIBs STATIC and SHARED with their respective
# settings and definitions
INCLUDE(bii_targets.cmake)
