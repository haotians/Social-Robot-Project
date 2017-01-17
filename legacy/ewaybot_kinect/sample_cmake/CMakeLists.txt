cmake_minimum_required(VERSION 2.8) 
PROJECT (test1)
#=============================================
# OpenGL
find_package(GLUT REQUIRED )
find_package(OpenGL REQUIRED )
#=============================================
# OpenNI library
FIND_PATH(OPEN_NI_INCLUDE "XnOpenNI.h" "OpenNIConfig.h" HINTS "$ENV{OPEN_NI_INCLUDE}" "/usr/include/ni" "/usr/include/openni" "/opt/ros/groovy/include/openni_camera")
FIND_LIBRARY(OPEN_NI_LIBRARY NAMES OpenNI libOpenNI HINTS $ENV{OPEN_NI_LIB} "/usr/lib")
LINK_DIRECTORIES($ENV{OPEN_NI_LIB})
INCLUDE_DIRECTORIES(${OPEN_NI_INCLUDE})
LINK_LIBRARIES(${OPEN_NI_LIBRARY})
#=============================================
# NITE library
#FIND_PATH(XN_NITE_INCLUDE "libXnVNite.so" HINTS "$ENV{XN_NITE_INSTALL_PATH}" "/usr/include/nite")
#FIND_LIBRARY(XN_NITE_LIBRARY NAMES libXnVNite_1_5_2.so HINTS $ENV{XN_NITE_INSTALL_PATH} "/usr/lib")
#LINK_DIRECTORIES($ENV{XN_NITE_LIB_INSTALL_PATH} "/usr/lib")
#INCLUDE_DIRECTORIES(${XN_NITE_INCLUDE})
#LINK_LIBRARIES(${XN_NITE_LIBRARY})
#===========================================
# source
set( NAME_SRC
    src/NiSimpleViewer.cpp    
)

set( NAME_HEADERS       
#     include/header.h
#	glh/*.h
)
#============================================
# header
find_path(OPENNI_INCLUDE_PATH XnCppWrapper.h)
INCLUDE_DIRECTORIES( ${CMAKE_CURRENT_SOURCE_DIR}/include 
			${OPENGL_INCLUDE_DIR}
			${OPENNI_INCLUDE_DIR} 
			#/home/jw/Desktop/openni/NiSimpleViewer/GL
			#/home/jw/Desktop/openni/NiSimpleViewer/glh
			#/home/jw/Desktop/openni/OpenNI-master/Include
			#find_path(OPENNI_INCLUDE_PATH XnCppWrapper.h)
			)
#INCLUDE_DIRECTORIES(${OPENGL_INCLUDE_DIR})
#==============================================================================
# compile and linking
link_directories( ${CMAKE_BINARY_DIR}/bin)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)

add_executable( test1 ${NAME_SRC} ${NAME_HEADERS} )

target_link_libraries( test1 ${OPENGL_LIBRARIES} ${GLUT_LIBRARIES} ${OPENNI_LIBRARIES})
