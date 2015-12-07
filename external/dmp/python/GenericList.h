#ifndef GENERIC_LIST
#define GENERIC_LIST

#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/extract.hpp>
#define G_LIST boost::python::list

class GenericList{
public:

	GenericList(G_LIST list);

	GenericList();

	~GenericList();

	void clear();

	unsigned int size();

	double readDouble(unsigned int position);

	void appendDouble(double d);

	int readInt(unsigned int position);

	void appendInt(int i);

	float readFloat(unsigned int position);

	void appendFloat(float f);

	G_LIST list(){ return this->_list; };

private:
	G_LIST _list;/*!< the GenericList */
};

#endif /* GENERIC_LIST */