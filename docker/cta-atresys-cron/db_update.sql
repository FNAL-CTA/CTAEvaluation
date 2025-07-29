-- This is to track objects scanned for repack
-- This file is here for documentation purposes only.
-- It is not executed by the application.
CREATE TABLE IF NOT EXISTS scanned_for_repack (
    id SERIAL PRIMARY KEY,
    vid VARCHAR(100) REFERENCES tape(vid) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'Marked for review',
    created NUMERIC(20, 0) NOT NULL,
    updated NUMERIC(20, 0) NOT NULL
);

-- Add an index on vid separately
CREATE INDEX IF NOT EXISTS idx_scanned_for_repack_vid ON scanned_for_repack(vid);

-- Uncomment to delete the table if needed
-- DROP TABLE IF EXISTS scanned_for_repack;
