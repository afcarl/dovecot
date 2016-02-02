#include <iostream>

#include "fcl/shape/geometric_shapes.h"
#include "fcl/math/vec_3f.h"
#include "fcl/collision_data.h"

#include "_fcl.h"

using namespace std;

#include "fcl/collision.h"

static int keycount = 0;


class SphereKey:public fcl::Sphere, public KeyObject {

public:
    SphereKey(fcl::FCL_REAL radius_, int key_)
        : fcl::Sphere(radius_), KeyObject(key_) {}

};

class BoxKey:public fcl::Box, public KeyObject {

public:
    BoxKey(fcl::FCL_REAL x_, fcl::FCL_REAL y_, fcl::FCL_REAL z_, int key_)
        : fcl::Box(x_, y_, z_), KeyObject(key_) {}

};


PyFCL::PyFCL() {
    keycount = 1;
    manager = new fcl::DynamicAABBTreeCollisionManager();
    collision_data = new CollisionData();
}

PyFCL::~PyFCL() {
    delete collision_data;
    delete manager;
    for (int i = 0; i < col_objects.size(); i++) {
        delete col_objects[i];
    }
}

void PyFCL::reset() {
    keycount = 1;
    if (collision_data != NULL) {
        delete collision_data;
    }
    manager->clear();

    for (int i = 0; i < col_objects.size(); i++) {
        delete col_objects[i];
    }
    col_objects.clear();
    collision_data = new CollisionData();
}

int PyFCL::add_sphere_quat(double radius,
                          double tx, double ty, double tz,
                          double q0, double q1, double q2, double q3)
{
    keycount += 1;
    SphereKey* sphere = new SphereKey(radius, keycount);
    fcl::CollisionObject* obj = new fcl::CollisionObject(boost::shared_ptr<fcl::CollisionGeometry>(sphere), fcl::Transform3f(fcl::Quaternion3f(q0, q1, q2, q3), fcl::Vec3f(tx, ty, tz)));
    ((KeyObject*)obj)->key = keycount;
    manager->registerObject(obj);

    col_objects.push_back(obj);
    return keycount;
}

int PyFCL::add_box_quat(double x, double y, double z,
                        double tx, double ty, double tz,
                        double q0, double q1, double q2, double q3)
{
    keycount += 1;
    BoxKey* box = new BoxKey(x, y, z, keycount);
    fcl::CollisionObject* obj = new fcl::CollisionObject(boost::shared_ptr<fcl::CollisionGeometry>(box), fcl::Transform3f(fcl::Quaternion3f(q0, q1, q2, q3), fcl::Vec3f(tx, ty, tz)));
    ((KeyObject*)obj)->key = keycount;
    manager->registerObject(obj);

    col_objects.push_back(obj);
    return keycount;
}



bool collisionFunction(fcl::CollisionObject* o1, fcl::CollisionObject* o2, void* cdata_)
{
  CollisionData* cdata = static_cast<CollisionData*>(cdata_);
  fcl::CollisionRequest* request = new fcl::CollisionRequest();
  fcl::CollisionResult* result = new fcl::CollisionResult();

  collide(o1, o2, *request, *result);

  if (result->isCollision()) {
    cdata->key1.push_back(((KeyObject*)o1)->key);
    cdata->key2.push_back(((KeyObject*)o2)->key);
  }

  delete request;
  delete result;
  return false;
}


void PyFCL::collide() {
    delete collision_data;
    collision_data = new CollisionData();
    manager->setup();
    manager->collide(collision_data, collisionFunction);

}

int PyFCL::collision_count() {
    return collision_data->key1.size();
}

vector<int> PyFCL::get_first_keys() {
  vector<int> keys;
  for (int i = 0; i < collision_data->key1.size(); i++){
    keys.push_back(collision_data->key1[i]);
  }
  return keys;
}

vector<int> PyFCL::get_second_keys() {
  vector<int> keys;
  for (int i = 0; i < collision_data->key2.size(); i++)
    keys.push_back(collision_data->key2[i]);
  return keys;
}
