#ifndef NO_GRAPHICS
/**
 * @file UI_SETUP.CPP
 * @author Sebastian Lievano
 * @date July 4th, 2022
 * @brief Manages setup for main.ui created buttons
 * 
 * This file contains the various setup functions for all of the ui functions.
 * As of June 2022, gtk ui items are to be created through Glade/main.ui file (see Docs)
 * Each function here initializes a different set of ui buttons, connecting their callback functions
 */

#    include "draw_global.h"
#    include "draw.h"
#    include "draw_toggle_functions.h"
#    include "buttons.h"
#    include "intra_logic_block.h"
#    include "clustered_netlist.h"
#    include "ui_setup.h"
#    include "save_graphics.h"

#    include "ezgl/point.hpp"
#    include "ezgl/application.hpp"
#    include "ezgl/graphics.hpp"
void three_dimension_layers(GtkWidget* widget, gint /*response_id*/, gpointer /*data*/);
void basic_button_setup(ezgl::application* app) {
    //button to enter window_mode, created in main.ui
    GtkButton* window = (GtkButton*)app->get_object("Window");
    gtk_button_set_label(window, "Window");
    g_signal_connect(window, "clicked", G_CALLBACK(toggle_window_mode), app);

    //button to search, created in main.ui
    GtkButton* search = (GtkButton*)app->get_object("Search");
    gtk_button_set_label(search, "Search");
    g_signal_connect(search, "clicked", G_CALLBACK(search_and_highlight), app);

    //button for save graphcis, created in main.ui
    GtkButton* save = (GtkButton*)app->get_object("SaveGraphics");
    g_signal_connect(save, "clicked", G_CALLBACK(save_graphics_dialog_box),
                     app);

    //combo box for search type, created in main.ui
    GObject* search_type = (GObject*)app->get_object("SearchType");
    g_signal_connect(search_type, "changed", G_CALLBACK(search_type_changed), app);
}

/*
 * @brief sets up net related buttons and connects their signals
 * 
 * Sets up the toggle nets combo box, net alpha spin button, and max fanout
 * spin button which are created in main.ui file. Found in Net Settings dropdown
 * @param app ezgl::application ptr
 */
void net_button_setup(ezgl::application* app) {
    //Toggle net signal connection
    GtkComboBoxText* toggle_nets = GTK_COMBO_BOX_TEXT(app->get_object("ToggleNets"));
    g_signal_connect(toggle_nets, "changed", G_CALLBACK(toggle_nets_cbk), app);

    //Manages net alpha
    GtkSpinButton* net_alpha = GTK_SPIN_BUTTON(app->get_object("NetAlpha"));
    g_signal_connect(net_alpha, "value-changed", G_CALLBACK(set_net_alpha_value_cbk), app);
    gtk_spin_button_set_increments(net_alpha, 1, 1);
    gtk_spin_button_set_range(net_alpha, 1, 255);

    //Manages net max fanout
    GtkSpinButton* max_fanout = GTK_SPIN_BUTTON(app->get_object("NetMaxFanout"));
    g_signal_connect(max_fanout, "value-changed", G_CALLBACK(set_net_max_fanout_cbk), app);
    gtk_spin_button_set_increments(max_fanout, 1, 1);
    gtk_spin_button_set_range(max_fanout, 0., (double)get_max_fanout());
}

/*
 * @brief sets up block related buttons, connects their signals
 * 
 * Connects signals and sets init. values for blk internals spin button,
 * blk pin util combo box,placement macros combo box, and noc combo bx created in
 * main.ui. Found in Block Settings dropdown
 * @param app 
 */
void block_button_setup(ezgl::application* app) {
    t_draw_state* draw_state = get_draw_state_vars();

    //Toggle block internals
    GtkSpinButton* blk_internals_button = GTK_SPIN_BUTTON(app->get_object("ToggleBlkInternals"));
    g_signal_connect(blk_internals_button, "value-changed", G_CALLBACK(toggle_blk_internal_cbk), app);
    gtk_spin_button_set_increments(blk_internals_button, 1, 1);
    gtk_spin_button_set_range(blk_internals_button, 0., (double)(draw_state->max_sub_blk_lvl - 1));

    //Toggle Block Pin Util
    GtkComboBoxText* blk_pin_util = GTK_COMBO_BOX_TEXT(app->get_object("ToggleBlkPinUtil"));
    g_signal_connect(blk_pin_util, "changed", G_CALLBACK(toggle_blk_pin_util_cbk), app);

    //Toggle Placement Macros
    GtkComboBoxText* placement_macros = GTK_COMBO_BOX_TEXT(app->get_object("TogglePlacementMacros"));
    g_signal_connect(placement_macros, "changed", G_CALLBACK(placement_macros_cbk), app);

    //Toggle NoC Display (based on startup cmd --noc on)
    if (!draw_state->show_noc_button) {
        hide_widget("NocLabel", app);
        hide_widget("ToggleNocBox", app);
    } else {
        GtkComboBoxText* toggleNocBox = GTK_COMBO_BOX_TEXT(app->get_object("ToggleNocBox"));
        g_signal_connect(toggleNocBox, "changed", G_CALLBACK(toggle_noc_cbk), app);
    }
}

