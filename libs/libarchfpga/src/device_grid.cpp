#include "device_grid.h"

///@brief comparison operator to compare 2 grids based on the given dimension
struct gridDimComp {
    // The dimension to compare
    int dim_;
    // Whether to compare in ascending or descending order
    bool is_greater_;
    gridDimComp(int dim, bool is_greater)
        : dim_(dim)
        , is_greater_(is_greater) {}

    bool operator()(const vtr::Matrix<t_grid_tile>& lhs, const vtr::Matrix<t_grid_tile>& rhs) {
        return is_greater_ ? lhs.dim_size(dim_) > rhs.dim_size(dim_) : lhs.dim_size(dim_) < rhs.dim_size(dim_);
    }
};

DeviceGrid::DeviceGrid(std::string grid_name, vtr::NdMatrix<t_grid_tile, 3> grid)
    : name_(grid_name)
    , grid_(grid) {
    count_instances();
}

DeviceGrid::DeviceGrid(std::string grid_name, vtr::NdMatrix<t_grid_tile, 3> grid, std::vector<t_logical_block_type_ptr> limiting_res)
    : DeviceGrid(grid_name, grid) {
    limiting_resources_ = limiting_res;
}

size_t DeviceGrid::num_instances(t_physical_tile_type_ptr type, int layer_num) const {
    size_t count = 0;
    if (instance_counts_.size() == 0) {
        //No instances counted
        return count;
    }

    int num_layers = (int)grid_.size();

    if (layer_num == -1) {
        //Count all layers
        for (int curr_layer_num = 0; curr_layer_num < num_layers; ++curr_layer_num) {
            auto iter = instance_counts_[curr_layer_num].find(type);
            if (iter != instance_counts_[curr_layer_num].end()) {
                count += iter->second;
            }
        }
        return count;
    } else {
        auto iter = instance_counts_[layer_num].find(type);
        if (iter != instance_counts_[layer_num].end()) {
            //Return count
            count = iter->second;
        }
    }

    return count;
}

void DeviceGrid::clear() {
    grid_.clear();
    instance_counts_.clear();
}

void DeviceGrid::count_instances() {
    int num_layers = (int)grid_.size();
    instance_counts_.clear();
    instance_counts_.resize(num_layers);

    //Count the number of blocks in the grid
    for (int layer_num = 0; layer_num < num_layers; ++layer_num) {
        for (size_t x = 0; x < width(); ++x) {
            for (size_t y = 0; y < height(); ++y) {
                auto type = grid_[layer_num][x][y].type;

                if (grid_[layer_num][x][y].width_offset == 0 && grid_[layer_num][x][y].height_offset == 0) {
                    //Add capacity only if this is the root location
                    instance_counts_[layer_num][type] += type->capacity;
                }
            }
        }
    }
}
