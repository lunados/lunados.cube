/*
 * MILE-002 C4-01..03 — synthetic Structurizr DSL model (authored 2026-11-01).
 * Not a client or production system. Not executed with Structurizr tooling;
 * the implied-relationship outcome is derived from sources S-SZ-1 and S-SZ-3.
 */
workspace "MILE-002 C4 sample" "Synthetic model for grammar sampling" {

    !impliedRelationships true

    model {
        shop = softwareSystem "Shop" {
            api = container "API" {
                orderController = component "Order Controller"
                orderRepository = component "Order Repository"
            }
            db = container "Database"
        }

        orderController -> orderRepository "Delegates persistence to"
        orderController -> db "Writes orders to"
        orderRepository -> db "Reads orders from"
    }
}