/*
 * @brief configures and connects signals/functions for routing buttons
 * 
 * Connects signals/sets default values for toggleRRButton, ToggleCongestion,
 * ToggleCongestionCost, ToggleRoutingBBox, RoutingExpansionCost, ToggleRoutingUtil 
 * buttons. 
 */
void routing_button_setup(ezgl::application* app) {
    auto& route_ctx = g_vpr_ctx.routing();

    //Toggle RR
    GtkComboBoxText* toggle_rr_box = GTK_COMBO_BOX_TEXT(app->get_object("ToggleRR"));
    g_signal_connect(toggle_rr_box, "changed", G_CALLBACK(toggle_rr_cbk), app);

    //Toggle Congestion
    GtkComboBoxText* toggle_congestion = GTK_COMBO_BOX_TEXT(app->get_object("ToggleCongestion"));
    g_signal_connect(toggle_congestion, "changed", G_CALLBACK(toggle_cong_cbk), app);

    //Toggle Congestion Cost
    GtkComboBoxText* toggle_cong_cost = GTK_COMBO_BOX_TEXT(app->get_object("ToggleCongestionCost"));
    g_signal_connect(toggle_cong_cost, "changed", G_CALLBACK(toggle_cong_cost_cbk), app);

    //Toggle Routing BB
    GtkSpinButton* toggle_routing_bbox = GTK_SPIN_BUTTON(app->get_object("ToggleRoutingBBox"));
    g_signal_connect(toggle_routing_bbox, "value-changed", G_CALLBACK(toggle_routing_bbox_cbk), app);
    gtk_spin_button_set_increments(toggle_routing_bbox, 1, 1);
    gtk_spin_button_set_range(toggle_routing_bbox, -1., (double)(route_ctx.route_bb.size() - 1));
    gtk_spin_button_set_value(toggle_routing_bbox, -1.);

    //Toggle Routing Expansion Costs
    GtkComboBoxText* toggle_expansion_cost = GTK_COMBO_BOX_TEXT(app->get_object("ToggleRoutingExpansionCost"));
    g_signal_connect(toggle_expansion_cost, "changed", G_CALLBACK(toggle_expansion_cost_cbk), app);

    //Toggle Router Util
    GtkComboBoxText* toggle_router_util = GTK_COMBO_BOX_TEXT(app->get_object("ToggleRoutingUtil"));
    g_signal_connect(toggle_router_util, "changed", G_CALLBACK(toggle_router_util_cbk), app);
    show_widget("RoutingMenuButton", app);
}

/*
 * @brief configures and connects signals/functions for 3D buttons
 *
 * Determines how many layers there are and displays depending on number of layers
 */
void three_dimension_button_setup(ezgl::application* app) {
    int num_layers;

    auto& device_ctx = g_vpr_ctx.device();
    num_layers = device_ctx.grid.get_num_layers();

    // Hide the button if we only have one layer
    if (num_layers == 1) {
        hide_widget("3DMenuButton", app);
    } else {
        GtkPopover* popover = GTK_POPOVER(app->get_object("3Dpopover"));
        GtkBox* box = GTK_BOX(app->get_object("3Dbox"));

        // Create checkboxes for each layer
        for (int i = 0; i < num_layers; i++) {
            std::string label = "Layer " + std::to_string(i + 1);
            GtkWidget* checkbox = gtk_check_button_new_with_label(label.c_str());
            gtk_box_pack_start(GTK_BOX(box), checkbox, FALSE, FALSE, 0);

            if (i == 0) {
                // Set the initial state of the first checkbox to checked to represent the dafault view.
                gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbox), TRUE);
            }

            g_signal_connect(checkbox, "toggled", G_CALLBACK(three_dimension_layer_cbk), app);
        }
        gtk_widget_show_all(GTK_WIDGET(popover));
    }
}

/*
 * @brief Loads required data for search autocomplete, sets up special completion fn
 */
void search_setup(ezgl::application* app) {
    load_block_names(app);
    load_net_names(app);
    //Setting custom matching function for entry completion (searches whole string instead of start)
    GtkEntryCompletion* wildcardComp = GTK_ENTRY_COMPLETION(app->get_object("Completion"));
    gtk_entry_completion_set_match_func(wildcardComp, (GtkEntryCompletionMatchFunc)customMatchingFunction, NULL, NULL);
}

