-- Add actual location columns to scheduling table
ALTER TABLE "scheduling"
ADD COLUMN "actual_pickup_location" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN "actual_delivery_location" INTEGER NOT NULL DEFAULT 0;

-- Update existing records to use the same values as their foreign keys (if any exist)
UPDATE "scheduling"
SET 
    "actual_pickup_location" = (
        SELECT "pickup_location" 
        FROM "Store" 
        WHERE "store_id" = "scheduling"."PickUpLocation"
    ),
    "actual_delivery_location" = (
        SELECT "deliveryLocation" 
        FROM "Order" 
        WHERE "Order_ID" = "scheduling"."deliveryLocation"
    );

-- After data is migrated, remove the default values
ALTER TABLE "scheduling"
ALTER COLUMN "actual_pickup_location" DROP DEFAULT,
ALTER COLUMN "actual_delivery_location" DROP DEFAULT; 