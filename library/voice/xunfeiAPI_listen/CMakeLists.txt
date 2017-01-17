cmake_minimum_required(VERSION 2.8) 
PROJECT (asr)
#=============================================
# OpenGL
find_package(Threads REQUIRED)


#===========================================

set( XUNFEI_LIB    
		${CMAKE_CURRENT_SOURCE_DIR}/lib/libmsc.so  
)
#LINK_LIBRARIES(${XUNFEI_LIB})
#===========================================
# source
set( NAME_SRC    
		src/vsr.cpp   
)

set( NAME_HEADERS       

)
#============================================
# header

INCLUDE_DIRECTORIES( ${CMAKE_CURRENT_SOURCE_DIR}/include 
			)

#==============================================================================
# compile and linking
add_definitions( "-ldl -lrt -lpthread -lm -lmsc" )



link_directories( ${CMAKE_BINARY_DIR}/bin)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)

# add shared object .so
#ADD_LIBRARY( test2 SHARED ${NAME_SRC} ${NAME_HEADERS}  ${CMAKE_HELPER_FILES} )
#target_link_libraries( test2 ${OPENGL_LIBRARIES} ${GLUT_LIBRARIES} ${OPENNI_LIBRARIES} ${XN_NITE_LIBRARY})

# add binary
add_executable( asr ${NAME_SRC} ${NAME_HEADERS} )
# target_link_libraries( test1 ${XUNFEI_LIB} )

#SET(CMAKE_CXX_LINK_EXECUTABLE asr)
target_link_libraries(asr ${XUNFEI_LIB} ${CMAKE_DL_LIBS} ${CMAKE_THREAD_LIBS_INIT} )
#endif()

