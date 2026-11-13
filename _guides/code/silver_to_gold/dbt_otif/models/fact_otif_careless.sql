{# For the page: a careless join (every delivery row joined), to show WHEN dbt's tests run. #}
{{ config(materialized='table') }}
select l.line_id, l.dealer_id, l.promised_date, l.qty_ordered, d.qty as qty_delivered
from {{ ref('order_lines') }} l
left join {{ ref('deliveries') }} d on d.line_id = l.line_id
