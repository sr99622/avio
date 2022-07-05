cmake_minimum_required(VERSION 3.17)

project(avio)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "-D__STDC_CONSTANT_MACROS")
if (WIN32)
    add_compile_options("/EHsc")
endif()
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

if (FFMPEG_INCLUDE_DIRS AND FFMPEG_LIBRARIES)
    message("-- FFmpeg is using include dirs ${FFMPEG_INCLUDE_DIRS} and libs ${FFMPEG_LIBRARIES}")
else()
    find_package(FFmpeg)
    if (FFMPEG_INCLUDE_DIRS)
        message("-- Found FFmpeg Include Directories ${FFMPEG_INCLUDE_DIRS}")
    else()    
        message("-- **WARNING** Unable to find FFmpeg Include Directories automatically.  Use -DFFMPEG_INCLUDE_DIRS location manually")
    endif()
    if (FFMPEG_LIBRARIES)
        message("-- Found FFmpeg Libraries ${FFMPEG_LIBRARIES}")
    else()    
        message("-- **WARNING** Unable to find FFmpeg Libraries automatically.  Use -DFFMPEG_LIBRARIES to set location manually")
    endif()
endif()

if (SDL2_LIBRARIES AND SDL2_INCLUDE_DIRS)
    message("-- SDL2 is using include dirs ${SDL2_INCLUDE_DIRS} and lib ${SDL2_LIBRARIES}")
else()
    find_package(SDL2)
    if (SDL2_FOUND)
        set(SDL2_LIBRARIES SDL2::SDL2)
        message("-- Found SDL2: ${SDL2_INCLUDE_DIRS}")
    else()
        message("-- **WARNING** Unable to find SDL2 automatically.  Use -DSDL2_INCLUDE_DIRS and -DSDL2_LIBRARIES to set locations manually")
    endif()
endif()

find_package(SDL2_ttf)

if (FREETYPE_LIBRARIES)
    message("-- Freetype is using ${FREETYPE_LIBRARIES}")
else()
    find_package(Freetype)
    if (NOT FREETYPE_FOUND)
        find_library(FREETYPE_LIBRARIES NAME freetype
            HINTS
                $ENV{CONDA_PREFIX}/lib
        )
        if (FREETYPE_LIBRARIES)
            message("-- Found FreeType library ${FREETYPE_LIBRARIES}")
        else()
            message("-- **WARNING** Unable to find FreeType automatically.  Use -DFREETYPE_LIBRARIES to set lib location manually")
            message("               Alternatively, you can set the environment variable FREETYPE_DIR to the root directory of the")
            message("               Freetype installation")
        endif()
    endif()
endif()

find_package(PNG)

add_subdirectory(pybind11)

if (ZLIB_LIBRARIES)
    message("-- Zlib is using ${ZLIB_LIBRARIES}")
else()
    find_library(ZLIB_LIBRARIES NAME z
        HINTS
            $ENV{CONDA_PREFIX}/lib
    )    
    if (ZLIB_LIBRARIES)
        message("-- Zlib library has been found ${ZLIB_LIBRARIES}")
    else()
        message("-- **WARNING** Unable to find Zlib automatically.  Use -DZLIB_LIBRARIES to set lib location manually")
        message("               Alternatively, you can set the environment variable ZLIB_ROOT to the root directory of the")
        message("               Zlib installation")
    endif()
endif()

if (PNG_LIBRARIES)
    message("-- PNG is using ${PNG_LIBRARIES}")
else()
    find_library(PNG_LIBRARIES NAME z
        HINTS
            $ENV{CONDA_PREFIX}/lib
    )
    if (PNG_LIBRARIES)
        message("-- PNG Library has been found ${PNG_LIBRARIES}")
    else()
        message("-- **WARNING** Unable to find PNG automatically.  Use -DPNG_LIBRARIES to set lib location manually")
    endif()
endif()

if (Python_INCLUDE_DIRS AND Python_LIBRARIES AND Python_NumPy_INCLUDE_DIRS)
    message(-- "Python is using include dirs ${Python_INCLUDE_DIRS} and lib ${Python_LIBRARIES}, Numpy is using ${Python_NumPy_INCLUDE_DIRS}")
