-- PROCESSOR in SQL: the OTIF rule. The harness registers two views, already limited to the windows
-- being rebuilt: order_lines (after the declared filters) and deliveries. Pure: reads only those views.
WITH per_line AS (            -- one row per line FIRST, so the join below can never multiply lines
  SELECT line_id,
         SUM(qty)            AS qty_delivered,
         MAX(delivered_date) AS last_delivered
  FROM deliveries
  GROUP BY line_id
),
flags AS (
  SELECT l.line_id, l.dealer_id, l.promised_date, l.qty_ordered,
         COALESCE(p.qty_delivered, 0)                                         AS qty_delivered,
         CASE WHEN p.last_delivered <= l.promised_date THEN 1 ELSE 0 END      AS on_time,
         CASE WHEN COALESCE(p.qty_delivered, 0) >= l.qty_ordered THEN 1 ELSE 0 END AS in_full
  FROM order_lines l
  LEFT JOIN per_line p ON p.line_id = l.line_id
)
SELECT line_id, dealer_id, promised_date, qty_ordered, qty_delivered, on_time, in_full,
       on_time * in_full AS otif
FROM flags
