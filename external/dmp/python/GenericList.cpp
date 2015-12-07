#include "GenericList.h"

GenericList::GenericList(G_LIST list){
	this->_list = list;
}

GenericList::GenericList(){
	;
}

GenericList::~GenericList(){
	;
}

void GenericList::clear(){
	unsigned int size = this->size();
	for(unsigned int i = 0 ; i < size ; i++)
		_list.pop();
}

unsigned int GenericList::size(){
	unsigned int size = 0;
	size = boost::python::len(_list);
	return size;
}

void GenericList::appendDouble(double d){
	_list.append(d);
}

double GenericList::readDouble(unsigned int position){
	double d = 0.0;
	d = boost::python::extract<double>(_list[position]);
	return d;
}

void GenericList::appendInt(int i){
	_list.append(i);
}

int GenericList::readInt(unsigned int position){
	int i = 0;
	i = boost::python::extract<int>(_list[position]);
	return i;
}

void GenericList::appendFloat(float f){
	_list.append(f);
}

float GenericList::readFloat(unsigned int position){
	float f = 0.0;
	f = boost::python::extract<float>(_list[position]);
	return f;
}