else()
    if (WIN32)
	    find_package(Python COMPONENTS Interpreter Development)
    else ()
	    find_package(Python COMPONENTS Interpreter Development NumPy)
    endif()
    if (Python_LIBRARIES)
    	message("-- Python Libraries Found")
    else()
        if (UNIX)
    	    get_filename_component(Python_EXE $ENV{CONDA_PYTHON_EXE} REALPATH)
    	    get_filename_component(Python_VER ${Python_EXE} NAME)
    	    if (EXISTS "$ENV{CONDA_PREFIX}/lib/lib${Python_VER}.so")
	        message("-- Found Python Libraries")
	        set(Python_LIBRARIES $ENV{CONDA_PREFIX}/lib/lib${Python_VER}.so)
            else()
               message("-- **WARNING** Unable to find Python Libraries.  Use -DPython_LIBRARIES to set location manually")
            endif()
        endif()
    endif()
    if (Python_INCLUDE_DIRS)
    	message("-- Python Include Directories Found")
    else()
        if (UNIX)
    	    get_filename_component(Python_EXE $ENV{CONDA_PYTHON_EXE} REALPATH)
    	    get_filename_component(Python_VER ${Python_EXE} NAME)
    	    if (EXISTS "$ENV{CONDA_PREFIX}/include/${Python_VER}")
	        message("-- Found Python Include Directories")
	        set(Python_INCLUDE_DIRS $ENV{CONDA_PREFIX}/include/${Python_VER})
            else()
               message("-- **WARNING** Unable to find Python Include Directories.  Use -DPython_INCLUDE_DIRS to set location manually")
            endif()
        endif()
    endif()
    if (Python_NumPy_INCLUDE_DIRS)
        message("-- Found NumPy")        
    else()
#    	message("CMAKE_SYSTEM ${CMAKE_SYSTEM}  CMAKE_SYSTEM_NAME ${CMAKE_SYSTEM_NAME}")
    	if (UNIX)
    	    get_filename_component(Python_EXE $ENV{CONDA_PYTHON_EXE} REALPATH)
    	    get_filename_component(Python_VER ${Python_EXE} NAME)
    	    if (EXISTS "$ENV{CONDA_PREFIX}/lib/${Python_VER}/site-packages/numpy/core/include")
	        message("-- Found NumPy Include Directories")
	        set(Python_NumPy_INCLUDE_DIRS $ENV{CONDA_PREFIX}/lib/${Python_VER}/site-packages/numpy/core/include)
            else()
               message("-- **WARNING** Unable to find NumPy Include Directories.  Use -DPython_NumPy_INCLUDE_DIRS to set location manually")
            endif()
        endif()
    endif()
endif()

pybind11_add_module(avio 
                        src/avio.cpp
                        src/Reader.cpp
                        src/Exception.cpp
                        src/Event.cpp
                        src/Frame.cpp
                        src/Decoder.cpp
                        src/Filter.cpp
                        src/Clock.cpp
                        src/Display.cpp
                        src/Hud.cpp
                        src/Gui.cpp
                        src/Encoder.cpp
                        src/Writer.cpp
                        src/Pipe.cpp
                        src/PyRunner.cpp
                    )
                
target_link_libraries(avio PRIVATE 
                ${Python_LIBRARIES}
                ${FFMPEG_LIBRARIES}
                ${SDL2_LIBRARIES}
                ${SDL2_TTF_LIBRARIES}
                ${FREETYPE_LIBRARIES}
                ${PNG_LIBRARIES}
                ${ZLIB_LIBRARIES}
             )

target_include_directories(avio PUBLIC
                    include
                    ${Python3_INCLUDE_DIRS}
                    ${Python_NumPy_INCLUDE_DIRS}
                    ${FFMPEG_INCLUDE_DIRS}
                    ${SDL2_INCLUDE_DIRS}
                    ${SDL2_TTF_INCLUDE_DIRS}
                  )

