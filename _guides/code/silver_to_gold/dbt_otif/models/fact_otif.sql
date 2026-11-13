{# WRITER: dbt replaces every promised_date present in this run's output (delete, then insert). #}
{{ config(materialized='incremental', incremental_strategy='delete+insert', unique_key='promised_date') }}

-- READER 1: which windows changed? dbt keeps no bookmark of its own, so the bookmark is stored
-- in the fact itself (_lines_seq, _dels_seq) and read back with max().
with changed_windows as (
    select promised_date from {{ ref('order_lines') }}
    {% if is_incremental() %} where _seq > (select max(_lines_seq) from {{ this }}) {% endif %}
    union
    select l.promised_date
    from {{ ref('deliveries') }} d join {{ ref('order_lines') }} l on l.line_id = d.line_id
    {% if is_incremental() %} where d._seq > (select max(_dels_seq) from {{ this }}) {% endif %}
    {% if is_incremental() %}
    union   -- windows still waiting: an unknown dealer, or a missing warehouse file
    select promised_date from {{ this }} where dealer_key = -1 or not _is_complete
    {% endif %}
),

-- READER 2: every row of those windows, then the declared filter
order_lines_in as (
    select * from {{ ref('order_lines') }}
    where promised_date in (select promised_date from changed_windows)
      and dealer_id not in ('TEST01')
),
deliveries_in as (
    select d.* from {{ ref('deliveries') }} d
    where d.line_id in (select line_id from order_lines_in)
),

-- PROCESSOR
built as ( {{ otif_rule('order_lines_in', 'deliveries_in') }} ),

-- keys as of the event date; a missing dealer gets -1
keyed as (
    select b.*, coalesce(d.dealer_key, -1) as dealer_key
    from built b
    left join {{ ref('dim_dealer') }} d
      on d.dealer_id = b.dealer_id and b.promised_date >= d.valid_from and b.promised_date < d.valid_to
),

-- completeness: both warehouses have sent their file for the day
complete as (
    select file_date, count(distinct warehouse) = 2 as ok
    from {{ ref('delivery_files') }} group by file_date
)

select k.*, coalesce(c.ok, false) as _is_complete,
       (select max(_seq) from {{ ref('order_lines') }}) as _lines_seq,
       (select max(_seq) from {{ ref('deliveries') }})  as _dels_seq
from keyed k
left join complete c on c.file_date = k.promised_date