/*
 * @brief connects critical path button to its cbk fn
 * 
 * @param app ezgl application
 */
void crit_path_button_setup(ezgl::application* app) {
    GtkComboBoxText* toggle_crit_path = GTK_COMBO_BOX_TEXT(app->get_object("ToggleCritPath"));
    g_signal_connect(toggle_crit_path, "changed", G_CALLBACK(toggle_crit_path_cbk), app);
    show_widget("ToggleCritPath", app);
}

/*
 * @brief Hides or displays critical path routing / routing delay UI elements
 *
 * @param app ezgl app
 */
void hide_crit_path_routing(ezgl::application* app, bool hide) {
    GtkComboBoxText* toggle_crit_path = GTK_COMBO_BOX_TEXT(app->get_object("ToggleCritPath"));
    if (hide) {
        gtk_combo_box_text_remove(toggle_crit_path, 4);
        gtk_combo_box_text_remove(toggle_crit_path, 3);
    } else {
        gtk_combo_box_text_insert_text(toggle_crit_path, 3, "Crit Path Routing");
        gtk_combo_box_text_insert_text(toggle_crit_path, 4, "Crit Path Routing Delays");
    }
}
/*
 * @brief Hides the widget with the given name
 * 
 * @param widgetName string of widget name in main.ui
 * @param app ezgl app
 */
void hide_widget(std::string widgetName, ezgl::application* app) {
    GtkWidget* widget = GTK_WIDGET(app->get_object(widgetName.c_str()));
    gtk_widget_hide(widget);
}

/**
 * @brief Hides the widget with the given name
 */
void show_widget(std::string widgetName, ezgl::application* app) {
    GtkWidget* widget = GTK_WIDGET(app->get_object(widgetName.c_str()));
    gtk_widget_show(widget);
}

/**
 * @brief loads atom and cluster lvl names into gtk list store item used for completion
 * 
 * @param app ezgl application used for ui
 */
void load_block_names(ezgl::application* app) {
    auto blockStorage = GTK_LIST_STORE(app->get_object("BlockNames"));
    auto& cluster_ctx = g_vpr_ctx.clustering();
    auto& atom_ctx = g_vpr_ctx.atom();
    GtkTreeIter iter;
    int i = 0;
    for (ClusterBlockId id : cluster_ctx.clb_nlist.blocks()) {
        gtk_list_store_append(blockStorage, &iter);
        gtk_list_store_set(blockStorage, &iter,
                           0, (cluster_ctx.clb_nlist.block_name(id)).c_str(), -1);
        i++;
    }
    for (AtomBlockId id : atom_ctx.nlist.blocks()) {
        gtk_list_store_append(blockStorage, &iter);
        gtk_list_store_set(blockStorage, &iter,
                           0, (atom_ctx.nlist.block_name(id)).c_str(), -1);
        i++;
    }
}

/*
 * @brief loads atom net names into gtk list store item used for completion
 * 
 * @param app ezgl application used for ui
 */
void load_net_names(ezgl::application* app) {
    auto netStorage = GTK_LIST_STORE(app->get_object("NetNames"));
    auto& atom_ctx = g_vpr_ctx.atom();
    GtkTreeIter iter;
    //Loading net names
    int i = 0;
    for (AtomNetId id : atom_ctx.nlist.nets()) {
        gtk_list_store_append(netStorage, &iter);
        gtk_list_store_set(netStorage, &iter,
                           0, (atom_ctx.nlist.net_name(id)).c_str(), -1);
        i++;
    }
}

void three_dimension_layers(GtkWidget* widget, gint /*response_id*/, gpointer /*data*/) {
    t_draw_state* draw_state = get_draw_state_vars();

    GtkWidget* parent = gtk_widget_get_parent(widget);
    GtkBox* box = GTK_BOX(parent);

    GList* children = gtk_container_get_children(GTK_CONTAINER(box));
    int index = 0;
    // Iterate over the checkboxes
    for (GList* iter = children; iter != NULL; iter = g_list_next(iter)) {
        if (GTK_IS_CHECK_BUTTON(iter->data)) {
            GtkWidget* checkbox = GTK_WIDGET(iter->data);
            gboolean state = gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbox));

            // Change the the boolean of the draw_layer_display vector depending on checkbox
            if (state) {
                std::cout << "Layer " << index + 1 << " on" <<std::endl;
                draw_state->draw_layer_display[index].visible = true;

            } else {
                draw_state->draw_layer_display[index].visible = false;
                std::cout << "Layer " << index + 1 << " off" << std::endl;
            }
            index++;
        }
    }
    g_list_free(children);
    application.refresh_drawing();
}

#endif /* NO_GRAPHICS */
