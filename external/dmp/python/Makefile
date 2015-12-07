CPPFLAGS = -I./ -I/home/fbenurea/prefix/include -Wall $(shell python-config --cflags) -fPIC
OBJS = main.o src/dmp/demos/pydmp.o GenericList.o

OS = $(shell uname -s)

V = 1
CXX_0 = @echo "Compiling $<..."; $(CXX)
CXX_1 = $(CXX)
CXX_V = $(CXX_$(V))
BOOST_DIR = /usr/local

ECHO=@

ifeq ($(OS), Linux)
	OPTION = -shared
	EXT = so
	CPPFLAGS += -I$(shell echo $(BOOST_DIR))/include
	LDFLAGS = -L$(shell python-config --prefix)/lib $(shell python-config --ldflags) -L$(shell echo $(BOOST_DIR))/lib -lboost_python -lfcl
else
	CPPFLAGS += -I$(shell echo $(BOOST_DIR))/include
	LDFLAGS += $(shell python-config --ldflags) -L$(shell python-config --prefix)/lib -lpython $(shell echo $(BOOST_DIR))/lib/libboost_python.a -lboost_system -lboost_filesystem -lboost_serialization -ldmp -lfunctionapproximators -ldynamicalsystems
	OPTION = -dynamiclib -current_version 1.0
	EXT = so

endif

TARGET = pydmp.$(EXT)

all: pyfcl

pyfcl: $(OBJS)
		$(CXX_V) $(CPPFLAGS) $(OBJS) $(STATIC_LIBS) $(OBJS_ADDITIONAL) $(OPTION) -o $(TARGET) $(LDFLAGS)

%.o: %.c
		$(CXX_V) $(CPPFLAGS) -c $< -o $@

%.o: %.cpp
		$(CXX_V) $(CPPFLAGS) -c $< -o $@

_%.o: _%.cpp
		$(CXX_V) $(CPPFLAGS) -c $< -o $@

clean:
		rm -rf $(OBJS) $(TARGET)
