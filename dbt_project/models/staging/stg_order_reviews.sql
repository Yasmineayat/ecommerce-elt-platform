select
    review_id,
    order_id,
    review_score::int                                   as review_score,
    review_comment_title,
    review_comment_message,
    nullif(review_creation_date, '')::timestamp         as review_created_at,
    nullif(review_answer_timestamp, '')::timestamp      as review_answered_at
from {{ source('olist', 'order_reviews') }}