#ifndef CLUSTERED_NETLIST_FWD_H
#define CLUSTERED_NETLIST_FWD_H
#include "vtr_strong_id.h"
#include "base_netlist_fwd.h"


//Type tags for Ids
struct cluster_block_id_tag;
struct cluster_net_id_tag;
struct cluster_port_id_tag;
struct cluster_pin_id_tag;

//A unique identifier for a block/primitive in the atom netlist
typedef vtr::StrongId<cluster_block_id_tag> ClusterBlockId;

//A unique identifier for a net in the atom netlist
typedef vtr::StrongId<cluster_net_id_tag> ClusterNetId;

//A unique identifier for a port in the atom netlist
typedef vtr::StrongId<cluster_port_id_tag> ClusterPortId;

//A unique identifier for a pin in the atom netlist
typedef vtr::StrongId<cluster_pin_id_tag> ClusterPinId;

#endif