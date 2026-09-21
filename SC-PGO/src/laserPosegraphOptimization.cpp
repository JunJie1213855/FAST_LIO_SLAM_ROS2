#include <memory>

#include <rclcpp/rclcpp.hpp>

#include "sc_pgo/sc_pgo_node.hpp"

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SCPGONode>();

    rclcpp::spin(node);
    rclcpp::shutdown();

    return 0;
}
