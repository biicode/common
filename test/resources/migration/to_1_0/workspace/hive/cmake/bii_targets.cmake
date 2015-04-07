#This file is automatically created by biicode.
#Do not modify it, as your changes will be overwritten.


###### Artifact for target phil/hello #######
# This block has executables, not building library

###### Artifact for target phil_hello_main #######
ADD_EXECUTABLE( ${BII_TARGET_phil_hello_main_NAME}
                ${BII_TARGET_phil_hello_main_EXE_TYPE} 
                ${BII_TARGET_phil_hello_main_FILES})
TARGET_LINK_LIBRARIES( ${BII_TARGET_phil_hello_main_NAME} ${BII_TARGET_phil_hello_main_LIBS})
TARGET_LINK_LIBRARIES( ${BII_TARGET_phil_hello_main_NAME} ${BII_TARGET_phil_hello_main_EXTERNAL_LIBS})
SET_TARGET_PROPERTIES(${BII_TARGET_phil_hello_main_NAME} PROPERTIES COMPILE_FLAGS "${BII_TARGET_phil_hello_main_COMPILE_FLAGS}")
SET_TARGET_PROPERTIES(${BII_TARGET_phil_hello_main_NAME} PROPERTIES LINK_FLAGS "${BII_TARGET_phil_hello_main_LINKER_FLAGS}")
INCLUDE_DIRECTORIES(${BII_TARGET_phil_hello_main_INCLUDE_DIRECTORIES})
SET_PROPERTY(TARGET ${BII_TARGET_phil_hello_main_NAME} APPEND_STRING PROPERTY COMPILE_DEFINITIONS "${BII_TARGET_phil_hello_main_COMPILE_DEFINITIONS}")
