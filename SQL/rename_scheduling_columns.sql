-- Rename columns in scheduling table
ALTER TABLE "scheduling"
RENAME COLUMN "PickUpLocation" TO "store_id",
RENAME COLUMN "deliveryLocation" TO "order_id";

-- Update foreign key constraints
ALTER TABLE "scheduling" 
DROP CONSTRAINT "fk_scheduling_PickUpLocation_Store",
DROP CONSTRAINT "fk_scheduling_deliveryLocation_Order",
ADD CONSTRAINT "fk_scheduling_store_id_Store" 
    FOREIGN KEY ("store_id") 
    REFERENCES "Store"("store_id")
    ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT "fk_scheduling_order_id_Order" 
    FOREIGN KEY ("order_id") 
    REFERENCES "Order"("Order_ID")
    ON DELETE CASCADE ON UPDATE CASCADE; 