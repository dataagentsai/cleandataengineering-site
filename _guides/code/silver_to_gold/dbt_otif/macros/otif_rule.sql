{# PROCESSOR: the OTIF rule, the same SQL as fact_otif.sql, as a macro that takes its two inputs. #}
{% macro otif_rule(order_lines, deliveries) %}
  with per_line as (            -- one row per line FIRST, so the join can never multiply lines
    select line_id, sum(qty) as qty_delivered, max(delivered_date) as last_delivered
    from {{ deliveries }}
    group by line_id
  ),
  flags as (
    select l.line_id, l.dealer_id, l.promised_date, l.qty_ordered,
           coalesce(p.qty_delivered, 0)                                              as qty_delivered,
           case when p.last_delivered <= l.promised_date then 1 else 0 end           as on_time,
           case when coalesce(p.qty_delivered, 0) >= l.qty_ordered then 1 else 0 end as in_full
    from {{ order_lines }} l
    left join per_line p on p.line_id = l.line_id
  )
  select line_id, dealer_id, promised_date, qty_ordered, qty_delivered, on_time, in_full,
         on_time * in_full as otif
  from flags
{% endmacro %}
