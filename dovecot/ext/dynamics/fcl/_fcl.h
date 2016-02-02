
#ifndef _FCL_H_
#define _FCL_H_

#include <vector>
#include "fcl/broadphase/broadphase.h"

/// @brief Collision data stores the collision request and the result given by collision algorithm.
struct CollisionData
{
  CollisionData() {};

  std::vector<int> key1;
  std::vector<int> key2;

  // /// @brief Collision request
  // fcl::CollisionRequest request;

  // /// @brief Collision result
  // fcl::CollisionResult result;

  // /// @brief Whether the collision iteration can stop
  // bool done;
};


class KeyObject {
public:
    KeyObject(int key_) {
            this->key = key_;
        }

    int key;

};


class PyFCL
{
public:

    /** Initialization constructor. */
    PyFCL();
    ~PyFCL();

    /** Reset */
    void reset();

    /** Add a sphere to the collision group.
     *  \param[in] radius          radius of the sphere
     *  \param[in] tx, ty, tz      translation
     *  \param[in] q0, q1, q2, q3  quaternion
     */
    int add_sphere_quat(double radius,
                       double tx, double ty, double tz,
                       double q0, double q1, double q2, double q3);

    int add_box_quat(double x, double y, double z,
                     double tx, double ty, double tz,
                     double q0, double q1, double q2, double q3);

    /** Compute collision */
    void collide();

    /** Return the number of collisions **/
    int collision_count();

    /* return first and second list of elements colliding */
    std::vector<int> get_first_keys();
    std::vector<int> get_second_keys();

private:
    // std::vector<KeyObject*> key_objects;
    std::vector<fcl::CollisionObject*> col_objects;
    CollisionData* collision_data;
    fcl::DynamicAABBTreeCollisionManager* manager;

};

#endif // _FCL_H_
